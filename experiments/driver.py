#!/usr/bin/env python3

import argparse
import lib
import logs
import os


FPATH = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.join(FPATH, "..")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OUT_DIR = os.path.join(LOGS_DIR, "kv-skew")
SKEWS = [1.000001, 1.00001, 1.0001, 1.001, 1.01, 1.1, 2]

EXP = {
    "out_dir": OUT_DIR,
    "cockroach_commit": "jenn-thisWillWork"
    "workload_nodes": [
       	{
            "ip": "192.168.1.1",
        },
    ],
    "hot_nodes": [],
    "warm_nodes": [
        {
            "ip": "192.168.1.2",
            "region": "newyork",
            "store": lib.STORE_DIR,
        },
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
        # {
        #     "ip": "192.168.1.5",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.6",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.7",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.8",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.9",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.10",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.11",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.12",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.13",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.14",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.15",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.16",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
        # {
        #     "ip": "192.168.1.17",
        #     "region": "singapore",
        #     "store": lib.STORE_DIR,
        # },
    ],
    "benchmark": {
        "name": "kv",
        "init_args": {
        },
        "run_args": {
            "concurrency": 128,
            "duration": 240,
            # "splits": 1000,
            # "drop": True,
            "read_percent": 90,
            # "n_statements_per_txn": 1,
            "n_keys_per_statement": 10,
            "distribution": {
                "type": "zipf",
                "params": {
                    # "skew": 0.5,
                },
            }
        }
    }
}


def main():
    parser = argparse.ArgumentParser(description='Start and kill script for cockroach.')
    parser.add_argument('--kill', action='store_true', help='kills cluster, if specified')
    parser.add_argument('--benchmark', action='store_true', help='runs specified benchmark')
    parser.add_argument('--logs', action='store_true', help='parses benchmark logs')

    args = parser.parse_args()
    if args.benchmark:
        exps = lib.vary_zipf_skew(EXP, SKEWS)
        for e in exps:
            if args.kill:
                lib.cleanup_previous_experiment(EXP)
                lib.init_experiment(EXP)

            lib.run_bench(e)

    if args.logs:
        logs.parse_kvbench_logs(OUT_DIR)


if __name__ == "__main__":
    main()
