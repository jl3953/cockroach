#!/usr/bin/env python3

import configparser
import os
import json

def create_out_dir(fpath, logs_dirname, out_dirname):
	base_dir = os.path.join(fpath, "..")
	logs_dir = os.path.join(base_dir, logs_dirname)
	out_dir = os.path.join(logs_dir, out_dirname)

	return out_dir


def create_experiment(fpath, config_filename):

	config = configparser.ConfigParser()
	config.read(config_filename)

	exp = {
		"out_dir": create_out_dir(fpath, config["DEFAULT"]["LOGS_DIR"], config["DEFAULT"]["OUT_DIR"]),
		"cockroach_commit": config["cluster"]["cockroach_commit"],
		"workload_nodes": json.loads(config["cluster"]["workload_nodes"]),
		"hot_nodes": json.loads(config["cluster"]["hot_nodes"]),
		"warm_nodes": json.loads(config["cluster"]["warm_nodes"]),
		"benchmark": {
			"name": config["benchmark"]["name"],
			"init_args": {},
			"run_args": {
				"concurrency": int(config["benchmark"]["concurrency"]),
				"duration": int(config["benchmark"]["duration"]),
				"read_percent": int(config["benchmark"]["read_percent"]),
				"n_keys_per_statement": int(config["benchmark"]["n_keys_per_statement"]),
				"distribution": {
					"type": config["benchmark"]["distribution_type"],
					"params": {}
				}
			}
		}
	}

	skews = json.loads(config["benchmark"]["skews"])
	
	return exp, skews


if __name__ == "__main__":
	create_experiment(os.path.dirname(os.path.realpath(__file__)), "default.ini")
