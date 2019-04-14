#!/usr/bin/env python3

import argparse
import collections
import enum

class Action(enum.Enum):
    ATTEMPT = 0
    SUCCEED = 1
    FAIL = 2


class Extracted:

    def __init__(self, timestamp, action, tracker):
        self.timestamp = self.__parse_timestamp(timestamp)
        self.action = action
        self.tracker = tracker

    def __parse_timestamp(self, timestamp):
        return timestamp

    def __str__(self):
        return "[%s], action:[%s], tracker:[%d]".format(self.timestamp, self.action, self.tracker)


class Features:

    def __init__(self):
        self.overall_access_count = 1
        self.fail_access_count = 0

    def update(self, extracted):

        if extracted.action == Action.ATTEMPT:
            self.overall_access_count += 1
        elif extracted.action == Action.FAIL:
            self.fail_access_count += 1

    def calculate_contention_rate(self):
        return float(self.fail_access_count) / self.overall_access_count

    def __str__(self):
        return "overall_access:{0}, fail:{1}, contention:{2}".format(
                self.overall_access_count, self.fail_access_count, self.calculate_contention_rate())


class Key:

    def __init__(self, key):
        self.key = key


def parse_line(line):

    TIMESTAMP_IDX = 1
    TRACKER_IDX = 5
    KEY_IDX = 8
    ACTION_IDX = 7

    tokens = line.split()
    timestamp = tokens[TIMESTAMP_IDX]
    tracker = int(tokens[TRACKER_IDX].strip(","))
    key = tokens[KEY_IDX]

    action = tokens[ACTION_IDX]
    if action == "latchAttempt":
        action = Action.ATTEMPT
    elif action == "latchSuccess":
        action = Action.SUCCEED
    else:
        action = Action.FAIL

    return key, Extracted(timestamp, action, tracker)

    
def main():

    parser = argparse.ArgumentParser(description='Parses out features for prediction contention')
    parser.add_argument('logfiles', nargs="+", help="Logfiles to be parsed")

    args = parser.parse_args()

    keys_to_features = collections.defaultdict(Features)
    for logfile in args.logfiles:
        with open(logfile, 'r') as f:
            for line in f:
                key, extracted = parse_line(line)
                keys_to_features[key].update(extracted)

    for key, value in keys_to_features.items():
        print(key, value)

    return 0


if __name__ == "__main__":
    main()


