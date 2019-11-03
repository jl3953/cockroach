#!/usr/bin/env python3

import argparse
import exp_lib
import lib
import operator
import os

FPATH = os.path.dirname(os.path.realpath(__file__))

def parse_config_file(config_file, variation_file):
	exp, _ = exp_lib.create_experiment(FPATH, config_file)
	variation_config = exp_lib.read_variation(variation_file)

	return exp, variation_config


def find_optimal_parameters(exp, variations, view):

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
				if not view:
					lib.run_bench(e)

			datum = {"concurrency": concurrency}
			datum.update(lib.accumulate_workloads_per_skew(exp, os.path.join(exp["out_dir"], "skew-0"))[0])
			data.append(datum)
			exp["out_dir"] = original_outdir

		max_concurrency = max(data, key=operator.itemgetter("ops/sec(cum)"))["concurrency"]
		concurrency = max_concurrency
		start = concurrency - step_size
		end = concurrency + step_size
		step_size = int(step_size / 2)

	data = sorted(data, key=lambda i: i["concurrency"])
	filename = lib.write_out_data(data, os.path.dirname(exp["out_dir"]))

	driver_node = "192.168.1.1" # usually
	csv_file = os.path.basename(os.path.dirname(exp["out_dir"])) + ".csv"
	cmd = "mv {0} /usr/local/temp/go/src/github.com/cockroachdb/cockroach/gnuplot/{1}".format(filename, csv_file)
	lib.call_remote(driver_node, cmd, "i like to move it move it")

	return max_concurrency


def run_single_trial(config_file, variation_file, report_params_args, view):

	set_params, variations = parse_config_file(config_file, variation_file)
	optimal_params = find_optimal_parameters(set_params, variations, view)
	print(optimal_params)
	# report_optimal_parameters(report_params_args)


def main():

	parser = argparse.ArgumentParser(description="find latency throughput graph")
	parser.add_argument('--view', action='store_true', help='only runs warmup for short testing')
	args = parser.parse_args()

	run_single_trial("lt_8clients.ini", "lt.ini", "", args.view)


if __name__ == "__main__":
	main()

