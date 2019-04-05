#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import time

# Constants
NODES = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]
REGIONS = ["newyork", "london", "tokyo"] # correspond directly to each node
EXE = "/usr/local/temp/go/src/github.com/cockroachdb/cockroach/cockroach"
STORE_DIR = "/data"

FPATH = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.join(FPATH, '..')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

EXP = {
    "out_dir": os.path.join(LOGS_DIR, "kv"),
    "coordinator": NODES[0],
    "benchmark": "kv",
    "duration": 30,
    "distribution": {
        "type": "zipf",
        "params": {
            "skew": 1
        }
    }
}


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


def start_cockroach_node(host, listen, region, join=None):
    cmd = ("{0} start --insecure --background"
           " --listen-addr={2}:26257 --store={1}"
	   " --locality=region={3}") \
           .format(EXE, STORE_DIR, listen, region)

    if join:
        cmd = "{0} --join={1}:26257".format(cmd, join)

    return call_remote(host, cmd, "Failed to start cockroach node.")


def kill_cluster():
    for n in NODES:
        kill_cockroach_node(n)

    time.sleep(10)


def start_cluster():
    first = NODES[0]

    start_cockroach_node(first, first, REGIONS[0])
    for n, r in zip(NODES[1:], REGIONS[1:]):
        start_cockroach_node(n, n, r, join=first)


def init_bench(name, args=""):
    cmd = "{0} workload init {1} {2}".format(EXE, name, args)
    return call(cmd, "Failed to initialize benchmark")


def run_bench(name, args=""):
    cmd = "{0} workload run {1} {2}".format(EXE, name, args)
    return call(cmd, "Failed to run benchmark")


def run_tpcc(config):
    ip = config["coordinator"]
    n_warehouses = config["warehouses"]

    name = "tpcc"
    args = "'postgresql://root@{0}:26257?sslmode=disable' --warehouses={1}".format(ip, n_warehouses)
    init_bench(name, args)

    duration = config["duration"]

    args = "'postgresql://root@{0}:26257?sslmode=disable' --warehouses={1} --ramp=30s --duration={2}s --split --scatter ".format(ip, n_warehouses, duration)
    run_bench(name, args)


def run_kvbench(config):
    ip = config["coordinator"]

    name = "kv"
    args = "'postgresql://root@{0}:26257?sslmode=disable'".format(ip)
    init_bench(name, args)

    duration = config["duration"]
    distribution = config["distribution"]
    dist_params = distribution["params"]

    args = "'postgresql://root@{0}:26257?sslmode=disable' --duration={1}s".format(ip, duration)
    if distribution["type"] == "zipf":
        args = "{0} --zipfian={1}".format(args, dist_params["skew"])

    out = run_bench(name, args)
    out_dir = config["out_dir"]
    path = os.path.join(out_dir, "out.txt")
    with open(path, "w") as f:
        f.write(out)


def save_params(exp_params, out_dir):
    params = {
        "exp_params": exp_params
    }

    path = os.path.join(out_dir, "params.json")
    with open(path, "w") as f:
        json.dump(params, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description='Start and kill script for cockroach.')
    parser.add_argument('--kill', action='store_true', help='kills cluster, if specified')
    parser.add_argument('--benchmark', nargs='+', choices=['kv', 'tpcc'],
		    	help='runs specified benchmark')

    args = parser.parse_args()
    if args.kill:
        kill_cluster()
    else:

        out_dir = EXP["out_dir"]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        save_params(EXP, out_dir)

        kill_cluster()
        start_cluster()
        
        if args.benchmark:
            for bench in args.benchmark:
                if bench == "tpcc":
                    run_tpcc(bench)
                elif bench == "kv":
                    run_kvbench(bench)

if __name__ == "__main__":
    main()
