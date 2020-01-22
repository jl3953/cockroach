set terminal png

set xlabel "key rank"
set logscale x
set ylabel "cdf"

set output "cdf-1M-comparison.png"
set title "CDF comparisons, keyspace = 1M"
plot "cdf-1M_0.7.csv" using "key":"frequency" title "batch=1 key, s=0.7" with linespoint,\
		 "cdf-1M-dedup-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.7" with linespoint,\
		 "cdf-1M-distinct-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, distinct, s=0.7" with linespoint,\
		 "cdf-1M_1.0.csv" using "key":"frequency" title "batch=1 key, s=.99" with linespoint,\
		 "cdf-1M-dedup-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.99" with linespoint,\
		 "cdf-1M-distinct-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, distinct, s=0.99" with linespoint,\
		 "cdf-1M_1.2.csv" using "key":"frequency" title "batch=1 key, s=1.2" with linespoint,\
		 "cdf-1M-dedup-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.2" with linespoint,\
		 "cdf-1M-distinct-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, distinct, s=1.2" with linespoint

set output "cdf-10M-comparison.png"
set title "CDF comparisons, keyspace = 10M"
plot "cdf-10M_0.7.csv" using "key":"frequency" title "batch=1 key, s=0.7" with linespoint,\
		 "cdf-10M-dedup-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.7" with linespoint,\
		 "cdf-10M-distinct-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, distinct, s=0.7" with linespoint,\
		 "cdf-10M_1.0.csv" using "key":"frequency" title "batch=1 key, s=.99" with linespoint,\
		 "cdf-10M-dedup-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.99" with linespoint,\
		 "cdf-10M-distinct-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, distinct, s=0.99" with linespoint,\
		 "cdf-10M_1.2.csv" using "key":"frequency" title "batch=1 key, s=1.2" with linespoint,\
		 "cdf-10M-dedup-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.2" with linespoint,\
		 "cdf-10M-distinct-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, distinct, s=1.2" with linespoint

set output "cdf-100M-comparison.png"
set title "CDF comparisons, keyspace = 100M"
plot "cdf-100M_0.7.csv" using "key":"frequency" title "batch=1 key, s=0.7" with linespoint,\
		 "cdf-100M-dedup-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.7" with linespoint,\
		 "cdf-100M-distinct-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, distinct, s=0.7" with linespoint,\
		 "cdf-100M_1.0.csv" using "key":"frequency" title "batch=1 key, s=.99" with linespoint,\
		 "cdf-100M-dedup-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.99" with linespoint,\
		 "cdf-100M-distinct-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, distinct, s=0.99" with linespoint,\
		 "cdf-100M_1.2.csv" using "key":"frequency" title "batch=1 key, s=1.2" with linespoint,\
		 "cdf-100M-dedup-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.2" with linespoint,\
		 "cdf-100M-distinct-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, distinct, s=1.2" with linespoint

set output "cdf-keyspace-comparison.png"
set title "CDF comparisons across keyspaces"
plot "cdf-1M-dedup-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.7, keyspace=1M" with linespoint,\
		 "cdf-10M-dedup-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.7, keyspace=10M" with linespoint,\
		 "cdf-100M-dedup-batch6_0.7.csv" using "key":"frequency" title "batch=6 keys, dedup, s=0.7, keyspace=100M" with linespoint,\
		 "cdf-1M-dedup-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.0, keyspace=1M" with linespoint,\
		 "cdf-10M-dedup-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.0, keyspace=10M" with linespoint,\
		 "cdf-100M-dedup-batch6_1.0.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.0, keyspace=100M" with linespoint,\
		 "cdf-1M-dedup-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.2, keyspace=1M" with linespoint,\
		 "cdf-10M-dedup-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.2, keyspace=10M" with linespoint,\
		 "cdf-100M-dedup-batch6_1.2.csv" using "key":"frequency" title "batch=6 keys, dedup, s=1.2, keyspace=100M" with linespoint,\
