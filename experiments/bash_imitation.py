#!/usr/bin/env python3

import os
import subprocess

import lib

def create_dir(location, dir_name):

	""" Creates a directory at location.

	Args:
		location (str): absolute path name, directory location of new dir
		dir_name (str): name of new directory.
	
	Returns:
		Absolute path of new directory.
	"""

	new_dir = os.path.join(location, dir_name)
	lib.call_remote("localhost", "mkdir {0}".format(new_dir), "unable to make new dir")

	return new_dir


def git_commit_hash():

	""" Returns current commit hash on current branch.
	
	Args:
		None.
	
	Returns:
		Commit hash (str)
	"""


	hash_byte = subprocess.check_output("git rev-parse HEAD".split())
	git_commit = hash_byte.decode("utf-8").strip()

	return git_commit


def git_submodule_commit_hash(submodule):

	""" Returns current commit hash of submodule.

	Args:
		submodule (str): name of submodule
	
	Returns:
		commit hash.
	"""

	hash_byte = subprocess.check_output("git rev-parse @:{0}".format(submodule).split())
	commit = hash_byte.decode("utf-8").strip()

	return commit


def move_logs(src_logs, dest_logs):

	""" Moves logs from src to dest.

	Args:
		src_logs (str)
		dest_logs (str)

	Returns:
		None.
	"""

	lib.call_remote("localhost", "mv {0} {1}".format(src_logs, dest_logs),
			"unable to move logs")


def gnuplot(gnuplot_script, input_csv, output_graph_dir, trial=None):

	""" Calls gnuplot script on input csv and dumps generated graphs
	in output_graph_dir.

	Args:
		gnuplot_script (str): abs path of gnuplot script
		input_csv (str): abs path of input csv file
		output_graph_dir (str): abs path of directory where output graphs
			are dumped.
		trial (int): the trial that this plot belongs to.

	Returns:
		None.
	"""

	if trial:
		lib.call("gnuplot -c {0} {1} {2} {3}".format(gnuplot_script, input_csv,
					output_graph_dir, trial), "gnuplot bash imitation trial failed")
	else:
		lib.call("gnuplot -c {0} {1} {2}".format(gnuplot_script, input_csv,
					output_graph_dir), "gnuplot bash imitiation failed")

