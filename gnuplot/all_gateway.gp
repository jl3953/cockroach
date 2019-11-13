set terminal png

set xlabel "skew"
set ylabel "tp (txn/sec)"
set title "gateway"
set output "gateway.png"


plot     "new_zipfian_read95.csv" using  "skew":"ops/sec(cum)" title "trial=0" with linespoint,\
          "new_zipfian_read951.csv" using "skew":"ops/sec(cum)" title "trial=1" with linespoint,\
          "new_zipfian_read952.csv" using "skew":"ops/sec(cum)" title "trial=2" with linespoint,\
          "new_zipfian_read953.csv" using "skew":"ops/sec(cum)" title "trial=3" with linespoint,\
          "new_zipfian_read954.csv" using "skew":"ops/sec(cum)" title "trial=4" with linespoint,\
		  "all_gateway_skew.csv" using "skew":"ops/sec(cum)" title "gateway, trial=0" with linespoint,\
		 "all_gateway_1_skew.csv" using "skew":"ops/sec(cum)" title "gateway, trial=1" with linespoint,\
		 "all_gateway_2_skew.csv" using "skew":"ops/sec(cum)" title "gateway, trial=2" with linespoint,\
		 "all_gateway_3_skew.csv" using "skew":"ops/sec(cum)" title "gateway, trial=3" with linespoint,\
		 "all_gateway_4_skew.csv" using "skew":"ops/sec(cum)" title "gateway, trial=4" with linespoint,\
		 "new_zipfian_hot_n11.csv" using "skew":"ops/sec(cum)" title "hot one, trial=1" with linespoint,\
          "new_zipfian_hot_n12.csv" using "skew":"ops/sec(cum)" title "hot one, trial=2" with linespoint,\
          "new_zipfian_hot_n13.csv" using "skew":"ops/sec(cum)" title "hot one, trial=3" with linespoint,\
		  "new_zipfian_hot_n14.csv" using "skew":"ops/sec(cum)" title "hot one, trial=4" with linespoint

