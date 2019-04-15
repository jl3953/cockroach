import json
import os
import shlex
import subprocess
import sys

# Constants
COCKROACH_DIR = "/usr/local/temp/go/src/github.com/cockroachdb/cockroach"
EXE = os.path.join(COCKROACH_DIR, "cockroach")
STORE_DIR = "/data"

FPATH = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.join(FPATH, '..')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')


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


def init_store(node):
    ip = node["ip"]

    cmd = "if [[ ! -e {0} ]]; then mkdir {0}; fi".format(STORE_DIR)
    call_remote(ip, cmd, "Failed to initialize store")

    cmd = ("if [[ $(! mount -l | grep {0}) != *{0}* ]]; "
           "then mount -t tmpfs -o size=32g tmpfs {0}; fi").format(STORE_DIR)
    call_remote(ip, cmd, "Failed to initialize store")


def cleanup_store(node):
    ip = node["ip"]
    store = node["store"]
    cmd = "sudo rm -rf {0}".format(os.path.join(store, "*"))
    call_remote(ip, cmd, "Failed to remove cockroach data.")


def kill_cockroach_node(node):
    ip = node["ip"]

    cmd = ("PID=$(! pgrep cockroach) "
           "|| (sudo pkill -9 cockroach; while ps -p $PID;do sleep 1;done;)")
    call_remote(ip, cmd, "Failed to kill cockroach node.")


def start_cockroach_node(node, join=None):
    ip = node["ip"]
    store = node["store"]
    region = node["region"]

    cmd = ("{0} start --insecure "
           "--advertise-addr={1} "
           "--store={2} "
           "--locality=region={3} "
           "--cache=.25 "
           "--max-sql-memory=.25 "
           "--background").format(EXE, ip, store, region)

    if join:
        cmd = "{0} --join={1}:26257".format(cmd, join)

    return call_remote(ip, cmd, "Failed to start cockroach node.")


def set_cluster_settings(node):
    ip = node["ip"]
    cmd = ('echo '
           '"set cluster setting kv.raft_log.synchronize=false;'
           'alter range default configure zone using num_replicas = 1;'
           '" | {0} sql --insecure '
           '--url="postgresql://root@{1}?sslmode=disable"').format(EXE, ip)

    call_remote(ip, cmd, "Failed to set cluster settings.")


def start_cluster(nodes):
    first = nodes[0]

    start_cockroach_node(first)
    for n in nodes[1:]:
        start_cockroach_node(n, join=first["ip"])

    set_cluster_settings(first)


def build_cockroach(node, commit):
    cmd = ("ssh -t {0} 'export GOPATH=/usr/local/temp/go "
           "&& cd {1} && git pull && git checkout {2}"
           "&& (make build || (make clean && make build))'") \
           .format(node["ip"], COCKROACH_DIR, commit)

    return subprocess.Popen(shlex.split(cmd))


def build_cockroach_commit(nodes, commit):
    ps = [build_cockroach(n, commit) for n in nodes]

    for p in ps:
        p.wait()


def cleanup_previous_experiment(config):
    for n in config["nodes"]:
        kill_cockroach_node(n)
        cleanup_store(n)


def init_experiment(config):
    build_cockroach_commit(config["nodes"], config["cockroach_commit"])
    start_cluster(config["nodes"])


def save_params(exp_params, out_dir):
    params = {
        "exp_params": exp_params
    }

    path = os.path.join(out_dir, "params.json")
    with open(path, "w") as f:
        json.dump(params, f, indent=4)


def parse_bench_args(bench_config):
    args = []

    if "duration" in bench_config:
        args.append("--duration={}s".format(bench_config["duration"]))

    if "n_clients" in bench_config:
        args.append("--concurrency={}".format(bench_config["n_clients"]))

    if "splits" in bench_config:
        args.append("--splits={}".format(bench_config["splits"]))

    if "read_percent" in bench_config:
        args.append("--read-percent={}".format(bench_config["read_percent"]))

    if "distribution" in bench_config:
        d = bench_config["distribution"]
        params = d["params"]

        if d["type"] == "zipf":
            args.append("--zipfian={1}".format(args, params["skew"]))

    return " ".join(args)


def run_bench(config):
    nodes = config["nodes"]
    out_dir = config["out_dir"]
    b = config["benchmark"]

    name = b["name"]

    urls = ["postgresql://root@{0}:26257?sslmode=disable".format(n["ip"])
            for n in nodes]
    urls = " ".join(urls)

    args = parse_bench_args(b["init_args"])
    cmd = "{0} workload init {1} {2} {3}".format(EXE, name, urls, args)
    call(cmd, "Failed to initialize benchmark")

    args = parse_bench_args(b["run_args"])
    cmd = "{0} workload run {1} {2} {3}".format(EXE, name, urls, args)

    path = os.path.join(out_dir, "bench_out.txt")
    print(path)
    with open(path, "w") as f:
        subprocess.Popen(shlex.split(cmd), stdout=f).wait()
