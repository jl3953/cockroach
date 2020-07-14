package main

import (
		"fmt"
		"math/rand"
		"sort"
		"strconv"
		"os"
		"github.com/cockroachdb/cockroach/pkg/util/timeutil"
	   )

func generate_filename(prepend string, s float64) string {
	return prepend + fmt.Sprintf("%.1f", s) + ".csv"
}

type Set struct {
	vals []int
	i	int
}

func (set *Set) Add(val int) bool {

	for i := 0; i < len(set.vals); i++ {
		if set.vals[i] == val {
			return false
		}
	}

	set.vals = append(set.vals, val)
	return true
}

func NewSet() *Set {
	return &Set{make([]int, 0), 0}
}


func main() {

	accesses := 10000
	max_int, _ := strconv.ParseInt(os.Args[1], 10, 64)
	max := uint64(max_int)
	skews := []float64{0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 1.1, 1.2, 1.3, 1.4, 1.5}

	for _, s := range skews {
		random := rand.New(rand.NewSource(timeutil.Now().UnixNano()))
		zipf, _ := NewZipfGenerator(random, 0, max, s, false)

		hist := make(map[int]int)
		total_accesses := 0
		for i := 0; i < accesses; i++ {

			set := NewSet()
			for k := 0; k < 1; k++ {
				ok := false
				for !ok {
					ok = set.Add(int(zipf.Uint64()))
				}
			}

			for _, key := range set.vals {
				total_accesses += 1
				if val, ok := hist[key]; ok {
					hist[key] = val + 1
				} else {
					hist[key] = 1
				}
			}
		}

		keys := make([]int, 0)
		for k, _ := range hist {
			keys = append(keys, k)
		}
		sort.Ints(keys)
		cum := 0
		pdf,_ := os.Create(generate_filename("pdf", s))
		pdf.WriteString("key\tfrequency\n")
		cdf, _ := os.Create(generate_filename(os.Args[2], s))
		cdf.WriteString("key\tfrequency\n")
		for _, k := range keys {
			cum += hist[k]
			// frequency := float64(hist[k])/float64(total_accesses)
			// if frequency >= 0 {
			// 	pdf.WriteString(fmt.Sprintf("%d", k) + "\t" + fmt.Sprintf("%f", frequency) + "\n")
			// }
			cdf.WriteString(fmt.Sprintf("%d", k) + "\t" + fmt.Sprintf("%f", float64(cum)/float64(total_accesses)) + "\n")
		}
		cdf.Close()
		pdf.Close()
	}
}

