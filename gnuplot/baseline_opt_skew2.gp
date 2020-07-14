set terminal png

set xlabel "zipf constant"
set ylabel "tp (txn/sec)"
set title "optimal at skew 2 vs uniform"
set output "baseline_opt_skew2.png"

plot "new_zipfian_read95.csv" using  "skew":"ops/sec(cum)" title "trial=0" with linespoint,\
     "new_zipfian_read951.csv" using "skew":"ops/sec(cum)" title "trial=1" with linespoint,\
     "new_zipfian_read952.csv" using "skew":"ops/sec(cum)" title "trial=2" with linespoint,\
     "new_zipfian_read953.csv" using "skew":"ops/sec(cum)" title "trial=3" with linespoint,\
     "new_zipfian_read954.csv" using "skew":"ops/sec(cum)" title "trial=4" with linespoint,\
	 "baseline_opt_skew2_skew.csv" using "skew":"ops/sec(cum)" title "skew=2.0, trial=0" with linespoint,\
	 "baseline_opt_skew2_1_skew.csv" using "skew":"ops/sec(cum)" title "skew=2.0, trial=1" with linespoint,\
	 "baseline_opt_skew2_2_skew.csv" using "skew":"ops/sec(cum)" title "skew=2.0, trial=2" with linespoint,\
	 "baseline_opt_skew2_3_skew.csv" using "skew":"ops/sec(cum)" title "skew=2.0, trial=3" with linespoint,\
	 "baseline_opt_skew2_4_skew.csv" using "skew":"ops/sec(cum)" title "skew=2.0, trial=4" with linespoint
