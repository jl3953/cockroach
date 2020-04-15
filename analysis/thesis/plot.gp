set terminal png

set xlabel "s"
set ylabel "throughput (txns/sec)"

set title "Mocked protocol comparison, keyspace=1M"
set output "protocol_comparison_1M.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint,\
		 "hot1_1M.csv" using "skew":"median" title "hotkey in [0, 1]" with linespoint,\
		 "hot10_1M.csv" using "skew":"median" title "hotkey in [0, 10]" with linespoint,\
		 "hot100_1M.csv" using "skew":"median" title "hotkey in [0, 100]" with linespoint,\
		 "hot1K_1M.csv" using "skew":"median" title "hotkey in [0, 1K]" with linespoint

set xrange [0.5: 1.0]
set title "Mocked protocol comparison at lower skews, keyspace=1M"
set output "protocol_comparison_1M_lowskews.png"
plot "baseline.csv" using "skew":"median" title "baseline" with linespoint,\
		 "hot1_1M.csv" using "skew":"median" title "hotkey in [0, 1]" with linespoint,\
		 "hot10_1M.csv" using "skew":"median" title "hotkey in [0, 10]" with linespoint,\
		 "hot100_1M.csv" using "skew":"median" title "hotkey in [0, 100]" with linespoint,\
		 "hot1K_1M.csv" using "skew":"median" title "hotkey in [0, 1K]" with linespoint
set xrange restore
