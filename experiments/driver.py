#!/usr/bin/env python3

import argparse
import subprocess
import sys
import time

NODES = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]
EXE = "/usr/local/temp/go/src/github.com/cockroachdb/cockroach/cockroach"
STORE_DIR = "/data"


def call(cmd, err_msg):
    print(cmd)
    p = subprocess.run(cmd, universal_newlines=True, shell=True)
    if p.returncode:
        print(p.stderr)
        print(err_msg)
        sys.exit(1)
    else:
        return p.stdout


def call_remote(host, cmd, err_msg):
    cmd = "sudo ssh -t {0} '{1}'".format(host, cmd)
    return call(cmd, err_msg)


def kill_cockroach_node(host):
    cmd = '(! pgrep cockroach) || sudo killall -q cockroach'
    call_remote(host, cmd, 'Failed to kill cockroach node.')

    time.sleep(1)

    cmd = 'sudo rm -rf {0}'.format(os.path.join(STORE_DIR, "*"))
    call_remote(host, cmd, 'Failed to remove cockroach data.')


def start_cockroach_node(host, listen, join=None):
    cmd = ("{0} start --insecure --background"
           " --listen-addr={2}:26257 --store={1}") \
           .format(EXE, STORE_DIR, listen)

    if join:
        cmd = "{0} --join={1}:26257".format(cmd, join)

    return call_remote(host, cmd, "Failed to start cockroach node.")


def kill_cluster():
    for n in NODES:
        kill_cockroach_node(n)


def start_cluster():
    first = NODES[0]

    start_cockroach_node(first, first)
    for n in NODES[1:]:
        start_cockroach_node(n, n, join=first)


def main():	
    parser = argparse.ArgumentParser(description='Start and kill script for cockroach.')
    parser.add_argument('--kill', action='store_true', help='kills cluster, if specified')

    args = parser.parse_args()
    if args.kill:
        kill_cluster()
    else:
        kill_cluster()
        time.sleep(5)
        start_cluster()


if __name__ == "__main__":
    main()
