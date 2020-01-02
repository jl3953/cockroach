#!/usr/bin/env python3

import argparse
import copy
import configparser
import datetime
import os
import sys

import bash_imitation


FPATH = os.path.dirname(os.path.realpath(__file__))


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
		Name of run's directory.
	"""

	overall_dir = bash_imitation.create_dir(location, generate_testrun_name(suffix))
	bash_imitation.create_dir(overall_dir, "graphs")
	bash_imitation.create_dir(overall_dir, "raw_out")
	bash_imitation.create_dir(overall_dir, "csv")


	return overall_dir



def main():

	parser = argparse.ArgumentParser(description="coordinator script for pipeline")
	parser.add_argument("config", help=".ini file with config params, params.ini")
	parser.add_argument("--stage", default="create_new_run",
			choices=["create_new_run"], help="which stage to start running at.")
	parser.add_argument("--run_single_stage", action="store_true",
			help="if set, do not continue after specified stage")
	parser.add_argument("--existing_directory", help="existing directory to use")

	args = parser.parse_args()

	# make all test directories
	human_tag = extract_human_tag(args.config)
	create_directories(os.path.join(FPATH, ".."), human_tag)

	return 0

if __name__ == "__main__":
	sys.exit(main())
