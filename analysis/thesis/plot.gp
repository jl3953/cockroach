set terminal png

set xlabel "zipfian constant (s)"
set ylabel "throughput (txns/sec)"

set yrange [0: 210000]
set title "Mocked protocol comparison, keyspace=1M"
set output "protocol_comparison_1M.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint,\
		 "hot1_1M.csv" using "skew":"median" title "hotkey subset: 1e-6%" with linespoint,\
		 "hot10_1M.csv" using "skew":"median" title "hotkey subset: 1e-5%" with linespoint,\
		 "hot100_1M.csv" using "skew":"median" title "hotkey subset: 1e-4%" with linespoint,\
		 "hot1K_1M.csv" using "skew":"median" title "hotkey subset: 0.001%" with linespoint

set xrange [0.5: 1.0]
set title "Mocked protocol comparison at lower skews, keyspace=1M"
set output "protocol_comparison_1M_lowskews.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint,\
		 "hot1_1M.csv" using "skew":"median" title "hotkey in [0, 1]" with linespoint,\
		 "hot10_1M.csv" using "skew":"median" title "hotkey in [0, 10]" with linespoint,\
		 "hot100_1M.csv" using "skew":"median" title "hotkey in [0, 100]" with linespoint,\
		 "hot1K_1M.csv" using "skew":"median" title "hotkey in [0, 1K]" with linespoint

set xrange [0.4:1.6]
set title "Mocked protocol, keyspace=1M"
set output "protocol_comparison_baseline_1hot.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint,\
		 "hot1_1M.csv" using "skew":"median" title "hotkey in [0, 1]" with linespoint

set title "Baseline"
set output "baseline.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint
