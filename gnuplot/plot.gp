set terminal png

set xlabel "zipfian constant"
set ylabel "throughput"
set output "uniform_benchmark.png"
plot "new_zipfian_overload.csv" using "skew":"ops/sec(cum)" title "trial=0" with linespoint,\
		 "new_zipfian_overload1.csv" using "skew":"ops/sec(cum)" title "trial=1" with linespoint,\
		 "new_zipfian_overload2.csv" using "skew":"ops/sec(cum)" title "trial=2" with linespoint,\
		 "new_zipfian_overload3.csv" using "skew":"ops/sec(cum)" title "trial=3" with linespoint,\
		 "new_zipfian_overload4.csv" using "skew":"ops/sec(cum)" title "trial=4" with linespoint,\
		 "new_zipfian_overload5.csv" using "skew":"ops/sec(cum)" title "trial=5" with linespoint,\
		 "new_zipfian_overload6.csv" using "skew":"ops/sec(cum)" title "trial=6" with linespoint,\
		 "new_zipfian_overload7.csv" using "skew":"ops/sec(cum)" title "trial=7" with linespoint,\
		 "new_zipfian_overload8.csv" using "skew":"ops/sec(cum)" title "trial=8" with linespoint,\
		 "new_zipfian_overload9.csv" using "skew":"ops/sec(cum)" title "trial=9" with linespoint

set xlabel "tp (txns/sec)"
set ylabel "latency"
set output "lt_8clients.png"
plot "lt_8clients.csv" using "ops/sec(cum)":"p99(ms)" with linespoint

# set xlabel "tp (txns/sec)"
# set ylabel "latency"
# set output "match.png"
# plot "old_zipfian_match.csv" using "skew":"ops/sec(cum)" title "old" with linespoint,\
# 		 "new_zipfian_match.csv" using "skew":"ops/sec(cum)" title "new" with linespoint
# 
# set output "lt_uniform.png"
# plot "lt_uniform.csv" using "ops/sec(cum)":"p99(ms)" with linespoint,\
# 		 #"lt_uniform.csv" using "ops/sec(cum)":"p99(ms)" with linespoint

# set xlabel "skew"
# set ylabel "Throughput (txns/sec)"
# 
# 
# set output "zoom_low_skew.png"
# set title "tp v low skews"
# plot "low_skew.csv" using "skew":"ops/sec(cum)" title "trial=0" with linespoint,\
# 		"low_skew1.csv" using "skew":"ops/sec(cum)" title "trial=1" with linespoint,\
# 		"low_skew2.csv" using "skew":"ops/sec(cum)" title "trial=2" with linespoint,\
# 		"new_zipfian_low_skews.csv" using "skew":"ops/sec(cum)" title "new" with linespoint,\
# 		 "old_zipfian.csv" using "skew":"ops/sec(cum)" title "old" with linespoint,\
# 		 "new_zipfian_low_skews_2.csv" using "skew":"ops/sec(cum)" title "new, trial2" with linespoint
# 		# "low_skew3.csv" using "skew":"ops/sec(cum)" title "trial=3" with linespoint,\
# 		# "low_skew4.csv" using "skew":"ops/sec(cum)" title "trial=4" with linespoint,\
# 		# "low_skew5.csv" using "skew":"ops/sec(cum)" title "trial=5" with linespoint,\
# 		# "low_skew6.csv" using "skew":"ops/sec(cum)" title "trial=6" with linespoint,\
# 		# "low_skew7.csv" using "skew":"ops/sec(cum)" title "trial=7" with linespoint,\
# 		# "low_skew8.csv" using "skew":"ops/sec(cum)" title "trial=8" with linespoint,\
# 
# set output "new_v_old.png"
# set title "new vs old zipfian"
# plot "new_zipfian_low_skews.csv" using "skew":"ops/sec(cum)" title "new" with linespoint,\
# 		 "old_zipfian.csv" using "skew":"ops/sec(cum)" title "old" with linespoint,\
# 		 "new_zipfian_low_skews_2.csv" using "skew":"ops/sec(cum)" title "new, trial2" with linespoint
# 
# set output "tp_v_skew_edge.png"
# set title "TP vs skew"
# plot "single_key_56.csv" using "skew":"ops/sec(cum)" title "concurrency=56" with linespoint,\
# 		 "single_key_64.csv" using "skew":"ops/sec(cum)" title "concurrency=64" with linespoint,\
# 		 "single_key_91.csv" using "skew":"ops/sec(cum)" title "concurrency=91" with linespoint
# set output "p99_v_skew_edge.png"
# plot "single_key_56.csv" using "skew":"p99(ms)" title "concurrency=56" with linespoint,\
# 		 "single_key_64.csv" using "skew":"p99(ms)" title "concurrency=64" with linespoint,\
# 		 "single_key_91.csv" using "skew":"p99(ms)" title "concurrency=91" with linespoint

# set output "single_key_latency_tp.png"
# set title "Latency vs Tp"
# plot "single_key_latency_tp_stripped.csv" using "ops/sec(cum)":"p99(ms)" title "jenn" with linespoint

# plot "single_key_64.csv" using "ops/sec(cum)":"p99(ms)" title "concurrency=64" with linespoint,\
# 		 "single_key_72.csv" using "ops/sec(cum)":"p99(ms)" title "concurrency=72" with linespoint,\
# 		 "single_key_80.csv" using "ops/sec(cum)":"p99(ms)" title "concurrency=80" with linespoint,\
# 		 "single_key_96.csv" using "ops/sec(cum)":"p99(ms)" title "concurrency=96" with linespoint

# set output "single_key_optimal_concurrency.png"
# set title "TP/sec vs. skew"
# plot "single_key_64.csv" using "skew":"ops/sec(cum)" title "concurrency=64" with linespoint,\
# 		 "single_key_72.csv" using "skew":"ops/sec(cum)" title "concurrency=72" with linespoint,\
# 		 "single_key_80.csv" using "skew":"ops/sec(cum)" title "concurrency=80" with linespoint,\
# 		 "single_key_96.csv" using "skew":"ops/sec(cum)" title "concurrency=96" with linespoint,
# 
# set output "single_key_optimal_concurrency_latency.png"
# plot "single_key_64.csv" using "skew":"p99(ms)" title "concurrency=64" with linespoint,\
# 		 "single_key_72.csv" using "skew":"p99(ms)" title "concurrency=72" with linespoint,\
# 		 "single_key_80.csv" using "skew":"p99(ms)" title "concurrency=80" with linespoint,\
# 		 "single_key_96.csv" using "skew":"p99(ms)" title "concurrency=96" with linespoint

# set output "single_key_optimal_threads.png"
# set title "TP/sec vs. skew"
# plot "single_key_64_15.csv" using "skew":"ops/sec(cum)" title "14 secs" with linespoint,\
# 		 "single_key_64_9.csv" using "skew":"ops/sec(cum)" title "9 secs" with linespoint,\
# 		 "single_key_64_60.csv" using "skew":"ops/sec(cum)" title "60 secs" with linespoint

# set title "Throughput vs skew with 2 clients"

# set output "tp_v_s_single_and_multiclient.png"
# set ylabel "Throughput (txn / sec)"
# plot "logs-32-2nodes.csv" using "skew":"ops/sec(cum)" title "tp-32, 2 clients" with linespoint,\
# 		 "logs-64.csv" using "skew":"ops/sec(cum)" title "tp-64, 1 client" with linespoint
# 
# set output "p99_v_s_single_and_multiclient.png"
# set ylabel "p99 (ms)"
# plot "logs-32-2nodes.csv" using "skew":"p99(ms)" title "tp-32, 2 clients" with linespoint,\
# 		 "logs-64.csv" using "skew":"p99(ms)" title "tp-64, 1 client" with linespoint
# 
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
# plot "logs-64.csv" using "skew":"ops/sec(cum)" title "tp-64" with linespoint,\
# 		 "logs-64-hot.csv" using "skew":"ops/sec(cum)" title "tp-64-hot" with linespoint,\
# 		 "logs-64-10keys.csv" using "skew":"ops/sec(cum)" title "tp-64-10keys" with linespoint,\
# 		 "logs-64-10hot.csv" using "skew":"ops/sec(cum)" title "tp-64-10hot" with linespoint
# 

#set output "tp_v_s-64-10hot.png"
#plot "logs-64-10hot.csv" using "skew":"ops/sec(cum)" with linespoint

# set output "high_for_multikey.png"
# plot "logs-64-10hot.csv" using "skew":"ops/sec(cum)" title "n=10" with linespoint,\
# 		 "logs-64-5hot.csv" using "skew":"ops/sec(cum)" title "n=5" with linespoint,\
# 		 "logs-64-3hot.csv" using "skew":"ops/sec(cum)" title "n=3" with linespoint,\
# 		 "logs-64-2hot.csv" using "skew":"ops/sec(cum)" title "n=2" with linespoint
# 

set output "high_for_10keys.png"
plot "logs-64-10hot.csv" using "skew":"ops/sec(cum)" title "c=64" with linespoint,\
		 "logs-32-10hot.csv" using "skew":"ops/sec(cum)" title "c=32" with linespoint,\
		 "logs-8-10hot.csv" using "skew":"ops/sec(cum)" title "c=8" with linespoint

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
