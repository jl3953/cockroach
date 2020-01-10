#!/usr/bin/env python3

def create_out_dir(fpath, logs_dirname):
	base_dir = os.path.join(fpath, "..")
	logs_dir = os.path.join(base_dir, logs_dirname)

	return logs_dir


def create_experiment(fpath, config_filename):

	config = configparser.ConfigParser()
	config.read(config_filename)

	exp = {
		"out_dir": create_out_dir(fpath, config["DEFAULT"]["LOGS_DIR"]),
		"cockroach_commit": config["cluster"]["cockroach_commit"],
		"workload_nodes": json.loads(config["cluster"]["workload_nodes"]),
		"hot_nodes": json.loads(config["cluster"]["hot_nodes"]),
		"warm_nodes": json.loads(config["cluster"]["warm_nodes"]),
		"benchmark": {

