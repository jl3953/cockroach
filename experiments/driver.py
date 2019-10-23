#!/usr/bin/env python3

import argparse
import exp_lib
import lib
import logs
import os


FPATH = os.path.dirname(os.path.realpath(__file__))
EXP, SKEWS = exp_lib.create_experiment(FPATH, "default.ini")

def main():
	
	parser = argparse.ArgumentParser(description='Start script for cockroach.')
	parser.add_argument('--start', action='store_true', help='starts, or restarts, the cluster.')
	parser.add_argument('--obliterate', action='store_true', help='kills cluster and cleans up, if specified')
	parser.add_argument('--benchmark', action='store_true', help='runs specified benchmark, assumes db is already started')
	# parser.add_argument('--logs', action='store_true', help='parses benchmark logs')
	
	args = parser.parse_args()
	if args.obliterate:
		lib.cleanup_previous_experiment(EXP)
	elif args.benchmark:
		exps = lib.vary_zipf_skew(EXP, SKEWS)
		for e in exps:
			lib.cleanup_previous_experiment(EXP)
			lib.init_experiment(EXP)
			lib.warmup_cluster(e)
			lib.run_bench(e)
		lib.gnuplot(EXP, SKEWS)
	elif args.start:
		lib.cleanup_previous_experiment(EXP)
		lib.init_experiment(EXP)
	else:
		parser.print_help()

if __name__ == "__main__":
    main()
