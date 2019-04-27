#!/usr/bin/env python3

import argparse
import collections
import sklearn.linear_model
import numpy as np

def parse_line(line):
    tokens = line.split(',')
    key = tokens[0]
    tokens = tokens[1:]

    feature_dict = {}
    for token in tokens:
        token = token.strip()
        feature_name, feature_val = token.split('=')
        feature_dict[feature_name] = float(feature_val)

    return key, feature_dict


def parse_latencies(line):

    tokens = line.split(',')
    key = tokens[0]
    tokens = tokens[1:]

    latency_dict = {}
    for token in tokens:
        token = token.strip()
        latency, latency_val = token.split('=')
        latency_dict[latency] = float(latency_val)

    return key, latency_dict


def main():

    parser = argparse.ArgumentParser(description="Who cares")
    parser.add_argument("feature_file", type=str, help="file of features")
    parser.add_argument("latency_file", type=str, help="file of latencies")
    parser.add_argument("--outfile", type=str, default="params.txt", help="file to write parameters to")

    args = parser.parse_args()

    keys_to_features = collections.defaultdict(list)
    with open(args.feature_file, 'r') as f:
        for line in f:
            key, features = parse_line(line)
            keys_to_features[key].append(features)

    keys_to_latencies = collections.defaultdict(list)
    with open(args.latency_file, 'r') as f:
        for line in f:
            key, latencies = parse_latencies(line)
            keys_to_latencies[key] = latencies


    # avg(latency)
    matrix = []
    y = []
    feature_names = []
    is_set = False
    for key, list_of_dicts in keys_to_features.items():
        if key not in keys_to_latencies:
            continue

        for features in list_of_dicts:
            if features["total_accesses"] < 3:
                continue
            coeffs = []
            for name, feature_val in features.items():
                if not is_set:
                    feature_names.append(name)

                coeffs.append(feature_val)
            if np.isnan(coeffs[-1]):
                continue
            is_set = True
            matrix.append(coeffs)
            y.append(keys_to_latencies[key]["avg(latency)"])

    X = np.array(matrix)
    Y = np.array(y)

    reg = sklearn.linear_model.LinearRegression().fit(X, Y)
    
    with open(args.outfile, 'w') as f:
        f.write("reg.score()="+str(reg.score(X, Y)) + "\n")
        for feature, c in zip(feature_names, reg.coef_):
            f.write(feature + " " + str(c) + "\n")
        f.write(str(reg.intercept_) + "\n")


    return 0


if __name__ == "__main__":
    main()
