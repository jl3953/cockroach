#!/usr/bin/env python3

import argparse
import collections
import datetime
import enum
import numpy as np
import pandas
import statistics

class Action(enum.Enum):
    SPANLATCH_WAIT = 0
    ACCESS_SUCCESS = 1
    UNCOMMITTED_INTENT = 2
    NEWER_COMMITTED_VALUE = 3
    TXNQUEUE_WAIT = 4


def parse_key(k):

    key = k
    test = k.split()
    if len(test) > 1:
       key = test[3].split('=')[1]

    components = key.split('/')
    if len(components) < 6:
        return key

    result = "/".join(components[0:4] + components[-2:])
    try:
        _ = int(components[-2])
    except:
        result = "/".join(components[0:4] + components[-1:])
    return result

def parse_typ(typ):

    if typ == "latchRelease":
        return Action.SPANLATCH_WAIT
    elif typ == "write_success":
        return Action.ACCESS_SUCCESS
    elif typ == "uncommitted_write_intent":
        return Action.UNCOMMITTED_INTENT
    elif typ == "newer_committed_value":
        return Action.NEWER_COMMITTED_VALUE
    elif typ == "txn_wait_queue":
        return Action.TXNQUEUE_WAIT


def parse_val(val, typ=Action.SPANLATCH_WAIT):

    if typ != Action.SPANLATCH_WAIT and typ != Action.TXNQUEUE_WAIT:
        return val

    try:
        return float(val.strip("ms"))
    except:
        return float(val[:-3]) / 10e3

def parse_ts(ts):
    dt = datetime.datetime.strptime(ts, "%H:%M:%S.%f")
    dt.replace(year=2019, month=4, day=27)
    return dt
        

def parse_line(line):

    tokens = line.split()
    timestamp = parse_ts(tokens[1])

    tokens = tokens[6:]

    payload = " ".join(tokens)
    tokens = payload.split("],")

    key = parse_key(tokens[0].split(':[')[1].strip(']').strip('['))
    typ = parse_typ(tokens[1].split(':[')[1].strip(']').strip('['))

    if len(tokens) > 2:
        val = parse_val(tokens[2].split(':[')[1].strip(']').strip('['))
    else:
        val = None

    return key, {
            "timestamp": timestamp, 
            "typ": typ, 
            "val": val
            }


def calculate_stats(extracts):

    df = pandas.DataFrame.from_records(extracts)
    for name, group in df.groupby(pandas.Grouper(key="timestamp", freq="1s"):


    print(value)

def main():

    parser = argparse.ArgumentParser(description='Parses out features for prediction contention')
    parser.add_argument('logfiles', nargs="+", help="Logfiles to be parsed")

    args = parser.parse_args()

    keys_to_features = collections.defaultdict(list)
    for logfile in args.logfiles:
        with open(logfile, 'r') as f:
            for line in f:
                key, feature_dict = parse_line(line)
                keys_to_features[key].append(feature_dict)


    for key, value in keys_to_features.items():
        print(key)
        calculate_stats(value)


    return 0


if __name__ == "__main__":
    main()
