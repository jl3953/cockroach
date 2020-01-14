set terminal png

set xlabel "s"
set ylabel "throughput (txns/sec)"

set title "Mocked protocol comparison, keyspace 1M"
set output "protocol_comparison_1M.png"
plot "hot1_1M_cut.csv" using "skew":"median" title "hotkeys in [0, 1]" with linespoint,\
		 "hot10_1M.csv" using "skew":"median" title "hotkeys in [0, 10]" with linespoint,\
		 "hot100_1M.csv" using "skew":"median" title "hotkeys in [0, 100]" with linespoint,\
		 "hot1k_1M.csv" using "skew":"median" title "hotkeys in [0, 1k]" with linespoint,\
		 "hot10k_1M.csv" using "skew":"median" title "hotkeys in [0, 10k]" with linespoint

set title "Mocked protocol comparison, keyspace 10M"
set output "protocol_comparison_10M.png"
plot "hot10k_10M.csv" using "skew":"median" title "hotkeys in [0, 10k]" with linespoint,\
		 "hot100k_10M.csv" using "skew":"median" title "hotkeys in [0, 100k]" with linespoint,\
		 "hot1M_10M.csv" using "skew":"median" title "hotkeys in [0, 1M]" with linespoint

set title "Mocked protocol comparison over keyspaces, hotkey cdf apprx 0.3"
set output "protocol_comparison_cdf_0.3.png"
plot "hot10k_1M.csv" using "skew":"median" title "keyspace=1M, hotkeys in [0, 10k]" with linespoint,\
		 "hot1M_10M.csv" using "skew":"median" title "keyspace=10M, hotkeys in [0, 1M]" with linespoint

set title "Mocked protocol, keyspace 1M, one hot key"
set output "protocol_1M.png"
plot "hot1_1M.csv" using "skew":"median" title "mocked hot key, batch size = 6" with linespoint,\
		 "keys5.csv" using "skew":"median" title "batch size=5" with linespoint,\
		 "keys6.csv" using "skew":"median" title "batch size=6" with linespoint

set title "Mocked protocol comparison, keyspace 1M"
set output "protocol_comparison_1M_lower.png"
plot "hot1_1M_lower.csv" using "skew":"median" title "hotkeys in [0, 1]" with linespoint,\
		 "hot10_1M_lower.csv" using "skew":"median" title "hotkeys in [0, 10]" with linespoint,\
		 "hot100_1M_lower.csv" using "skew":"median" title "hotkeys in [0, 100]" with linespoint,\
		 "hot1k_1M_lower.csv" using "skew":"median" title "hotkeys in [0, 1k]" with linespoint

