set terminal png

set xlabel "zipf const"
set ylabel "tp (txn/sec)"
set title "reads at 100%"
set output "read100.png"

plot "new_zipfian_read95.csv" using  "skew":"ops/sec(cum)" title "trial=0" with linespoint,\
 		 "new_zipfian_read951.csv" using "skew":"ops/sec(cum)" title "trial=1" with linespoint,\
 		 "new_zipfian_read952.csv" using "skew":"ops/sec(cum)" title "trial=2" with linespoint,\
 		 "new_zipfian_read953.csv" using "skew":"ops/sec(cum)" title "trial=3" with linespoint,\
 		 "new_zipfian_read954.csv" using "skew":"ops/sec(cum)" title "trial=4" with linespoint,\
		 "read100_tryagain_skew.csv" using "skew":"ops/sec(cum)" title "read=100%, trial=0" with linespoint,\
		  "read100_tryagain_1_skew.csv" using "skew":"ops/sec(cum)" title "read=100%, trial=1" with linespoint,\
		  "read100_tryagain_2_skew.csv" using "skew":"ops/sec(cum)" title "read=100%, trial=2" with linespoint,\
		  "read100_tryagain_3_skew.csv" using "skew":"ops/sec(cum)" title "read=100%, trial=3" with linespoint,\
