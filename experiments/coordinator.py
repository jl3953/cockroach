#!/usr/bin/env python3

import argparse
import copy
import configparser
import datetime
import enum
import os
import sys

import bash_imitation
import lib


FPATH = os.path.dirname(os.path.realpath(__file__))
LT_EXECUTABLE = os.path.join(FPATH, "lt_driver.py")


class Stage(enum.Enum):
	CREATE_NEW_DIRS = "create_new_dirs"
	METADATA = "metadata"
	LATENCY_THROUGHPUT = "latency_throughput"

	def __str__(self):
		return self.value

	@staticmethod
	def next(stage):
		if stage == Stage.CREATE_NEW_DIRS:
			return Stage.METADATA
		elif stage == Stage.METADATA:
			return Stage.LATENCY_THROUGHPUT


def extract_human_tag(config_file):

	""" Reads the human tag from the config file.

	Args:
		config_file (str): .ini file
	
	Returns:
		human tag
	"""

	config = configparser.ConfigParser()
	config.read(config_file)

	return config["DEFAULT"]["LOGS_DIR"]


def generate_testrun_name(suffix):

	""" Creates a test run directory's name in the format
	test_<timestamp>_<suffix>.

	Args:
		suffix (str): human readable tag
	
	Returns:
		generated name.
	"""

	timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
	name = "test_{0}_{1}".format(timestamp, suffix)

	return name


def create_directories(location, suffix):

	""" Creates the run's directories.

	Args:
		suffix (str): appending dir name with a human readable tag.
	
	Returns:
		Name of all created directories
	"""

	overall_dir = bash_imitation.create_dir(location, generate_testrun_name(suffix))
	graph_dir = bash_imitation.create_dir(overall_dir, "graphs")
	raw_out_dir = bash_imitation.create_dir(overall_dir, "raw_out")
	csv_dir = bash_imitation.create_dir(overall_dir, "csv_files")


	return overall_dir, graph_dir, raw_out_dir, csv_dir


def reconstruct_directories(location, existing_directory):

	""" Reconstructs the structure of the existing directory and returns
	the inner directories.

	Args:
		location (str): location of existing directory
		existing_directory (str): name of existing directory

	Return:
		Name of all directories.
	"""

	overall_dir = os.path.join(location, existing_directory)
	graph_dir = os.path.join(overall_dir, "graphs")
	raw_out_dir = os.path.join(overall_dir, "raw_out")
	csv_dir = os.path.join(overall_dir, "csv_files")

	return overall_dir, graph_dir, raw_out_dir, csv_dir


def copy_and_create_metadata(location, config_file):

	""" Copies config file as params.ini, creates a metadata file of
	current git hash.

	Args:
		location (str): location in which all files are copied / created
		config_file (str): config file to be copied.
	
	Return: 
		None.
	"""

	# copy parameter file
	cmd = "cp {0} {1}".format(config_file, os.path.join(location, "params.ini"))
	lib.call(cmd, "could not copy params file.")

	# create git hash file
	with open(os.path.join(location, "git_commit_hash.txt"), "w") as f:
		git_commit_hash = bash_imitation.git_current_commit_hash()
		f.write(git_commit_hash)


def call_latency_throughput(location, baseline_file, lt_file, params_dir,
		csv_dir, raw_out_dir):

	""" Calls the latency throughput script.

	Args:
		location (str): absolute path of location directory.
		baseline_file (str): original params config file, abs path
		lt_file (str): latency throughput params config, abs path
		params_dir(str): directory in which output param file lives
		csv_dir(str): directory in which csv file will live
		raw_out_dir (str): dir in which generated logs live
	
	Returns:
		None.
	"""

	# call the script
	cmd = "{0} {1} {2} {3} {4} --driver_node localhost".format(
			LT_EXECUTABLE, baseline_file, lt_file, params_dir, csv_dir)
	lib.call(cmd, "lt_driver script failed")

	# move the generated logs
	src_logs = exp_lib.find_log_dir(FPATH, baseline_file)
	dest = os.path.join(raw_out_dir, "lt_logs")
	bash_imitation.move_logs(src_logs, dest)


def main():

	parser = argparse.ArgumentParser(description="coordinator script for pipeline")
	parser.add_argument("config", help=".ini file with config params, params.ini")
	parser.add_argument("lt_config", help=".ini file with latency throughput params")
	parser.add_argument("--stage", type=Stage, default=Stage.CREATE_NEW_DIRS, 
			choices=[Stage.CREATE_NEW_DIRS, Stage.METADATA, Stage.LATENCY_THROUGHPUT],
			help="which stage to start running at. Useful for testing.")
	parser.add_argument("--run_single_stage", action="store_true",
			help="if set, do not continue after specified stage. Useful for testing.")
	parser.add_argument("--existing_directory",
			help="existing directory to use. Useful for testing.")

	args = parser.parse_args()
	args.config = os.path.join(FPATH, args.config) # replace with abs path
	args.lt_config = os.path.join(FPATH, args.lt_config)

	if args.stage is not Stage.CREATE_NEW_DIRS and not args.existing_directory:
		print("You must provide an existing test run directory with this stage.")
		parser.print_help()
		return -1

	# pipeline
	stage = args.stage
	overall_dir, graph_dir, raw_out_dir, csv_dir = None, None, None, None

	if stage == Stage.CREATE_NEW_DIRS:
		human_tag = extract_human_tag(args.config)
		overall_dir, graph_dir, raw_out_dir, csv_dir = create_directories(
				os.path.join(FPATH, ".."), human_tag)
		if args.run_single_stage:
			return 0
		stage = Stage.next(stage)
	else:
		overall_dir, graph_dir, raw_out_dir, csv_dir = reconstruct_directories(
				os.path.join(FPATH, ".."), args.existing_directory)

	if stage == Stage.METADATA:
		copy_and_create_metadata(overall_dir, args.config)
		if args.run_single_stage:
			return 0
		stage = Stage.next(stage)

	if stage == stage.LATENCY_THROUGHPUT:
		call_latency_throughput(overall_dir, args.config, args.lt_config,
				overall_dir, csv_dir, raw_out_dir)

	return 0

if __name__ == "__main__":
	sys.exit(main())
