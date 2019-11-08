package main

import (
		"fmt"
		"math/rand"
		"sort"
		"os"
		"github.com/cockroachdb/cockroach/pkg/util/timeutil"
	   )

func generate_filename(prepend string, s float64) string {
	return prepend + fmt.Sprintf("%.1f", s) + ".csv"
}

func main() {

	accesses := 10000
	max := uint64(1000000)
	//skews := []float64{0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 1.1, 1.2}
	skews := []float64{2.0}

	for _, s := range skews {
		random := rand.New(rand.NewSource(timeutil.Now().UnixNano()))
		zipf, _ := NewZipfGenerator(random, 0, max, s, false)

		hist := make(map[int]int)
		for i := 0; i < accesses; i++ {
			var key int = int(zipf.Uint64())
			if val, ok := hist[key]; ok {
				hist[key] = val + 1
			} else {
				hist[key] = 1
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
		cdf, _ := os.Create(generate_filename("cdf", s))
		cdf.WriteString("key\tfrequency\n")
		for _, k := range keys {
			cum += hist[k]
			frequency := float64(hist[k])/float64(accesses)
			if frequency >= 0 {
				pdf.WriteString(fmt.Sprintf("%d", k) + "\t" + fmt.Sprintf("%f", frequency) + "\n")
			}
			cdf.WriteString(fmt.Sprintf("%d", k) + "\t" + fmt.Sprintf("%f", float64(cum)/float64(accesses)) + "\n")
		}
		cdf.Close()
		pdf.Close()
	}
}

