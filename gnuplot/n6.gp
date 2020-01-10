set terminal png

set xlabel "skew"
set ylabel "tp (txn/sec)"
set title "6 keys"
set output "n6.png"

plot "n6.csv" using "skew":"ops/sec(cum)-r" title "trial=0, read" with linespoint,\
		 "n61.csv" using "skew":"ops/sec(cum)-r" title "trial=1, read" with linespoint,\
		 "n62.csv" using "skew":"ops/sec(cum)-r" title "trial=2, read" with linespoint,\
		 "n63.csv" using "skew":"ops/sec(cum)-r" title "trial=3, read" with linespoint,\
		 "n64.csv" using "skew":"ops/sec(cum)-r" title "trial=4, read" with linespoint,\
		 "n6.csv" using "skew":"ops/sec(cum)-w" title "trial=0, write" with linespoint,\
         "n61.csv" using "skew":"ops/sec(cum)-w" title "trial=1, write" with linespoint,\
         "n62.csv" using "skew":"ops/sec(cum)-w" title "trial=2, write" with linespoint,\
         "n63.csv" using "skew":"ops/sec(cum)-w" title "trial=3, write" with linespoint,\
         "n64.csv" using "skew":"ops/sec(cum)-w" title "trial=4, write" with linespoint

set ylabel "p50(ms)"
set title "p50(ms)"
set output "n6_p50.png"
plot "n6.csv" using "skew":"p50(ms)-r" title "trial=0, read" with linespoint,\
		 "n61.csv" using "skew":"p50(ms)-r" title "trial=1, read" with linespoint,\
		 "n62.csv" using "skew":"p50(ms)-r" title "trial=2, read" with linespoint,\
		 "n63.csv" using "skew":"p50(ms)-r" title "trial=3, read" with linespoint,\
		 "n64.csv" using "skew":"p50(ms)-r" title "trial=4, read" with linespoint,\
		 "n6.csv" using "skew":"p50(ms)-w" title "trial=0, write" with linespoint,\
         "n61.csv" using "skew":"p50(ms)-w" title "trial=1, write" with linespoint,\
         "n62.csv" using "skew":"p50(ms)-w" title "trial=2, write" with linespoint,\
         "n63.csv" using "skew":"p50(ms)-w" title "trial=3, write" with linespoint,\
         "n64.csv" using "skew":"p50(ms)-w" title "trial=4, write" with linespoint

set ylabel "p99(ms)"
set title "p99(ms)"
set output "n6_p99.png"
plot "n6.csv" using "skew":"p99(ms)-r" title "trial=0, read" with linespoint,\
		 "n61.csv" using "skew":"p99(ms)-r" title "trial=1, read" with linespoint,\
		 "n62.csv" using "skew":"p99(ms)-r" title "trial=2, read" with linespoint,\
		 "n63.csv" using "skew":"p99(ms)-r" title "trial=3, read" with linespoint,\
		 "n64.csv" using "skew":"p99(ms)-r" title "trial=4, read" with linespoint,\
		 "n6.csv" using "skew":"p99(ms)-w" title "trial=0, write" with linespoint,\
         "n61.csv" using "skew":"p99(ms)-w" title "trial=1, write" with linespoint,\
         "n62.csv" using "skew":"p99(ms)-w" title "trial=2, write" with linespoint,\
         "n63.csv" using "skew":"p99(ms)-w" title "trial=3, write" with linespoint,\
         "n64.csv" using "skew":"p99(ms)-w" title "trial=4, write" with linespoint

