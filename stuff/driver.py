#!/usr/bin/env python3

import collections
import datetime
import os
import subprocess
import sys

# constants
COCKROACH_DIR = "~/go/src/github.com/cockroachdb/cockroach"
EXE = os.path.join(COCKROACH_DIR, "cockroach")
STORE_DIR = "/data"
LOGS_DIR = os.path.join(STORE_DIR, 'logs')
GREP_PHRASE = "JENNDEBUG"

NODES = ["node-1", "node-2", "node-3", "node-4"]


def make_logfile_name(name, timestamp, *argv):

    """ Makes a logfile name.

    Args:
        name (str): name of logfile.
        timestamp (datetime.datetime obj): timestamp to append.
        argv: any other arguments to append to logfile.

    Returns:
        a logfile name.
    """

    result = name
    for arg in argv:
        result += "_" + str(arg)
    result += "." + timestamp.strftime("%Y%m%d_%H%M%S")
    result += ".log"

    return os.path.join(LOGS_DIR, result)


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


def parse_ts(ts):
    dt = datetime.datetime.strptime(ts, "%H:%M:%S.%f")
    dt.replace(year=2019, month=4, day=27)
    return dt


def execute_round(a, dur, logfile):

    """ Runs a bound of the kv benchmark.

    Args:
        a (double): skew alpha
        dur (int): duration on which to run round (sec).
        logfile (str): logfile to which to log results.

    Returns:
        begin_ts, end_ts

    """
    begin_ts = datetime.datetime.now()
    cmd = " ".join(EXE, "workload run kv --zipfian --skew {0} --duration {1}s &> {2}".format(
        a, dur, logfile))
    call(cmd, "failed to run kv benchmark")
    end_ts = datetime.datetime.now()

    return begin_ts, end_ts


def parse_latencies(logfile):
    """ Parses the training logfile for latencies.
    
    Args:
        logfile (str): logfile on which to parse.

    Returns:
        keys to a list of timestamps and latencies (collections.defaultdict)
    """

    cmd = "cat {0} | grep {1} &> {2}".format(logfile, GREP_PHRASE, logfile + ".tmp")
    call(cmd, "parse latencies failed")

    def parse(line):
        tokens = line.split(',')

        def parse_keys(token):
            keys = [i for i in token.strip(" keys:[[").strip("]]").split()]
            return keys

        def parse_elapsed(token):
            elapsed = token.strip(" elapsed:[").strip().strip("]")
            try:
                return float(elapsed.strip("s")) * 1000
            except:
                return float(elapsed.strip("ms"))

        keys = parse_keys(tokens[1])
        elapsed = parse_elapsed(tokens[2])

        tokens = line.split()
        timestamp = parse_ts(tokens[1])

        result = []
        for k in keys:
            result.append((k, timestamp, elapsed))

        return result

    keys_to_latencies = collections.defaultdict(list)
    with open(logfile, 'r') as f:
        for line in f:
            # key, timestamp, latency
            tuples = parse(line)
            for key, ts, latency in tuples:
                # print(key)
                keys_to_latencies[key].append({
                    "timestamp": ts,
                    "latency": latency
                })

    return keys_to_latencies


def parse_training_features(begin, end):

    """ Parses training features per node.

    Args:
        begin (datetime.datetime object): begin timestamp
        end (datetime.datetime object): end timestamp

    Returns:
        keys to features (collection.dict(list))

    """

    logs = []
    for ip in NODES:

        # composing log file
        temp_log = make_logfile_name("temp", begin, ip)
        logs.append(temp_log)

        # grepping for lines between two timestamps
        awk = "awk -v \"from={0}\" -v \"to={1}\" -F ' ' '{ if ($2 >= from && $2 <= to) print }'".format(
            begin.strftime("%H:%M:%S"), end.strftime("%H:%M:%S"))

        # filter for grep phrase and redirect all output to composed logfile
        filter_cmd = "cat /data/logs/cockroach.log | {0} | grep {1} &> {2};".format(
            awk, GREP_PHRASE, temp_log)
        call_remote(ip, filter_cmd, "woops, fucked")

        # bring that file over to this machine
        scp = "scp {0}:{1} .".format(ip, temp_log)
        call(scp, "scp fucked")

    feature_log = make_logfile_name("features", begin)
    call("sort temp* &> {0}".format(feature_log), "that fucked too")


    def parse(line):

        tokens = line.split()
        timestamp = parse_ts(tokens[1])

        tokens = tokens[6:]

        payload = " ".join(tokens)
        tokens = payload.split("],")

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
            return result.split("/")[-2]

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
            elif typ == "ts_bumped_for_read":
                return Action.TS_BUMPED_READ


        def parse_val(val, typ=Action.SPANLATCH_WAIT):

            if typ != Action.SPANLATCH_WAIT and typ != Action.TXNQUEUE_WAIT:
                return val

            try:
                return float(val.strip("ms"))
            except:
                return float(val[:-3]) / 10e3


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

    keys_to_features = collections.defaultdict(list)
    with open(feature_log, 'r') as f:
        for line in f:
            key, feature_dict = parse(line)
            keys_to_features[key].append(feature_dict)

    return keys_to_features



def run_iteration(a, train_dur, inf_dur):

    """ Runs an iteration of tests.

    Args:
        a (double): skew alpha
        train_dur (int): duration on which to train, sec
        inf_dur(int): duration on which to run inference round, sec.

    Returns:
        training R^2, prediction R^2.
    """

    # logfiles
    ts = datetime.datetime.now()
    train_logfile = make_logfile_name("train", ts, a, train_dur, inf_dur)
    inf_logfile = make_logfile_name("inf", ts, a, train_dur, inf_dur)

    # run training round
    begin, end = execute_round(a, train_dur, train_logfile)
    train_latencies = parse_latencies(train_logfile)
    train_features = parse_training_features(begin, end)
    model = train_model(train_features, train_latencies)
    train_r2 = score_mode(model, train_features, train_latencies)

    # run inference round
    begin, end = execute_round(inf_dur, inf_logfile)
    inf_latencies = parse_inference(inf_logfile)
    inf_features = parse_inference(begin, end)
    inf_r2 = score_model(model, inf_features, inf_latencies)

    return train_r2, inf_r2
