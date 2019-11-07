#!/usr/bin/env python3

import argparse
import exp_lib
import lib
import logs
import os
import configparser


FPATH = os.path.dirname(os.path.realpath(__file__))
EXP, SKEWS = exp_lib.create_experiment(FPATH, "default.ini")
CONFIG_LIST = [
	# "new_zipfian_read95.ini",
	"new_zipfian_write.ini"
	]


def run_experiment(exp, skews, view=False):

	exps = lib.vary_zipf_skew(exp, skews)
	# for e in exps:
	# 	lib.cleanup_previous_experiment(exp)
	# 	lib.init_experiment(exp)
	# 	lib.warmup_cluster(e)
	# 	if not view:
	# 		lib.run_bench(e)

	if not view:
		lib.gnuplot(exp, skews)


def create_trial_outdir(config_filename, i):

	config = configparser.ConfigParser()
	config.read(config_filename)
	logs_dir = config["DEFAULT"]["LOGS_DIR"]

	if i > 0:
		logs_dir += str(i)

	return exp_lib.create_out_dir(FPATH, logs_dir, config["DEFAULT"]["OUT_DIR"])


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
			for i in range(exp["trials"]):
				exp["out_dir"] = create_trial_outdir(config_file, i)
				run_experiment(exp, skews, args.view)

	elif args.start:
		lib.cleanup_previous_experiment(EXP)
		lib.init_experiment(EXP)
	else:
		parser.print_help()

if __name__ == "__main__":
    main()
