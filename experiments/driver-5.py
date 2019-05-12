#!/usr/bin/env python3

import argparse
import lib
import os


FPATH = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.join(FPATH, "..")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

EXP = {
    "out_dir": os.path.join(LOGS_DIR, "kv"),
    "cockroach_commit": "jenn-no-wound",
    "workload_nodes": [
        {
            "ip": "192.168.1.1",
        },
    ],
    "hot_nodes": [
        {
            "ip": "192.168.1.2",
            "region": "newyork",
            "store": lib.STORE_DIR,
        },
    ],
    "warm_nodes": [
        {
            "ip": "192.168.1.3",
            "region": "london",
            "store": lib.STORE_DIR,
        },
        {
            "ip": "192.168.1.4",
            "region": "tokyo",
            "store": lib.STORE_DIR,
        },
        {
            "ip": "192.168.1.5",
            "region": "singapore",
            "store": lib.STORE_DIR,
        },
    ],
    "benchmark": {
        "name": "kv",
        "init_args": {
        },
        "run_args": {
            "n_clients": 512,
            "duration": 30,
            "hot_keys": [1],
            "read_percent": 95,
        }
    }
}


def main():
    parser = argparse.ArgumentParser(description='Start and kill script for cockroach.')
    parser.add_argument('--kill', action='store_true', help='kills cluster, if specified')
    parser.add_argument('--benchmark', action='store_true', help='runs specified benchmark')

    parser.add_argument("--runbenchmark", action="store_true", help="actually runs benchmark")

    args = parser.parse_args()
    if args.runbenchmark:
        lib.run_bench(EXP)
        return 0

    if args.kill:
        lib.cleanup_previous_experiment(EXP)
    else:

        out_dir = EXP["out_dir"]
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        lib.save_params(EXP, out_dir)

        lib.cleanup_previous_experiment(EXP)
        lib.init_experiment(EXP)

        if args.benchmark:
            lib.run_bench(EXP)


if __name__ == "__main__":
    main()
