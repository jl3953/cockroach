set terminal png

set xlabel "key in [0 to 10^9)"

set ylabel "pdf"
set output "pdf0-0.3.png"

plot "pdf0.0.csv" using "key":"frequency" title "s=0.0" with point,\
	 	 "pdf0.1.csv" using "key":"frequency" title "s=0.1" with point,\
	 	 "pdf0.2.csv" using "key":"frequency" title "s=0.2" with point,\
	 	 "pdf0.3.csv" using "key":"frequency" title "s=0.3" with point

set output "pdf0.4-0.6.png"
plot "pdf0.4.csv" using "key":"frequency" title "s=0.4" with point,\
		 "pdf0.5.csv" using "key":"frequency" title "s=0.5" with point,\
		 "pdf0.6.csv" using "key":"frequency" title "s=0.6" with point

set output "pdf0.7-1.2.png"
plot "pdf0.7.csv" using "key":"frequency" title "s=0.7" with linespoint,\
		 "pdf0.8.csv" using "key":"frequency" title "s=0.8" with linespoint,\
		 "pdf0.9.csv" using "key":"frequency" title "s=0.9" with linespoint,\
		 "pdf1.0.csv" using "key":"frequency" title "s=1.0" with linespoint,\
		 "pdf1.1.csv" using "key":"frequency" title "s=1.1" with linespoint,\
		 "pdf1.2.csv" using "key":"frequency" title "s=1.2" with linespoint

set ylabel "cdf"
set output "cdf-1B.png"
set title "cdf"
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

