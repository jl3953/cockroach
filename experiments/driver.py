#!/usr/bin/env python3

import subprocess
import sys

CR_NODES = ["192.168.1.2", "192.168.1.3", "192.168.1.4"]
CR_EXE = "/usr/local/temp/go/src/github.com/cockroachdb/cockroach/cockroach"


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
    cmd = "ssh {0} '{1}'".format(host, cmd)
    return call(cmd, err_msg)


def start_cockroach_node(host, listen, join=None):
    cmd = "{0} start --insecure --background --listen-addr={1}:26257".format(CR_EXE, listen)

    if join:
        cmd = "{0} --join={0}:26257".format(cmd, join)

    return call_remote(host, cmd)


def start_cluster():
    first = CR_NODES[0]

    start_cockroach_node(first, first)
    for n in CR_NODES[1:]:
        start_cockroach_node(n, n, join=first)


def main():
    start_cluster()


if __name__ == "__main__":
    main()
