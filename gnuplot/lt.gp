set terminal png

set xlabel "tp (txn/sec)"
set ylabel "p50 (ms)"
set title "latency throughput graph"
set output "lt_tp_p50.png"

plot "baseline_lt.csv" using "ops/sec(cum)":"p50(ms)" with linespoint
