set terminal png
set output "zipfian_distro_limited_domain.png"
set xlabel "domain"
set ylabel "normalized frequency (sampled 10,000 times)"

plot "zipf1-1-maxInt64" using ($0 < 10000 ? $0 : 1/0):2 with linespoint
