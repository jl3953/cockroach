package sql

import (
	"context"
	"fmt"

	"github.com/cockroachdb/cockroach/pkg/keys"
	"github.com/cockroachdb/cockroach/pkg/kv"
	"github.com/cockroachdb/cockroach/pkg/roachpb"
	"github.com/cockroachdb/cockroach/pkg/sql/privilege"
	"github.com/cockroachdb/cockroach/pkg/sql/sem/tree"
	"github.com/cockroachdb/cockroach/pkg/sql/sem/types"
	"github.com/cockroachdb/cockroach/pkg/sql/sqlbase"
	"github.com/cockroachdb/cockroach/pkg/storage/storagebase"
	"github.com/pkg/errors"
)

type hotKeyNode struct {
	optColumnsSlot

	tableDesc *sqlbase.TableDescriptor
	index     *sqlbase.IndexDescriptor
	rows      planNode
	run       hotKeyRun
}

// hotKeyRun contains the run-time state of hotKeyNode during local execution.
type hotKeyRun struct {
	lastHotKey []byte
}

// HotKey sets selected keys to be redirected to the hot shard.
// Privileges: INSERT on table.
func (p *planner) HotKey(ctx context.Context, n *tree.HotKey) (planNode, error) {
	tableDesc, index, err := p.getTableAndIndex(ctx, n.Table, n.Index, privilege.INSERT)
	if err != nil {
		return nil, err
	}

	// Calculate the desired types for the select statement. It is OK if the
	// select statement returns fewer columns (the relevant prefix is used).
	desiredTypes := make([]types.T, len(index.ColumnIDs))
	for i, colID := range index.ColumnIDs {
		c, err := tableDesc.FindColumnByID(colID)
		if err != nil {
			return nil, err
		}
		desiredTypes[i] = c.Type.ToDatumType()
	}

	// Create the plan for the split rows source.
	rows, err := p.newPlan(ctx, n.Rows, desiredTypes)
	if err != nil {
		return nil, err
	}

	cols := planColumns(rows)
	if len(cols) == 0 {
		return nil, errors.Errorf("no columns in HOTKEY AT data")
	}
	if len(cols) > len(index.ColumnIDs) {
		return nil, errors.Errorf("too many columns in HOTKEY AT data")
	}
	for i := range cols {
		if !cols[i].Typ.Equivalent(desiredTypes[i]) {
			return nil, errors.Errorf(
				"HOTKEY AT data column %d (%s) must be of type %s, not type %s",
				i+1, index.ColumnNames[i], desiredTypes[i], cols[i].Typ,
			)
		}
	}

	return &hotKeyNode{
		tableDesc: tableDesc.TableDesc(),
		index:     index,
		rows:      rows,
	}, nil
}

var hotKeyNodeColumns = sqlbase.ResultColumns{
	{
		Name: "key",
		Typ:  types.Bytes,
	},
	{
		Name: "pretty",
		Typ:  types.String,
	},
}

func (n *hotKeyNode) startExec(params runParams) error {
	// This check is not intended to be foolproof. The setting could be outdated
	// because of gossip inconsistency, or it could change halfway through the
	// SPLIT AT's execution. It is, however, likely to prevent user error and
	// confusion in the common case.
	if storagebase.MergeQueueEnabled.Get(&params.p.ExecCfg().Settings.SV) {
		return errors.New("hot keys would be immediately discarded by merge queue; " +
			"disable the merge queue first by running 'SET CLUSTER SETTING kv.range_merge.queue_enabled = false'")
	}
	return nil
}

func (n *hotKeyNode) Next(params runParams) (bool, error) {
	// TODO(radu): instead of performing the splits sequentially, accumulate all
	// the split keys and then perform the splits in parallel (e.g. split at the
	// middle key and recursively to the left and right).

	if ok, err := n.rows.Next(params); err != nil || !ok {
		return ok, err
	}

	rowKey, err := getRowKey(n.tableDesc, n.index, n.rows.Values())
	if err != nil {
		return false, err
	}

	// Create splits before and after key to isolate it
	k := roachpb.Key(rowKey)
	fmt.Println("Creating split at key: ", k)
	if err := params.extendedEvalCtx.ExecCfg.DB.AdminSplit(params.ctx, rowKey, rowKey); err != nil {
		return false, err
	}

	nextKey := k.PrefixEnd()
	fmt.Println("Creating split at key: ", nextKey)
	if err := params.extendedEvalCtx.ExecCfg.DB.AdminSplit(params.ctx, nextKey, nextKey); err != nil {
		return false, err
	}

	nts := params.extendedEvalCtx.ExecCfg.DB.GetFactory().NonTransactionalSender()
	switch t := nts.(type) {
	case *kv.DistSender:
		ds := nts.(*kv.DistSender)
		fmt.Println("Adding hot key: ", k)
		if err := ds.AddHotKey(k); err != nil {
			return false, err
		}
	default:
		fmt.Println("Got unknown sender type: %T", t)
	}

	n.run.lastHotKey = rowKey

	return true, nil
}

func (n *hotKeyNode) Values() tree.Datums {
	return tree.Datums{
		tree.NewDBytes(tree.DBytes(n.run.lastHotKey)),
		tree.NewDString(keys.PrettyPrint(nil /* valDirs */, n.run.lastHotKey)),
	}
}

func (n *hotKeyNode) Close(ctx context.Context) {
	n.rows.Close(ctx)
}
