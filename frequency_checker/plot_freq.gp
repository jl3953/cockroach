set terminal png

set xlabel "key rank"
set logscale x

set ylabel "cdf"
set output "cdf-1M-batch6.png"
set title "CDF for 1M keys"
plot "cdf0.5.csv" using "key":"frequency" title "s=0.5" with linespoint,\
		 "cdf0.6.csv" using "key":"frequency" title "s=0.6" with linespoint,\
		 "cdf0.7.csv" using "key":"frequency" title "s=0.7" with linespoint,\
		 "cdf0.8.csv" using "key":"frequency" title "s=0.8" with linespoint,\
		 "cdf0.9.csv" using "key":"frequency" title "s=0.9" with linespoint,\
		 "cdf1.0.csv" using "key":"frequency" title "s=1.0" with linespoint,\
		 "cdf1.1.csv" using "key":"frequency" title "s=1.1" with linespoint,\
		 "cdf1.2.csv" using "key":"frequency" title "s=1.2" with linespoint,\
		 "cdf1.3.csv" using "key":"frequency" title "s=1.3" with linespoint,\
		 "cdf1.4.csv" using "key":"frequency" title "s=1.4" with linespoint,\
		 "cdf1.5.csv" using "key":"frequency" title "s=1.5" with linespoint

