#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import time

NODES = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]
EXE = "/usr/local/temp/go/src/github.com/cockroachdb/cockroach/cockroach"
STORE_DIR = "/data"

# TPCC
DURATION_S = 30
N_WAREHOUSES = 100


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

    time.sleep(10)


def start_cluster():
    first = NODES[0]

    start_cockroach_node(first, first)
    for n in NODES[1:]:
        start_cockroach_node(n, n, join=first)


def init_bench(name, args=""):
    cmd = "{0} workload init {1} {2}".format(EXE, name, args)
    return call(cmd, "Failed to initialize benchmark")


def run_bench(name, args=""):
    cmd = "{0} workload run {1} {2}".format(EXE, name, args)
    return call(cmd, "Failed to run benchmark")


def run_tpcc(cr_ip, duration_s, n_warehouses):
    name = "tpcc"
    args = "--warehouses={0} 'postgresql://root@{1}:26257?sslmode=disable'".format(n_warehouses, cr_ip)
    init_bench(name, args)

    args = "--warehouses={0} --ramp=30s --duration={1}s --split --scatter 'postgresql://root@{2}:26257?sslmode=disable'".format(n_warehouses, duration_s, cr_ip)
    run_bench(name, args)


def main():
    parser = argparse.ArgumentParser(description='Start and kill script for cockroach.')
    parser.add_argument('--kill', action='store_true', help='kills cluster, if specified')

    args = parser.parse_args()
    if args.kill:
        kill_cluster()
    else:
        kill_cluster()

        run_tpcc(NODES[0], DURATION_S, N_WAREHOUSES)
        start_cluster()


if __name__ == "__main__":
    main()
