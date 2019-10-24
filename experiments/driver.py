#!/usr/bin/env python3

import argparse
import exp_lib
import lib
import logs
import os


FPATH = os.path.dirname(os.path.realpath(__file__))
EXP, SKEWS = exp_lib.create_experiment(FPATH, "default.ini")
CONFIG_LIST = [
	# "single_key_85.ini",
	# "single_key_87.ini",
	# "single_key_89.ini",
	# "single_key_90.ini",
	"single_key_91.ini",
	# "single_key_94.ini",
	# "single_key_96.ini",
	# "single_key_98.ini",
	# "single_key_100.ini",
	# "single_key_102.ini",
	# "single_key_108.ini",
	# "single_key_124.ini",
	"single_key_56.ini",
	"single_key_64.ini",
	# "single_key_72.ini",
	# "single_key_80.ini",
	# "single_key_96.ini",
	]


def run_experiment(exp, skews, view=False):

	exps = lib.vary_zipf_skew(exp, skews)
	for e in exps:
		lib.cleanup_previous_experiment(exp)
		lib.init_experiment(exp)
		lib.warmup_cluster(e)
		if not view:
			lib.run_bench(e)

	if not view:
		lib.gnuplot(exp, skews)


def main():
	
	parser = argparse.ArgumentParser(description='Start script for cockroach.')
	parser.add_argument('--start', action='store_true', help='starts, or restarts, the cluster.')
	parser.add_argument('--obliterate', action='store_true', help='kills cluster and cleans up, if specified')
	parser.add_argument('--benchmark', action='store_true', help='runs specified benchmark, assumes db is already started')
	parser.add_argument('--override', action='store_true', help='overrides parameters according to override.ini,'
			' only valid when running benchmark')
	parser.add_argument('--view', action='store_true', help='only runs warmup for short testing')
	# parser.add_argument('--logs', action='store_true', help='parses benchmark logs')
	
	args = parser.parse_args()
	if args.obliterate:
		lib.cleanup_previous_experiment(EXP)
	elif args.benchmark:
		for config_file in CONFIG_LIST:
			exp, skews = exp_lib.create_experiment(FPATH, config_file, args.override)
			run_experiment(exp, skews, args.view)
	elif args.start:
		lib.cleanup_previous_experiment(EXP)
		lib.init_experiment(EXP)
	else:
		parser.print_help()

if __name__ == "__main__":
    main()
