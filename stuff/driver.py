#!/usr/bin/env python3

import collections
import datetime
import enum
import os
import pandas
import sklearn.linear_model
import subprocess
import sys

# constants
COCKROACH_DIR = "~/go/src/github.com/cockroachdb/cockroach"
EXE = os.path.join(COCKROACH_DIR, "cockroach")
STORE_DIR = "/data"
LOGS_DIR = os.path.join(STORE_DIR, 'logs')
GREP_PHRASE = "JENNDEBUG"

NODES = [{
            "node": "node-1",
            "ip": "192.168.1.2",
        }, {
            "node": "node-2",
            "ip": "192.168.1.3",
        }, {
            "node": "node-3",
            "ip": "192.168.1.4"
        }, {
            "node": "node-4",
            "ip": "192.168.1.5"
        }]


class Action(enum.Enum):
    SPANLATCH_WAIT = 0
    ACCESS_SUCCESS = 1
    UNCOMMITTED_INTENT = 2
    NEWER_COMMITTED_VALUE = 3
    TXNQUEUE_WAIT = 4
    TS_BUMPED_READ = 5


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

def call_with_redirect(cmd, err_msg, logfile):
    print(cmd)
    with open(logfile, "w") as out:
        p = subprocess.run(cmd, universal_newlines=True, shell=True, stdout=out, stderr=out)
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

    begin_ts = datetime.datetime.utcnow()
    cmd = " ".join(["sudo", EXE, "workload run kv --zipfian --skew {0} --duration {1}s".format(a, dur)])
    for node in NODES:
        postgres = " postgresql://root@{0}:26257?sslmode=disable".format(node["ip"])
        cmd += postgres

    call_with_redirect(cmd, "failed to run kv benchmark", logfile)
    end_ts = datetime.datetime.utcnow()

    return begin_ts, end_ts


def parse_latencies(logfile):
    """ Parses the training logfile for latencies.
    
    Args:
        logfile (str): logfile on which to parse.

    Returns:
        keys to a list of timestamps and latencies (collections.defaultdict)
    """

    cmd = "cat {0} | grep {1}".format(logfile + ".tmp", GREP_PHRASE)
    call_with_redirect(cmd, "parse latencies failed", logfile)

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


def parse_features(begin, end, logfile):

    """ Parses training features per node.

    Args:
        begin (datetime.datetime object): begin timestamp
        end (datetime.datetime object): end timestamp
        logfile (str): logfile to write features to

    Returns:
        keys to features (collection.dict(list))

    """

    logs = []
    for node in NODES:
        ip = node["node"]

        # composing log file
        temp_log = make_logfile_name("temp", begin, ip)
        logs.append(temp_log)

        # grepping for lines between two timestamps
        awk = "awk -v \"from={0}\" -v \"to={1}\" -F ' ' '{{ if ($2 > from && $2 <= to) print }}'".format(
            begin.strftime("%H:%M:%S"), end.strftime("%H:%M:%S"))

        # filter for grep phrase and redirect all output to composed logfile
        filter_cmd = "sudo ssh -t {2} 'cat /data/logs/cockroach.log' | {0} | grep {1} | grep -v System | grep -v Local".format(
            awk, GREP_PHRASE, ip)
        call_with_redirect(filter_cmd, "Could not filter logfile", temp_log)


    sort = "sort {0}".format(make_logfile_name("temp", begin, "*"))
    call_with_redirect(sort, "sorting failed.", logfile)


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
    with open(logfile, 'r') as f:
        for line in f:
            try:
                key, feature_dict = parse(line)
                keys_to_features[key].append(feature_dict)
            except:
                print("Cannot parse line:", line)

    return keys_to_features


def parse_training_features(begin, end):

    """ Parses training features

    Args:
        begin (datetime.datetime obj): time at which training began
        end (datetime.datetime obj): time at which training run ended.

    Returns:
        logfile to which features are written (str), keys_to_features map.
    """

    feature_log = make_logfile_name("trainfeatures", begin)
    return feature_log, parse_features(begin, end, feature_log)


def parse_inference_features(begin, end):

    """ Parses inference features.

    Args:
        begin (datetime.datetime obj): time at which inference run began.
        end (datetime.datetime obj): time at which inference run ended.

    Returns:
        logfile to which features are written (Str), keys_to_features map.
    """

    feature_log = make_logfile_name("inferencefeatures", begin)
    return feature_log, parse_features(begin, end, feature_log)


def calculate_stats(extracts, frequency, latencies):

    results = []
    extracts += latencies
    # print(extracts)
    df = pandas.DataFrame.from_records(extracts)

    for name, group in df.groupby(pandas.Grouper(key="timestamp", freq=frequency)):
        successful_accesses = len(group[group["typ"] == Action.ACCESS_SUCCESS])
        uncommitted_intents = len(group[group["typ"] == Action.UNCOMMITTED_INTENT])
        newer_committed_values = len(group[group["typ"] == Action.NEWER_COMMITTED_VALUE])
        spanlatch_waits = group[group["typ"] == Action.SPANLATCH_WAIT]
        txnqueue_waits = group[group["typ"] == Action.TXNQUEUE_WAIT]
        bumped_for_read = len(group[group["typ"] == Action.TS_BUMPED_READ])
        #latencies = group[group["latency"].notnull()]

        failed_accesses = uncommitted_intents + newer_committed_values
        total_accesses = successful_accesses + failed_accesses

        result = {
                "total_accesses": total_accesses,
                "bumped_read": bumped_for_read,
                "failed_accesses": None if total_accesses == 0 else float(failed_accesses)/total_accesses,
                "uncommitted_intents": None if total_accesses == 0 else float(uncommitted_intents)/total_accesses,
                "newer_committed_values": None if total_accesses == 0 else float(newer_committed_values)/total_accesses,
                "avg(spanlatch_wait)": spanlatch_waits["val"].mean(),
                "med(spanlatch_wait)": spanlatch_waits["val"].median(),
                "p99(spanlatch_wait)": spanlatch_waits["val"].quantile(0.99),
                "avg(txnqueue_wait)": txnqueue_waits["val"].mean(),
                "med(txnqueue_wait)": txnqueue_waits["val"].median(),
                "p99(txnqueue_wait)": txnqueue_waits["val"].quantile(0.99),
                "avg(latency)": group["latency"].mean(),
                "med(latency)": group["latency"].median(),
                "p99(latency)": group["latency"].quantile(0.99)
                }

        results.append(result)
        return results


def process(keys_to_features, keys_to_latencies):
    freq = "10s"
    final = []
    for key, value in keys_to_features.items():
        if key not in keys_to_latencies:
            continue

        latencies = keys_to_latencies[key]
        for stat in calculate_stats(value, freq, latencies):
            stat["key"] = key
            final.append(stat)
    df = pandas.DataFrame.from_records(final).dropna()
    features = df.drop(columns=["avg(latency)", "med(latency)", "p99(latency)"])

    X = features.values
    avgy = df["avg(latency)"].values
    medy = df["med(latency)"].values
    p99y = df["p99(latency)"].values

    return X, avgy, medy, p99y


def train_model(X, avgy, medy, p99y):

    """ Creates and trains a model.

    Args:
        features (keys_to_features collections.defaultdict(list)): features
        Y (keys_to_latencies collections.defaultdict(list)): results.

    Returns:
        avg_model, med_model, p99_model
    """

    # avg
    avg_model = sklearn.linear_model.LinearRegression().fit(X, avgy)

    # med
    med_model = sklearn.linear_model.LinearRegression().fit(X, medy)

    # p99
    p99_model = sklearn.linear_model.LinearRegression().fit(X, p99y)

    return avg_model, med_model, p99_model


def score_model(model, features, labels):
    return model.score(features, labels)


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
    begin, end = execute_round(a, train_dur, train_logfile + ".tmp")
    train_latencies = parse_latencies(train_logfile)
    feature_log, train_features = parse_training_features(begin, end)
    features, avg_labels, med_labels, p99_labels = process(train_features, train_latencies)
    avg_model, med_model, p99_model = train_model(features, avg_labels, med_labels, p99_labels)
    train_avg_r2 = score_model(avg_model, features, avg_labels)
    train_med_r2 = score_model(med_model, features, med_labels)
    train_p99_r2 = score_model(p99_model, features, p99_labels)


    # run inference round
    begin, end = execute_round(a, inf_dur, inf_logfile + ".tmp")
    inf_latencies = parse_latencies(inf_logfile)
    inf_feature_log, inf_features = parse_inference_features(begin, end)
    features, avg_labels, med_labels, p99_labels = process(inf_latencies, inf_features)
    inf_avg_r2 = score_model(avg_model, features, avg_labels)
    inf_med_r2 = score_model(med_model, features, med_labels)
    inf_p99_r2 = score_model(p99_model, features, p99_labels)

    return train_avg_r2, train_med_r2, train_p99_r2, inf_avg_r2, inf_med_r2, inf_p99_r2


def main():

    skew = 1.1 # alpha
    train_dur = 5 # seconds
    inf_dur = 5 # seconds

    print(run_iteration(skew, train_dur, inf_dur))

    return 0


if __name__ == "__main__":
    sys.exit(main())
