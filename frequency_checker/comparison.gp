set terminal png

set xlabel "key rank"
set logscale x
set ylabel "cdf"

set output "cdf-1M-comparison_0.7.png"
set title "CDF comparisons, s=0.7"
plot "cdf-1M_0.7.csv" using "key":"frequency" title "batch=1 key" with linespoint,\
		 "cdf-1M-dedup-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, dedup" with linespoint,\
		 "cdf-1M-distinct-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, distinct" with linespoint

set output "cdf-1M-comparison_1.0.png"
set title "CDF comparisons, s=0.99"
plot "cdf-1M_1.0.csv" using "key":"frequency" title "batch=1 key" with linespoint,\
		 "cdf-1M-dedup-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, dedup" with linespoint,\
		 "cdf-1M-distinct-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, distinct" with linespoint

set output "cdf-1M-comparison_1.2.png"
set title "CDF comparisons, s=1.2"
plot "cdf-1M_1.2.csv" using "key":"frequency" title "batch=1 key" with linespoint,\
		 "cdf-1M-dedup-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, dedup" with linespoint,\
		 "cdf-1M-distinct-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, distinct" with linespoint


