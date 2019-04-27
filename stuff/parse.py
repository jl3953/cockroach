#!/usr/bin/env python3

import argparse
import collections
import datetime
import enum
import numpy as np
import pandas
import sklearn.linear_model
import statistics

class Action(enum.Enum):
    SPANLATCH_WAIT = 0
    ACCESS_SUCCESS = 1
    UNCOMMITTED_INTENT = 2
    NEWER_COMMITTED_VALUE = 3
    TXNQUEUE_WAIT = 4
    TS_BUMPED_READ = 5


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

def parse_ts(ts):
    dt = datetime.datetime.strptime(ts, "%H:%M:%S.%f")
    dt.replace(year=2019, month=4, day=27)
    return dt


def parse_latencies(line):

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

        # result = "total_accesses=%d" % total_accesses
        # result += ", bumped_read={0}".format(bumped_for_read)
        # if total_accesses > 0:
        #     result += ",failed_accesses={0}".format(float(failed_accesses)/total_accesses)
        #     result += ", uncommitted_intents={0}".format(float(uncommitted_intents)/total_accesses)
        #     result += ", newer_committed_values={0}".format(float(newer_committed_values)/total_accesses)
        # result += ", avg(spanlatch_wait)={0}".format(spanlatch_waits.val.mean())
        # result += ", med(spanlatch_wait)={0}".format(spanlatch_waits["val"].agg(np.median))
        # result += ", p99(spanlatch_wait)={0}".format(spanlatch_waits.val.quantile(.99))
        # result += ", avg(txnqueue_wait)={0}".format(txnqueue_waits["val"].agg(np.mean))
        # result += ", med(txnqueue_wait)={0}".format(txnqueue_waits["val"].agg(np.median))
        # result += ", p99(txnqueue_wait)={0}".format(txnqueue_waits.val.quantile(0.99))
        # result += ", avg(latency)={0}".format(latencies.latency.mean())
        # result += ", med(latency)={0}".format(latencies.latency.median())
        # result += ", p99(latency)={0}".format(latencies.latency.quantile(0.99))

        results.append(result)

    return results


def main():

    parser = argparse.ArgumentParser(description='Parses out features for prediction contention')
    parser.add_argument('logfile', help="Logfiles to be parsed")
    parser.add_argument('--latencyfile', help="Latency file to be parsed")
    parser.add_argument('--outfile', type=str, default="outfile", help="outfile to be written to")
    parser.add_argument('--params', type=str, default="params", help="parameter file to be written to")
    parser.add_argument('--frequency', nargs="+", choices=["1s", "10s", "100s", "1000s"], default=["1s"], help="frequencies at which to aggregate")

    args = parser.parse_args()

    keys_to_features = collections.defaultdict(list)
    with open(args.logfile, 'r') as f:
        for line in f:
            key, feature_dict = parse_line(line)
            keys_to_features[key].append(feature_dict)


    keys_to_latencies = collections.defaultdict(list)
    with open(args.latencyfile, 'r') as f:
        for line in f:
            # key, timestamp, latenc
            tuples = parse_latencies(line)
            for key, ts, latency in tuples:
                # print(key)
                keys_to_latencies[key].append({
                    "timestamp": ts,
                    "latency": latency
                    })
    
    for freq in args.frequency:
        final = []
        with open(args.outfile + freq + ".csv", "w") as f:
            for key, value in keys_to_features.items():
                if key not in keys_to_latencies:
                    continue

                latencies = keys_to_latencies[key]
                for stat in calculate_stats(value, freq, latencies):
                    f.write(key + ", " + str(stat) + "\n")
                    # stat["key"] = key
                    final.append(stat)

        df = pandas.DataFrame.from_records(final).dropna()
        features = df.drop(columns=["avg(latency)", "med(latency)", "p99(latency)"])
        print(features)
        print(list(features))
        X = features.values
        avgy = df["avg(latency)"].values
        medy = df["med(latency)"].values
        p99y = df["p99(latency)"].values

        # avg
        with open(args.params + freq + ".txt", 'w') as f:
            reg = sklearn.linear_model.LinearRegression().fit(X, avgy)
            f.write("avg\n")
            f.write("R^2=" + str(reg.score(X, avgy)) + "\n")
            for name, coeff in zip(list(features), reg.coef_):
                f.write(name + " " + str(coeff) + "\n")
            f.write(str(reg.intercept_) + "\n")
            f.write("\n")

            # med
            reg = sklearn.linear_model.LinearRegression().fit(X, medy)
            f.write("med\n")
            f.write("R^2=" + str(reg.score(X, medy)) + "\n")
            for name, coeff in zip(list(features), reg.coef_):
                f.write(name + " " + str(coeff) + "\n")
            f.write(str(reg.intercept_) + "\n")
            f.write("\n")

            # p99
            reg = sklearn.linear_model.LinearRegression().fit(X, p99y)
            f.write("p99\n")
            f.write("R^2=" + str(reg.score(X, p99y)) + "\n")
            for name, coeff in zip(list(features), reg.coef_):
                f.write(name + " " + str(coeff) + "\n")
            f.write(str(reg.intercept_) + "\n")


    return 0


if __name__ == "__main__":
    main()
