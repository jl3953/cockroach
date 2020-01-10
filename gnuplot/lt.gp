set terminal png

set xlabel "tp (txn/sec)"
set ylabel "p95 (ms)"
set title "latency throughput graph"
set output "lt_tp_p95.png"

plot "cololocated_one_hot.csv" using "ops/sec(cum)":"p95(ms)" with linespoint
