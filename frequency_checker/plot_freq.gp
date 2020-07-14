set terminal png

set xlabel "key rank"
set logscale x

set ylabel "cdf"
set output "cdf-1M.png"
set title "CDF for 1M keys"
plot "cdf-1M_0.5.csv" using "key":"frequency" title "s=0.5" with linespoint,\
		 "cdf-1M_0.6.csv" using "key":"frequency" title "s=0.6" with linespoint,\
		 "cdf-1M_0.7.csv" using "key":"frequency" title "s=0.7" with linespoint,\
		 "cdf-1M_0.8.csv" using "key":"frequency" title "s=0.8" with linespoint,\
		 "cdf-1M_0.9.csv" using "key":"frequency" title "s=0.9" with linespoint,\
		 "cdf-1M_1.0.csv" using "key":"frequency" title "s=1.0" with linespoint,\
		 "cdf-1M_1.1.csv" using "key":"frequency" title "s=1.1" with linespoint,\
		 "cdf-1M_1.2.csv" using "key":"frequency" title "s=1.2" with linespoint,\
		 "cdf-1M_1.3.csv" using "key":"frequency" title "s=1.3" with linespoint,\
		 "cdf-1M_1.4.csv" using "key":"frequency" title "s=1.4" with linespoint,\
		 "cdf-1M_1.5.csv" using "key":"frequency" title "s=1.5" with linespoint

set output "cdf-10M.png"
set title "CDF for 10M keys"
plot "cdf-10M_0.5.csv" using "key":"frequency" title "s=0.5" with linespoint,\
		 "cdf-10M_0.6.csv" using "key":"frequency" title "s=0.6" with linespoint,\
		 "cdf-10M_0.7.csv" using "key":"frequency" title "s=0.7" with linespoint,\
		 "cdf-10M_0.8.csv" using "key":"frequency" title "s=0.8" with linespoint,\
		 "cdf-10M_0.9.csv" using "key":"frequency" title "s=0.9" with linespoint,\
		 "cdf-10M_1.0.csv" using "key":"frequency" title "s=1.0" with linespoint,\
		 "cdf-10M_1.1.csv" using "key":"frequency" title "s=1.1" with linespoint,\
		 "cdf-10M_1.2.csv" using "key":"frequency" title "s=1.2" with linespoint,\
		 "cdf-10M_1.3.csv" using "key":"frequency" title "s=1.3" with linespoint,\
		 "cdf-10M_1.4.csv" using "key":"frequency" title "s=1.4" with linespoint,\
		 "cdf-10M_1.5.csv" using "key":"frequency" title "s=1.5" with linespoint

set output "cdf-100M.png"
set title "CDF for 100M keys"
plot "cdf-100M_0.5.csv" using "key":"frequency" title "s=0.5" with linespoint,\
		 "cdf-100M_0.6.csv" using "key":"frequency" title "s=0.6" with linespoint,\
		 "cdf-100M_0.7.csv" using "key":"frequency" title "s=0.7" with linespoint,\
		 "cdf-100M_0.8.csv" using "key":"frequency" title "s=0.8" with linespoint,\
		 "cdf-100M_0.9.csv" using "key":"frequency" title "s=0.9" with linespoint,\
		 "cdf-100M_1.0.csv" using "key":"frequency" title "s=1.0" with linespoint,\
		 "cdf-100M_1.1.csv" using "key":"frequency" title "s=1.1" with linespoint,\
		 "cdf-100M_1.2.csv" using "key":"frequency" title "s=1.2" with linespoint,\
		 "cdf-100M_1.3.csv" using "key":"frequency" title "s=1.3" with linespoint,\
		 "cdf-100M_1.4.csv" using "key":"frequency" title "s=1.4" with linespoint,\
		 "cdf-100M_1.5.csv" using "key":"frequency" title "s=1.5" with linespoint

# set output "cdf-1B.png"
# set title "CDF for 1B keys"
# plot "cdf0.5.csv" using "key":"frequency" title "s=0.5" with linespoint,\
# 		 "cdf0.6.csv" using "key":"frequency" title "s=0.6" with linespoint,\
# 		 "cdf0.7.csv" using "key":"frequency" title "s=0.7" with linespoint,\
# 		 "cdf0.8.csv" using "key":"frequency" title "s=0.8" with linespoint,\
# 		 "cdf0.9.csv" using "key":"frequency" title "s=0.9" with linespoint,\
# 		 "cdf1.0.csv" using "key":"frequency" title "s=1.0" with linespoint,\
# 		 "cdf1.1.csv" using "key":"frequency" title "s=1.1" with linespoint,\
# 		 "cdf1.2.csv" using "key":"frequency" title "s=1.2" with linespoint,\
# 		 "cdf1.3.csv" using "key":"frequency" title "s=1.3" with linespoint,\
# 		 "cdf1.4.csv" using "key":"frequency" title "s=1.4" with linespoint,\
# 		 "cdf1.5.csv" using "key":"frequency" title "s=1.5" with linespoint

