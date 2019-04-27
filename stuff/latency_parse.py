#!/usr/bin/env python3

import argparse
import collections
import datetime
import enum
import numpy as np
import pandas
import statistics


def parse_keys(token):
    keys = [int(i) for i in token.strip(" keys:[[").strip("]]").split()]
    return keys


def parse_elapsed(token):
    elapsed = token.strip(" elapsed:[").strip().strip("]")
    print(elapsed)
    try:
        return float(elapsed.strip("s")) * 1000
    except:
        return float(elapsed.strip("ms"))


def parse_line_and_modify_dict(line, dict_to_mod):
    tokens = line.split(',')
    keys = parse_keys(tokens[1])
    elapsed = parse_elapsed(tokens[2])

    for k in keys:
        dict_to_mod[k].append(elapsed)


def calculate_stats(latencies):
    result = "avg(latency)={0}".format(np.mean(latencies))
    result += ", med(latency)={0}".format(np.median(latencies))
    result += ", p99(latency)={0}".format(np.percentile(latencies, 0.99))
    return result


def main():
    parser = argparse.ArgumentParser(description='Parses out latencies')
    parser.add_argument('logfile', type=str, help="Logfile to parse")
    parser.add_argument("--outfile", type=str, default="latencies.csv", help="outfile to write to")

    args = parser.parse_args()

    keys_to_latencies = collections.defaultdict(list)
    with open(args.logfile, 'r') as f:
        for line in f:
            parse_line_and_modify_dict(line, keys_to_latencies)
    
    with open(args.outfile, 'w') as f:
        for key, latencies in keys_to_latencies.items():
            f.write(str(key) + ", " + calculate_stats(latencies) + "\n")

    return 0


if __name__ == "__main__":
    main()
        

