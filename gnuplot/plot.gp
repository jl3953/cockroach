set title "Throughput (reads) vs. skew"
set xlabel "Power Law s"
set ylabel "Throughput (txn over 30s)"
set terminal png
set title "Throughput vs skew with 2 clients"

set output "tp_v_s_single_and_multiclient.png"
set ylabel "Throughput (txn / sec)"
plot "logs-32-2nodes.csv" using "skew":"ops/sec(cum)" title "tp-32, 2 clients" with linespoint,\
		 "logs-64.csv" using "skew":"ops/sec(cum)" title "tp-64, 1 client" with linespoint

set output "p99_v_s_single_and_multiclient.png"
set ylabel "p99 (ms)"
plot "logs-32-2nodes.csv" using "skew":"p99(ms)" title "tp-32, 2 clients" with linespoint,\
		 "logs-64.csv" using "skew":"p99(ms)" title "tp-64, 1 client" with linespoint

# set output "tp_v_s-2clients.png"
# 
# plot "logs-8-2nodes.csv" using "skew":"ops(total)" title "tp-8" with linespoint,\
# 		 "logs-16-2nodes.csv" using "skew":"ops(total)" title "tp-16" with linespoint,\
# 		 "logs-33-2nodes.csv" using "skew":"ops(total)" title "tp-33" with linespoint,\
# 		 "logs-64-2nodes-halfskew.csv" using "skew":"ops(total)" title "tp-64" with linespoint,\
# 		 "logs-128-2nodes.csv" using "skew":"ops(total)" title "tp-128" with linespoint
# 
# 
# set output "p99_v_s-2clients.png"
# set ylabel "p99 (ms)"
# set title "p99 vs skew with 2 clients"
# plot "logs-33-2nodes.csv" using "skew":"p99(ms)" title "p99-33" with linespoint,\
# 		 "logs-64-2nodes.csv" using "skew":"p99(ms)" title "p99-64" with linespoint,\
# 		 "logs-128-2nodes.csv" using "skew":"p99(ms)" title "p99-128" with linespoint
# 
# set ylabel "Throughput (txn over 120s)"
# set output "tp_v_s-64_reads.png"
# 
# plot "logs-64.csv" using "skew":"ops(total)-r" title "tp-64" with linespoint,\
# 	 "logs-64-hot.csv" using "skew":"ops(total)-r" title "tp-64-hot" with linespoint,\
# 	 "logs-64-10keys.csv" using "skew": "ops(total)-r" title "tp-64-10keys" with linespoint
# 
# set output "tp_v_s-64.png"
# set title "Throughput vs. skew"
# plot "logs-64.csv" using "skew":"ops(total)" title "tp-64" with linespoint,\
# 		 "logs-64-hot.csv" using "skew":"ops(total)" title "tp-64-hot" with linespoint,\
# 		 "logs-64-10keys.csv" using "skew":"ops(total)" title "tp-64-10keys" with linespoint
# 
# set output "tail_v_s-64_reads.png"
# set title "Tail Latency (reads) vs. skew"
# set xlabel "Power Law s"
# set ylabel "P99 (ms)"
# 
# plot "logs-64.csv" using "skew":"p99(ms)-r" title "p99-64" with linespoint,\
# 		 "logs-64-hot.csv" using "skew":"p99(ms)-r" title "p99-64-hot" with linespoint,\
# 		 "logs-64-10keys.csv" using "skew":"p99(ms)-r" title "p99-64-10keys" with linespoint
# 
# set output "tail_v_s-64.png"
# set title "Tail Latency vs. skew"
# plot "logs-64.csv" using "skew":"p99(ms)" title "p99-64" with linespoint,\
# 		 "logs-64-hot.csv" using "skew":"p99(ms)" title "p99-64-hot" with linespoint,\
# 		 "logs-64-10keys.csv" using "skew":"p99(ms)" title "p99-64-10keys" with linespoint
# 
# set output "tp_v_s-64_10keys.png"
# set xlabel "Power Law s"
# set ylabel "Throughput (txn over 120 s)"
# plot "logs-64-10keys.csv" using "skew":"ops(total)" title "tp-64-10keys" with linespoint
