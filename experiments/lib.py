import copy
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
    cmd = "sudo ssh {0} '{1}'".format(host, cmd)
    return call(cmd, err_msg)


def init_store(node):
    ip = node["ip"]

    cmd = "if [[ ! -e {0} ]]; then mkdir {0}; fi".format(STORE_DIR)
    call_remote(ip, cmd, "Failed to initialize store")

    cmd = ("if [[ $(! mount -l | grep {0}) != *{0}* ]]; "
           "then mount -t tmpfs -o size=32g tmpfs {0}; fi").format(STORE_DIR)
    call_remote(ip, cmd, "Failed to initialize store")


def kill_cockroach_node(node):
    ip = node["ip"]

    if "store" in node:
        store = node["store"]
    else:
        store = None

    cmd = ("PID=$(! pgrep cockroach) "
           "|| (sudo pkill -9 cockroach; while ps -p $PID;do sleep 1;done;)")

    if store:
        cmd = "({0}) && {1}".format(cmd, "sudo rm -rf {0}".format(os.path.join(store, "*")))

    cmd = "ssh {0} '{1}'".format(ip, cmd)
    print(cmd)
    return subprocess.Popen(shlex.split(cmd))


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

    cmd = "ssh -tt {0} '{1}' && stty sane".format(ip, cmd)
    print(cmd)
    return subprocess.Popen(cmd, shell=True)


def set_cluster_settings(node):
    ip = node["ip"]
    cmd = ('echo "'
           'set cluster setting kv.range_merge.queue_enabled = false;'
           # 'set cluster setting kv.range_split.by_load_enabled = false;'
           'set cluster setting kv.raft_log.disable_synchronization_unsafe = true;'
           'alter range default configure zone using num_replicas = 1;'
           '" | {0} sql --insecure '
           '--url="postgresql://root@{1}?sslmode=disable"').format(EXE, ip)

    call_remote(ip, cmd, "Failed to set cluster settings.")


def start_cluster(nodes):
    if len(nodes) == 0:
        return

    first = nodes[0]
    start_cockroach_node(first).wait()

    ps = []
    for n in nodes[1:]:
        ps.append(start_cockroach_node(n, join=first["ip"]))

    for p in ps:
        p.wait()

    set_cluster_settings(first)


def build_cockroach(node, commit):
    cmd = ("ssh {0} 'export GOPATH=/usr/local/temp/go "
           "&& cd {1} && git pull && git checkout {2} "
           "&& (make build || "
           "(./bin/dep ensure && make clean && make build))'") \
           .format(node["ip"], COCKROACH_DIR, commit)

    return subprocess.Popen(shlex.split(cmd))


def build_cockroach_commit(nodes, commit):
    ps = [build_cockroach(n, commit) for n in nodes]

    for p in ps:
        p.wait()


def cleanup_previous_experiment(config):
    ps = []
    for n in config["workload_nodes"]:
        p = kill_cockroach_node(n)
        ps.append(p)

    for n in config["hot_nodes"] + config["warm_nodes"]:
        p = kill_cockroach_node(n)
        ps.append(p)

    for p in ps:
        p.wait()


def set_hot_keys(nodes, keys):
    if len(keys) == 0:
        return

    values = ', '.join(map(lambda k: "({})".format(k), keys))

    for n in nodes:
        ip = n["ip"]
        cmd = ('echo "'
               'alter table kv.kv hotkey at values {2};'
               '" | {0} sql --insecure '
               '--url="postgresql://root@{1}?sslmode=disable"').format(EXE, ip, values)

        call_remote(ip, cmd, "Failed to set cluster settings.")


def init_experiment(config):
    nodes = config["workload_nodes"] \
            + config["warm_nodes"] \
            + config["hot_nodes"]

    build_cockroach_commit(nodes, config["cockroach_commit"])

    # Start hot node separately from warm nodes
    start_cluster(config["hot_nodes"])
    start_cluster(config["warm_nodes"])


def save_params(exp_params, out_dir):
    params = {
        "exp_params": exp_params
    }

    path = os.path.join(out_dir, "params.json")
    with open(path, "w") as f:
        json.dump(params, f, indent=4)


def read_params(out_dir):
    path = os.path.join(out_dir, "params.json")
    with open(path, "r") as f:
        params = json.load(f)
        return params["exp_params"]

def vary_zipf_skew(config, skews):
    if ("benchmark" in config and
        "run_args" in config["benchmark"] and
        "distribution" in config["benchmark"]["run_args"] and
        "type" in config["benchmark"]["run_args"]["distribution"] and
        config["benchmark"]["run_args"]["distribution"]["type"] == "zipf"):

        out_dir = config["out_dir"]
        exps = []
        i = 0
        for s in skews:
            e = copy.deepcopy(config)
            if "params" not in e["benchmark"]["run_args"]["distribution"]:
                e["benchmark"]["run_args"]["distribution"]["params"] = {}

            if "skew" in e["benchmark"]["run_args"]["distribution"]["params"]:
                print("WARNING: Overwriting skew param in experiment config!")

            e["benchmark"]["run_args"]["distribution"]["params"]["skew"] = s
            e["out_dir"] = os.path.join(out_dir, "skew-{0}".format(i))
            exps.append(e)
            i += 1

        return exps

    else:
        raise ValueError("Passed experiment that does not use Zipf distribution!")


def parse_bench_args(bench_config):
    args = []

    if "duration" in bench_config:
        args.append("--duration={}s".format(bench_config["duration"]))

    if "drop" in bench_config and bench_config["drop"] is True:
        args.append("--drop")

    if "concurrency" in bench_config:
        args.append("--concurrency={}".format(bench_config["concurrency"]))

    if "splits" in bench_config:
        args.append("--splits={}".format(bench_config["splits"]))

    if "read_percent" in bench_config:
        args.append("--read-percent={}".format(bench_config["read_percent"]))

    if "n_statements_per_txn" in bench_config:
        args.append("--stmt-per-txn={}".format(bench_config["n_statements_per_txn"]))

    if "batch" in bench_config:
        args.append("--batch={}".format(bench_config["batch"]))
        
    if "distribution" in bench_config:
        d = bench_config["distribution"]
        params = d["params"]

        if d["type"] == "zipf":
            args.append("--zipfian")
            args.append("--s={1}".format(args, params["skew"]))

    return " ".join(args)


def run_bench(config):
    out_dir = config["out_dir"]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    save_params(config, out_dir)

    nodes = config["warm_nodes"]
    out_dir = config["out_dir"]
    b = config["benchmark"]

    name = b["name"]

    urls = ["postgresql://root@{0}:26257?sslmode=disable".format(n["ip"])
            for n in nodes]
    urls = " ".join(urls)

    workload_nodes = config["workload_nodes"]

    if len(workload_nodes) == 0:
        print("No workload nodes!")
        return

    if len(nodes) == 0:
        print("No cluster nodes!")
        return

    args = parse_bench_args(b["init_args"])
    cmd = "{0} workload init {1} {2} {3}".format(EXE, name, urls, args)

    ip = workload_nodes[0]["ip"]
    call_remote(ip, cmd, "Failed to initialize benchmark")

    if "hot_keys" in b["init_args"]:
        set_hot_keys(nodes, b["init_args"]["hot_keys"])
    
    i = 0
    ps = []
    for wn in workload_nodes:
        args = parse_bench_args(b["run_args"])
        cmd = "{0} workload run {1} {2} {3}".format(EXE, name, urls, args)

        # Call remote
        ip = wn["ip"]
        cmd = "sudo ssh {0} '{1}'".format(ip, cmd)
        print(cmd)

        path = os.path.join(out_dir, "bench_out_{0}.txt".format(i))
        print(path)
        with open(path, "w") as f:
            ps.append(subprocess.Popen(shlex.split(cmd), stdout=f))

        i += 1

    for p in ps:
        p.wait()

