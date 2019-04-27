#!/usr/bin/env python3

import argparse
import collections
import datetime
import enum
import numpy as np
import pandas
import statistics

class Action(enum.Enum):
    ATTEMPT = 0
    SUCCEED = 1
    FAIL = 2
    RELEASE = 3


class Extracted:

    def __init__(self, timestamp, action, tracker):
        self.timestamp = self.__parse_timestamp(timestamp)
        self.action = self.__parse_action(action)
        self.tracker = tracker
        self.duration_ms = None

    def __parse_timestamp(self, timestamp):
        dt = datetime.datetime.strptime(timestamp, "%H:%M:%S.%f")
        dt.replace(year=2019, month=4, day=14)
        return dt

    def __parse_action(self, action):
        if action == "latchAttempt":
            return Action.ATTEMPT
        elif action == "latchSuccess":
            return Action.SUCCEED
        elif action == "latchFail":
            return Action.FAIL
        elif action == "latchRelease":
            return Action.RELEASE

    def set_duration_ms(self, duration):
        try:
            self.duration_ms = float(duration.strip("ms"))
        except:
            self.duration_ms = float(duration[:-3]) / 10e3


    def __str__(self):
        return "{0}, action:{1}, tracker:{2}, duration:{3}".format(
                self.timestamp, self.action, self.tracker, self.duration)

    def to_dict(self):
        return {    "timestamp": self.timestamp,
                    "duration": self.duration_ms,
                    "action": self.action,
                }
        
    def to_df(self):
        return pandas.DataFrame(self.to_dict())


class Features:

    def __init__(self):
        self.overall_access_count = 1
        self.fail_access_count = 0
        self.durations_ms = []

        self.fail_access = collections.defaultdict(0)
        self.durations = collections.defaultdict([])

    def update(self, extracted):

        if extracted.action == Action.ATTEMPT:
            self.overall_access_count += 1
        elif extracted.action == Action.FAIL:
            self.fail_access[extracted.timestamp] += 1
            self.fail_access_count += 1
        elif extracted.action == Action.RELEASE:
            self.durations[extracted.timestamp].append(extracted.duration_ms)
            self.durations_ms.append(extracted.duration_ms)

    def calculate_contention_rate(self, interval=0):

        if interval == 0:
            return float(self.fail_access_count) / self.overall_access_count

        end_bound_to_contention = {}
        

    def calculate_average_duration(self):
        return statistics.mean(self.durations_ms)

    def calculate_median_duration(self):
        return statistics.median(self.durations_ms)

    def __str__(self):
        result = "overall_access:{0}, fail:{1}, contention:{2}".format(
                self.overall_access_count, self.fail_access_count, self.calculate_contention_rate())
        if len(self.durations_ms) > 0:
            result += ", avg_duration:{0}, median_duration:{1}".format(
                self.calculate_average_duration(), self.calculate_median_duration())

        return result


class Key:

    def __init__(self, key):
        self.key = key


def parse_line(line):

    TIMESTAMP_IDX = 1
    TRACKER_IDX = 5
    KEY_IDX = 8
    ACTION_IDX = 7
    
    DURATION = 10

    tokens = line.split()
    timestamp = tokens[TIMESTAMP_IDX]
    tracker = int(tokens[TRACKER_IDX].strip(","))
    key = tokens[KEY_IDX]
    action = tokens[ACTION_IDX]

    extracted = Extracted(timestamp, action, tracker)
    if extracted.action == Action.RELEASE:
        duration = tokens[DURATION] 
        extracted.set_duration_ms(duration)

    return key, extracted

def calculate_stats(extracts):

    df = pandas.DataFrame.from_records(extracts)
    
    for name, group in df.groupby(pandas.Grouper(key="timestamp", freq="1s")):
        attempts_df = group[group["action"] == Action.ATTEMPT]

        attempts = len(attempts_df)
        if attempts == 0:
            return

        sorted_df = attempts_df.sort_values(by=["timestamp"])
        sorted_df["time_bw_accesses"] = sorted_df["timestamp"].diff()

        fails = len(group[group["action"] == Action.FAIL])

        print(  "avg_duration:", group["duration"].agg(np.mean),
                "med_duration:", group["duration"].agg(np.median),
                "access_cnt:", attempts,
                "avg_time_bw_accesses:", sorted_df["time_bw_accesses"].agg(np.mean),
                "med_time_bw_accesses:", sorted_df["time_bw_accesses"].agg(np.median),
                "fails:", fails,
                "contention:", float(fails)/attempts)

    
def main():

    parser = argparse.ArgumentParser(description='Parses out features for prediction contention')
    parser.add_argument('logfiles', nargs="+", help="Logfiles to be parsed")

    args = parser.parse_args()

    keys_to_features = collections.defaultdict(list)
    for logfile in args.logfiles:
        with open(logfile, 'r') as f:
            for line in f:
                key, extracted = parse_line(line)
                keys_to_features[key].append(extracted.to_dict())

    for key, value in keys_to_features.items():
        print(key)
        calculate_stats(value)

    return 0


if __name__ == "__main__":
    main()


