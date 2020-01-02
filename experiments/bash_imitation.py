#!/usr/bin/env python3

import os

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

