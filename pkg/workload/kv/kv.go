// Copyright 2017 The Cockroach Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
// implied. See the License for the specific language governing
// permissions and limitations under the License. See the AUTHORS file
// for names of contributors.

package kv

import (
	"context"
	"crypto/sha1"
	"database/sql"
	"encoding/binary"
	"fmt"
	"hash"
	"math"
	"math/rand"
	"strconv"
	"strings"
	"sync/atomic"

	"github.com/cockroachdb/cockroach-go/crdb"
	"github.com/cockroachdb/cockroach/pkg/util/timeutil"
	"github.com/cockroachdb/cockroach/pkg/workload"
	"github.com/cockroachdb/cockroach/pkg/workload/histogram"
	"github.com/pkg/errors"
	"github.com/spf13/pflag"
	//"github.com/jackc/pgx"
)

const (
	kvSchema = `(
		k BIGINT NOT NULL PRIMARY KEY,
		v BYTES NOT NULL
	)`
	kvSchemaWithIndex = `(
		k BIGINT NOT NULL PRIMARY KEY,
		v BYTES NOT NULL,
		INDEX (v)
	)`
)

type kv struct {
	flags     workload.Flags
	connFlags *workload.ConnFlags

	batchSize                            int
	minBlockSizeBytes, maxBlockSizeBytes int
	cycleLength                          int64
	readPercent                          int
	spanPercent                          int
	seed                                 int64
	writeSeq                             string
	sequential                           bool
	zipfian                              bool
	splits                               int
	secondaryIndex                       bool
	useOpt                               bool
	targetCompressionRatio               float64
	stmtPerTxn                           int
	skew                                 float64
	hotKeys                              []int64
}

func init() {
	workload.Register(kvMeta)
}

var kvMeta = workload.Meta{
	Name:        `kv`,
	Description: `KV reads and writes to keys spread randomly across the cluster.`,
	Details: `
	By default, keys are picked uniformly at random across the cluster.
	--concurrency workers alternate between doing selects and upserts (according
	to a --read-percent ratio). Each select/upsert reads/writes a batch of --batch
	rows. The write keys are randomly generated in a deterministic fashion (or
	sequentially if --sequential is specified). Reads select a random batch of ids
	out of the ones previously written.
	--write-seq can be used to incorporate data produced by a previous run into
	the current run.
	`,
	Version:      `1.0.0`,
	PublicFacing: true,
	New: func() workload.Generator {
		g := &kv{}
		g.flags.FlagSet = pflag.NewFlagSet(`kv`, pflag.ContinueOnError)
		g.flags.Meta = map[string]workload.FlagMeta{
			`batch`: {RuntimeOnly: true},
		}
		g.flags.IntVar(&g.batchSize, `batch`, 1,
			`Number of blocks to read/insert in a single SQL statement.`)
		g.flags.IntVar(&g.minBlockSizeBytes, `min-block-bytes`, 1,
			`Minimum amount of raw data written with each insertion.`)
		g.flags.IntVar(&g.maxBlockSizeBytes, `max-block-bytes`, 1,
			`Maximum amount of raw data written with each insertion`)
		g.flags.Int64Var(&g.cycleLength, `cycle-length`, math.MaxInt64,
			`Number of keys repeatedly accessed by each writer through upserts.`)
		g.flags.IntVar(&g.readPercent, `read-percent`, 0,
			`Percent (0-100) of operations that are reads of existing keys.`)
		g.flags.IntVar(&g.spanPercent, `span-percent`, 0,
			`Percent (0-100) of operations that are spanning queries of all ranges.`)
		g.flags.Int64Var(&g.seed, `seed`, 1, `Key hash seed.`)
		g.flags.BoolVar(&g.zipfian, `zipfian`, false,
			`Pick keys in a zipfian distribution instead of randomly.`)
		g.flags.BoolVar(&g.sequential, `sequential`, false,
			`Pick keys sequentially instead of randomly.`)
		g.flags.StringVar(&g.writeSeq, `write-seq`, "",
			`Initial write sequence value. Can be used to use the data produced by a previous run. `+
				`It has to be of the form (R|S)<number>, where S implies that it was taken from a `+
				`previous --sequential run and R implies a previous random run.`)
		g.flags.IntVar(&g.splits, `splits`, 0,
			`Number of splits to perform before starting normal operations.`)
		g.flags.BoolVar(&g.secondaryIndex, `secondary-index`, false,
			`Add a secondary index to the schema`)
		g.flags.BoolVar(&g.useOpt, `use-opt`, true, `Use cost-based optimizer`)
		g.flags.Float64Var(&g.targetCompressionRatio, `target-compression-ratio`, 1.0,
			`Target compression ratio for data blocks. Must be >= 1.0`)
		g.flags.IntVar(&g.stmtPerTxn, `stmt-per-txn`, 10,
			`Statements per transaction to execute. Default=10`)
		g.flags.Float64Var(&g.skew, `skew`, 1.1,
			`Skew for zipfian distribution. Default=1.1`)
		g.flags.Int64SliceVar(&g.hotKeys, `hot-keys`, nil,
			`List of hot keys that will be store on hot shard`)
		g.connFlags = workload.NewConnFlags(&g.flags)
		return g
	},
}

// Meta implements the Generator interface.
func (*kv) Meta() workload.Meta { return kvMeta }

// Flags implements the Flagser interface.
func (w *kv) Flags() workload.Flags { return w.flags }

// Hooks implements the Hookser interface.
func (w *kv) Hooks() workload.Hooks {
	return workload.Hooks{
		Validate: func() error {
			if w.maxBlockSizeBytes < w.minBlockSizeBytes {
				return errors.Errorf("Value of 'max-block-bytes' (%d) must be greater than or equal to value of 'min-block-bytes' (%d)",
					w.maxBlockSizeBytes, w.minBlockSizeBytes)
			}
			if w.sequential && w.splits > 0 {
				return errors.New("'sequential' and 'splits' cannot both be enabled")
			}
			if w.sequential && w.zipfian {
				return errors.New("'sequential' and 'zipfian' cannot both be enabled")
			}
			if w.readPercent+w.spanPercent > 100 {
				return errors.New("'read-percent' and 'span-percent' higher than 100")
			}
			if w.targetCompressionRatio < 1.0 || math.IsNaN(w.targetCompressionRatio) {
				return errors.New("'target-compression-ratio' must be a number >= 1.0")
			}
			if w.splits > 0 && len(w.hotKeys) > 0 {
				return errors.New("Can only specify one of `splits` or `hot-keys`")
			}
			return nil
		},
	}
}

// Tables implements the Generator interface.
func (w *kv) Tables() []workload.Table {
	var nsplits int
	if w.splits > 0 {
		nsplits = w.splits
	} else {
		nsplits = 2 * len(w.hotKeys)
	}

	table := workload.Table{
		Name: `kv`,
		// TODO(dan): Support initializing kv with data.
		Splits: workload.Tuples(
			nsplits,
			func(splitIdx int) []interface{} {
				var splitPoint int
				if w.splits > 0 {
					stride := (float64(w.cycleLength) - float64(math.MinInt64)) / float64(nsplits+1)
					splitPoint = int(math.MinInt64 + float64(splitIdx+1)*stride)
				} else {
					hotKeyIdx := splitIdx / 2
					plusZeroOrOne := splitIdx % 2
					splitPoint = int(w.hotKeys[hotKeyIdx] + int64(plusZeroOrOne))
				}

				return []interface{}{splitPoint}

			},
		),
	}
	if w.secondaryIndex {
		table.Schema = kvSchemaWithIndex
	} else {
		table.Schema = kvSchema
	}
	return []workload.Table{table}
}

// Ops implements the Opser interface.
func (w *kv) Ops(urls []string, reg *histogram.Registry) (workload.QueryLoad, error) {
	writeSeq := 0
	if w.writeSeq != "" {
		first := w.writeSeq[0]
		if len(w.writeSeq) < 2 || (first != 'R' && first != 'S') {
			return workload.QueryLoad{}, fmt.Errorf("--write-seq has to be of the form '(R|S)<num>'")
		}
		rest := w.writeSeq[1:]
		var err error
		writeSeq, err = strconv.Atoi(rest)
		if err != nil {
			return workload.QueryLoad{}, fmt.Errorf("--write-seq has to be of the form '(R|S)<num>'")
		}
		if first == 'R' && w.sequential {
			return workload.QueryLoad{}, fmt.Errorf("--sequential incompatible with a Random --write-seq")
		}
		if first == 'S' && !w.sequential {
			return workload.QueryLoad{}, fmt.Errorf(
				"--sequential=false incompatible with a Sequential --write-seq")
		}
	}

	// sanitize your urls
	//ctx := context.Background()
	sqlDatabase, err := workload.SanitizeUrls(w, w.connFlags.DBOverride, urls)
	if err != nil {
		return workload.QueryLoad{}, err
	}

	// open db connections
	db, err := sql.Open(`cockroach`, strings.Join(urls, ` `))
	if err != nil {
		return workload.QueryLoad{}, err
	}
	// Allow a maximum of concurrency+1 connections to the database.
	db.SetMaxOpenConns(w.connFlags.Concurrency + 1)
	db.SetMaxIdleConns(w.connFlags.Concurrency + 1)

	// figuring out workload stuff
	ql := workload.QueryLoad{SQLDatabase: sqlDatabase}
	seq := &sequence{config: w, val: int64(writeSeq)}
	numEmptyResults := new(int64)
	//fmt.Printf("concurrency %d\n", w.connFlags.Concurrency)
	for i := 0; i < w.connFlags.Concurrency; i++ {
		op := &kvOp{
			config:          w,
			hists:           reg.GetHandle(),
			numEmptyResults: numEmptyResults,
			//mcp:             mcp,
			db: db,
		}
		if w.sequential {
			op.g = newSequentialGenerator(seq)
		} else if w.zipfian {
			op.g = newZipfianGenerator(seq, w.skew)
		} else {
			op.g = newHashGenerator(seq)
		}
		ql.WorkerFns = append(ql.WorkerFns, op.run)
		ql.Close = op.close
	}
	return ql, nil
}

type kvOp struct {
	config          *kv
	hists           *histogram.Histograms
	sr              workload.SQLRunner
	readStmt        workload.StmtHandle
	writeStmt       workload.StmtHandle
	rollbackStmt    workload.StmtHandle
	spanStmt        workload.StmtHandle
	g               keyGenerator
	numEmptyResults *int64 // accessed atomically
	mcp             *workload.MultiConnPool
	db              *sql.DB
}

func (o *kvOp) run(ctx context.Context) error {
	statementProbability := o.g.rand().Intn(100) // Determines what statement is executed.
	STATEMENTS_PER_TXN := o.config.stmtPerTxn
	rando := rand.Intn(1000)

	// transaction TODO(jenn) PROBABLY FATAL--follows default
	// of db
	if statementProbability < o.config.readPercent {
		start := timeutil.Now()

		if err := crdb.ExecuteTx(ctx,
			o.db,
			&sql.TxOptions{
				//Isolation: sql.LevelLinearizable,
				ReadOnly: true,
			}, func(tx *sql.Tx) error {

				for i := 0; i < STATEMENTS_PER_TXN; i++ {

					// construct query
					args := make([]interface{}, o.config.batchSize)
					stmt := "SELECT k from kv WHERE k IN ("
					for batch := 0; batch < o.config.batchSize; batch++ {
						if batch > 0 {
							stmt += ", "
						}
						stmt += "%d"
						args[batch] = o.g.readKey()
					}
					stmt += ")"
					stmt = fmt.Sprintf(stmt, args...)
					//log.Warningf(ctx, "jenndebug ro txn %s\n", stmt)
					//fmt.Println(stmt)
					rows, err := tx.Query(stmt)
					if err != nil {
						return err
					}
					for rows.Next() {
						var temp int
						if err := rows.Scan(&temp); err != nil {
							errors.Wrap(err, "row iteration %v\n")
							rows.Close()
							return err
						}
					}
					rows.Close()
				}

				return nil

			}); err != nil {
			fmt.Printf("reads suck\n")
			return err
		}

		elapsed := timeutil.Since(start)
		o.hists.Get(`read`).Record(elapsed)
		return nil
	}
	// Since we know the statement is not a read, we recalibrate
	// statementProbability to only consider the other statements.
	// TODO(jenn) this portion is useless, delete from code
	statementProbability -= o.config.readPercent
	if statementProbability < o.config.spanPercent {
		start := timeutil.Now()
		_, err := o.spanStmt.Exec(ctx)
		elapsed := timeutil.Since(start)
		o.hists.Get(`span`).Record(elapsed)
		return err
	}

	start := timeutil.Now()

	// writes
	if err := crdb.ExecuteTx(ctx,
		o.db,
		&sql.TxOptions{
			//Isolation: sql.LevelLinearizable,
			ReadOnly: false,
		}, func(tx *sql.Tx) error {
			for i := 0; i < STATEMENTS_PER_TXN; i++ {
				args := make([]interface{}, 0)
				hotArgs := make([]interface{}, 0)
				stmt := "UPSERT INTO kv (k, v) VALUES "
				hotStmt := stmt
				hotBatch := 0
				b := 0
				for batch := 0; batch < o.config.batchSize; batch++ {
					key := o.g.writeKey()
					if key >= 0 && key <= 5 { // probably a hotkey
						if hotBatch > 0 {
							hotStmt += ", "
						}
						hotStmt += "(%d, 'JennTheLamHotKey')"
						hotArgs = append(hotArgs, key)
						hotBatch += 1
					} else {
						if b > 0 {
							stmt += ", "
						}
						stmt += "(%d, 'JennTheLam')"
						args = append(args, key)
						b += 1
					}
				}
				stmt = fmt.Sprintf(stmt, args...)
				//log.Warningf(ctx, "jenndebug wo txn %s\n", stmt)
				//fmt.Println(stmt)
				if _, err := tx.Exec(stmt); err != nil {
					errors.Wrap(err, "aw shucks query:\n")
					return err
				}
				hotStmt = fmt.Sprintf(hotStmt, hotArgs...)
				if _, err := tx.Exec(stmt); err != nil {
					errors.Wrap(err, "hotkeys failed jennjenn\n")
					return err
				}
			}
			return nil
		}); err != nil {
		fmt.Printf("%d writes returned err\n", rando)
		return err
	}

	elapsed := timeutil.Since(start)
	o.hists.Get(`write`).Record(elapsed)
	return nil
}

func (o *kvOp) close(context.Context) {
	if empty := atomic.LoadInt64(o.numEmptyResults); empty != 0 {
		fmt.Printf("Number of reads that didn't return any results: %d.\n", empty)
	}
	seq := o.g.sequence()
	var ch string
	if o.config.sequential {
		ch = "S"
	} else {
		ch = "R"
	}
	fmt.Printf("Highest sequence written: %d. Can be passed as --write-seq=%s%d to the next run.\n",
		seq, ch, seq)
}

type sequence struct {
	config *kv
	val    int64
}

func (s *sequence) write() int64 {
	return (atomic.AddInt64(&s.val, 1) - 1) % s.config.cycleLength
}

// read returns the last key index that has been written. Note that the returned
// index might not actually have been written yet, so a read operation cannot
// require that the key is present.
func (s *sequence) read() int64 {
	return atomic.LoadInt64(&s.val) % s.config.cycleLength
}

// keyGenerator generates read and write keys. Read keys may not yet exist and
// write keys may already exist.
type keyGenerator interface {
	writeKey() int64
	readKey() int64
	rand() *rand.Rand
	sequence() int64
}

type hashGenerator struct {
	seq    *sequence
	random *rand.Rand
	hasher hash.Hash
	buf    [sha1.Size]byte
}

func newHashGenerator(seq *sequence) *hashGenerator {
	return &hashGenerator{
		seq:    seq,
		random: rand.New(rand.NewSource(timeutil.Now().UnixNano())),
		hasher: sha1.New(),
	}
}

func (g *hashGenerator) hash(v int64) int64 {
	binary.BigEndian.PutUint64(g.buf[:8], uint64(v))
	binary.BigEndian.PutUint64(g.buf[8:16], uint64(g.seq.config.seed))
	g.hasher.Reset()
	_, _ = g.hasher.Write(g.buf[:16])
	g.hasher.Sum(g.buf[:0])
	return int64(binary.BigEndian.Uint64(g.buf[:8]))
}

func (g *hashGenerator) writeKey() int64 {
	return g.hash(g.seq.write())
}

func (g *hashGenerator) readKey() int64 {
	v := g.seq.read()
	if v == 0 {
		return 0
	}
	return g.hash(g.random.Int63n(v))
}

func (g *hashGenerator) rand() *rand.Rand {
	return g.random
}

func (g *hashGenerator) sequence() int64 {
	return atomic.LoadInt64(&g.seq.val)
}

type sequentialGenerator struct {
	seq    *sequence
	random *rand.Rand
}

func newSequentialGenerator(seq *sequence) *sequentialGenerator {
	return &sequentialGenerator{
		seq:    seq,
		random: rand.New(rand.NewSource(timeutil.Now().UnixNano())),
	}
}

func (g *sequentialGenerator) writeKey() int64 {
	return g.seq.write()
}

func (g *sequentialGenerator) readKey() int64 {
	v := g.seq.read()
	if v == 0 {
		return 0
	}
	return g.random.Int63n(v)
}

func (g *sequentialGenerator) rand() *rand.Rand {
	return g.random
}

func (g *sequentialGenerator) sequence() int64 {
	return atomic.LoadInt64(&g.seq.val)
}

type zipfGenerator struct {
	seq    *sequence
	random *rand.Rand
	zipf   *zipf
}

// Creates a new zipfian generator.
func newZipfianGenerator(seq *sequence, skew float64) *zipfGenerator {
	random := rand.New(rand.NewSource(timeutil.Now().UnixNano()))
	return &zipfGenerator{
		seq:    seq,
		random: random,
		zipf:   newZipf(skew, 1, uint64(math.MaxInt64)),
	}
}

// Get a random number seeded by v that follows the
// zipfian distribution.
func (g *zipfGenerator) zipfian(seed int64) int64 {
	randomWithSeed := rand.New(rand.NewSource(seed))
	return int64(g.zipf.Uint64(randomWithSeed))
}

// Get a zipf write key appropriately.
func (g *zipfGenerator) writeKey() int64 {
	return g.zipfian(g.seq.write())
}

// Get a zipf read key appropriately.
func (g *zipfGenerator) readKey() int64 {
	v := g.seq.read()
	if v == 0 {
		return 0
	}
	return g.zipfian(g.random.Int63n(v))
}

func (g *zipfGenerator) rand() *rand.Rand {
	return g.random
}

func (g *zipfGenerator) sequence() int64 {
	return atomic.LoadInt64(&g.seq.val)
}

func randomBlock(config *kv, r *rand.Rand) []byte {
	blockSize := r.Intn(config.maxBlockSizeBytes-config.minBlockSizeBytes+1) + config.minBlockSizeBytes
	blockData := make([]byte, blockSize)
	uniqueSize := int(float64(blockSize) / config.targetCompressionRatio)
	if uniqueSize < 1 {
		uniqueSize = 1
	}
	for i := range blockData {
		if i >= uniqueSize {
			blockData[i] = blockData[i-uniqueSize]
		} else {
			blockData[i] = byte(r.Int() & 0xff)
		}
	}
	return blockData
}
