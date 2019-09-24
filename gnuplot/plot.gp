set title "Throughput (reads) vs. skew"
set xlabel "Power Law s"
set ylabel "Throughput (txn over 120s)"
set terminal png
set output "tp_v_s-64_reads.png"

plot "logs-64.csv" using "skew":"ops(total)-r" title "tp-64" with linespoint,\
	 "logs-64-hot.csv" using "skew":"ops(total)-r" title "tp-64-hot" with linespoint,\
	 "logs-64-10keys.csv" using "skew": "ops(total)-r" title "tp-64-10keys" with linespoint

set output "tp_v_s-64.png"
set title "Throughput vs. skew"
plot "logs-64.csv" using "skew":"ops(total)" title "tp-64" with linespoint,\
		 "logs-64-hot.csv" using "skew":"ops(total)" title "tp-64-hot" with linespoint,\
		 "logs-64-10keys.csv" using "skew":"ops(total)" title "tp-64-10keys" with linespoint

set output "tail_v_s-64_reads.png"
set title "Tail Latency (reads) vs. skew"
set xlabel "Power Law s"
set ylabel "P99 (ms)"

plot "logs-64.csv" using "skew":"p99(ms)-r" title "p99-64" with linespoint,\
		 "logs-64-hot.csv" using "skew":"p99(ms)-r" title "p99-64-hot" with linespoint,\
		 "logs-64-10keys.csv" using "skew":"p99(ms)-r" title "p99-64-10keys" with linespoint

set output "tail_v_s-64.png"
set title "Tail Latency vs. skew"
plot "logs-64.csv" using "skew":"p99(ms)" title "p99-64" with linespoint,\
		 "logs-64-hot.csv" using "skew":"p99(ms)" title "p99-64-hot" with linespoint,\
		 "logs-64-10keys.csv" using "skew":"p99(ms)" title "p99-64-10keys" with linespoint
