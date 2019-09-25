set terminal png
set output "zipfian_distro.png"
set xlabel "domain (maxInt64)"
set ylabel "normalized frequency (%, 100M samples)"
set title "Cockroaach's Zipfian Distribution"

plot "zipf1-1-maxInt64" title "s=1.1" with linespoint,\
		 "zipf1-2-maxInt64" title "s=1.2" with linespoint,\
		 "zipf1-3-maxInt64" title "s=1.3" with linespoint,\
		 "zipf1-5-maxInt64" title "s=1.5" with linespoint,\
		 "zipf1-7-maxInt64" title "s=1.7" with linespoint,\
		 "zipf2-0-maxInt64" title "s=2.0" with linespoint

set output "zipfian_distro_lower_skews.png"
set title "Cockroach's Zipfian Distribution (lower skews)"
plot "zipf1-1-maxInt64" title "s=1.1" with linespoint,\
		 "zipf1-2-maxInt64" title "s=1.2" with linespoint,\
		 "zipf1-3-maxInt64" title "s=1.3" with linespoint

set output "zipfian_distro_comparison_skews.png"
set title "Cockroach's Zipfian Distribution (full skew range comparison)"
plot "zipf1-1-maxInt64" title "s=1.1" with linespoint,\
		 "zipf1-5-maxInt64" title "s=1.5" with linespoint,\
		 "zipf2-0-maxInt64" title "s=2.0" with linespoint
