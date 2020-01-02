#!/usr/bin/env python3

import argparse
import exp_lib
import lib
import operator
import os
import plotlib

FPATH = os.path.dirname(os.path.realpath(__file__))

def parse_config_file(baseline_file, lt_file):
	exp, _ = exp_lib.create_experiment(FPATH, baseline_file)
	variation_config = exp_lib.read_variation(lt_file)

	return exp, variation_config


def find_optimal_concurrency(exp, variations, log_output_path, is_view_only):

	""" Returns:
	Max concurrency, csv data
	"""

	start = variations["variation"]["concurrency"][0]
	step_size = variations["variation"]["step_size"]
	end = variations["variation"]["concurrency"][1] + step_size

	data = []
	max_concurrency = -1
	while step_size > 0:
		for concurrency in range(start, end, step_size):
			exp["benchmark"]["run_args"]["concurrency"] = concurrency
			original_outdir = exp["out_dir"]
			exp["out_dir"] += "_" + str(concurrency)
			skew_list_with_one_item = [variations["variation"]["skew"]]
			exps = lib.vary_zipf_skew(exp, skew_list_with_one_item)

			for e in exps:
				lib.cleanup_previous_experiment(exp)
				lib.init_experiment(exp)
				lib.warmup_cluster(e)
				if not is_view_only:
					lib.run_bench(e)

			datum = {"concurrency": concurrency}
			datum.update(plotlib.accumulate_workloads_per_skew(exp, os.path.join(exp["out_dir"], "skew-0"))[0])
			data.append(datum)
			exp["out_dir"] = original_outdir

		max_concurrency = max(data, key=operator.itemgetter("ops/sec(cum)"))["concurrency"]
		concurrency = max_concurrency
		start = concurrency - step_size
		end = concurrency + step_size
		step_size = int(step_size / 2)

	
	return max_concurrency, data


def report_csv_data(csv_data, args):

	""" Outputs csv data to file storage.

	Args:
		csv_data
		args (dict): metadata for path of csv file, driver nodes, etc.

	Returns:
		None.

	"""
	data = sorted(csv_data, key=lambda i: i["concurrency"])
	filename = plotlib.write_out_data(data, args["csv_output_path"], "lt.csv")


def report_optimal_parameters(max_concurrency, args):

	""" Outputs optimal concurrency to file storage.

	Args:
		max_concurrency (int)
		args (dict): metadata for path of file, etc.

	Returns:
		None.

	"""

	filename = os.path.join(args["params_output_path"], "optimal_params.ini")
	with open(filename, "w") as f:
		f.write("max_concurrency: " + str(max_concurrency) + "\n")

	

def move_log_output(baseline_file, log_output_path, driver_node):

	""" Moves log files from original location to given location.

	Args:
		baseline_file (str): name of baseline config file.
		log_output_path (str): path of new location.
		driver_node (str)

	Returns:
		None.

	"""

	log_dir = exp_lib.find_log_dir(FPATH, baseline_file)
	
	cmd = "mv {0} lt_output; mv lt_output {1}".format(log_dir, log_output_path)
	lib.call_remote(driver_node, cmd, "mv lt_output err")


def run_single_trial(find_concurrency_args, report_params_args,
		report_csv_args, is_view_only):

	print(find_concurrency_args)
	set_params, variations = parse_config_file(find_concurrency_args["baseline_file"], 
			find_concurrency_args["lt_file"])
	max_concurrency, csv_data = find_optimal_concurrency(set_params,
			variations, find_concurrency_args["log_output_path"], is_view_only)
	# move_log_output(find_concurrency_args["baseline_file"],
	# 		find_concurrency_args["log_output_path"], find_concurrency_args["driver_node"])
	report_csv_data(csv_data, report_csv_args)
	report_optimal_parameters(max_concurrency, report_params_args)
	print(max_concurrency)


def main():

	parser = argparse.ArgumentParser(description="find latency throughput graph")
	parser.add_argument('baseline_file', help="baseline_file, original param file")
	parser.add_argument('lt_file', help="lt_file, for example lt.ini")
	parser.add_argument('log_output_path', help='path of log output files')
	parser.add_argument('params_output_path', help="path of output param files")
	parser.add_argument('csv_output_path', help="path of output csv file")
	parser.add_argument('--driver_node', default='192.168.1.1')
	parser.add_argument('--is_view_only', action='store_true', 
			help='only runs warmup for short testing')
	args = parser.parse_args()

	find_concurrency_args = {
		"baseline_file": args.baseline_file,
		"lt_file": args.lt_file,
		"log_output_path": args.log_output_path,
		"driver_node": args.driver_node,
	}
	report_csv_args = {
		"csv_output_path": args.csv_output_path,
	}

	report_params_args = {
		"params_output_path": args.params_output_path,
	}

	run_single_trial(find_concurrency_args, report_params_args, report_csv_args, 
			args.is_view_only)


if __name__ == "__main__":
	main()

