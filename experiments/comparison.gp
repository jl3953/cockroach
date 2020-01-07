set terminal png
set xlabel "zipfian constant"
set boxwidth 0.01

set ylabel "throughput (txn/sec)"
set output "comparison.png"
plot ARG1 using "skew":"box_min":"whisker_min":"whisker_high":"box_high" notitle with candlesticks lt -1 lw 2 whiskerbars,\
		 "" using "skew":"median":"median":"median":"median" with candlesticks lt -1 lw 2 notitle,\
		 "" using "skew":"median" title "removed hot key from six" with linespoint,\
		 ARG2 using "skew":"box_min":"whisker_min":"whisker_high":"box_high" title "five keys" with candlesticks lt -1 lw 2 whiskerbars,\
		 "" using "skew":"median":"median":"median":"median" with candlesticks lt -1 lw 2 notitle,\
		 "" using "skew":"median" with linespoint notitle,\
		ARG3 using "skew":"box_min":"whisker_min":"whisker_high":"box_high" title "six keys" with candlesticks lt -1 lw 2 whiskerbars,\
		 "" using "skew":"median":"median":"median":"median" with candlesticks lt -1 lw 2 notitle,\
		 "" using "skew":"median" with linespoint notitle
