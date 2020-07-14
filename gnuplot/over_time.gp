set terminal png

set xlabel "time elapsed (s)"
set ylabel "tp (txn/sec)"
set title "tp vs time"
set output "over_time.png"

plot "baseline_overtime_stats_0.csv" using "elapsed-r":"ops/sec(inst)-r" title "machine=0, read" with linespoint,\
		 "baseline_overtime_stats_1.csv" using "elapsed-r":"ops/sec(inst)-r" title "machine=1, read" with linespoint,\
		 "baseline_overtime_stats_2.csv" using "elapsed-r":"ops/sec(inst)-r" title "machine=2, read" with linespoint,\
		 "baseline_overtime_stats_3.csv" using "elapsed-r":"ops/sec(inst)-r" title "machine=3, read" with linespoint,\
		 "baseline_overtime_stats_0.csv" using "elapsed-w":"ops/sec(inst)-w" title "machine=0, write" with linespoint,\
         "baseline_overtime_stats_1.csv" using "elapsed-w":"ops/sec(inst)-w" title "machine=1, write" with linespoint,\
         "baseline_overtime_stats_2.csv" using "elapsed-w":"ops/sec(inst)-w" title "machine=2, write" with linespoint,\
         "baseline_overtime_stats_3.csv" using "elapsed-w":"ops/sec(inst)-w" title "machine=3, write" with linespoint

set output "over_time_200.png"
set xrange [:200]
replot
