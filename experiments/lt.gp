set terminal png
set xlabel "throughput (txn/sec)"

# ARG1 is the csv file
# ARG2 is the output location of the graphs

set ylabel "p50 (ms)"
set title "latency throughput (p50)"
set output ARG2."/lt_tp_p50.png"
plot ARG1 using "ops/sec(cum)":"p50(ms)" with linespoint

set ylabel "p95 (ms)"
set title "latency throughput (p95)"
set output ARG2."/lt_tp_p95.png"
plot ARG1 using "ops/sec(cum)":"p95(ms)" with linespoint

set ylabel "p99 (ms)"
set title "latency throughput (p99)"
set output ARG2."/lt_tp_p99.png"
plot ARG1 using "ops/sec(cum)":"p99(ms)" with linespoint
