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


def git_current_commit_hash():

	""" Returns current commit hash on current branch."""


	hash_byte = subprocess.check_output("git rev-parse HEAD".split())
	git_commit = hash_byte.decode("utf-8").strip()

	return git_commit


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
