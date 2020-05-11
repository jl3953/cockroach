set terminal png

set xlabel "zipfian constant (s)"
set ylabel "throughput (txns/sec)"

set title "Baseline"
set output "baseline.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint

set logscale y
set title "Mocked protocol, keyspace=1M"
set output "protocol_comparison_baseline_1hot.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint,\
		 "1.csv" using "skew":"median" title "hotkey subset: 2 keys" with linespoint

set output "protocol_comparison_1M.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint,\
		 "1.csv" using "skew":"median" title "hotkey subset: 2 keys" with linespoint,\
		 "10_combined.csv" using "skew":"median" title "hotkey subset: 10 keys" with linespoint,\
		 "100_combined.csv" using "skew":"median" title "hotkey subset: 100 keys" with linespoint,\
		 "1k_combined.csv" using "skew":"median" title "hotkey subset: 1000 keys" with linespoint

# set xrange [0.5: 1.0]
# set title "Mocked protocol comparison at lower skews, keyspace=1M"
# set output "protocol_comparison_1M_lowskews.png"
# plot "baseline.csv" using "skew":"median" title "baseline" with linespoint,\
# 		 "hot1_1M.csv" using "skew":"median" title "hotkey in [0, 1]" with linespoint,\
# 		 "hot10_1M.csv" using "skew":"median" title "hotkey in [0, 10]" with linespoint,\
# 		 "hot100_1M.csv" using "skew":"median" title "hotkey in [0, 100]" with linespoint,\
# 		 "hot1K_1M.csv" using "skew":"median" title "hotkey in [0, 1K]" with linespoint


