#!/usr/bin/env python3

import argparse

def generate_iface(index):

    link = "link_0.addInterface(iface{0})".format(index)
    return link


def generate_config(index):

    comment = "# Node node-{0}".format(index)
    pcname = "node_{0} = request.RawPC('node-{0}')".format(index)
    hwtype = "node_{0}.hardware_type = 'm510'".format(index)
    diskimage = "node_{0}.disk_image = 'urn:publicid:IDN+utah.cloudlab.us+image+cops-PG0:cockroachdb.node-0'".format(index)
    iface = "iface{0} = node_{0}.addInterface('interface-{0}', pg.IPv4Address('192.168.1.{1}','255.255.255.0'))".format(index, index+1)
    service = "node_{0}.addService(rspec.Execute(shell=\"bash\", command=\"/usr/local/bin/setup\"))".format(index)

    config = "\n".join([comment, pcname, hwtype, diskimage, iface, service])

    return config


def main():

    parser = argparse.ArgumentParser(description="Generates node configs.")
    parser.add_argument("index", type=int, help="start index.")
    parser.add_argument("--endindex", type=int, help="end of range, exclusive.")
    parser.add_argument("--outfile", type=str, default="outfile", help="file being output to.")

    parser.add_argument("--iface", action="store_true", help="generate iface config")

    args = parser.parse_args()
    if not args.endindex:
        args.endindex = args.index + 1

    if args.iface:
        with open(args.outfile, "w") as w:
            for i in range(args.index, args.endindex):
                w.write(generate_iface(i) + "\n")

        return 0


    with open(args.outfile, "w") as w:
        for i in range(args.index, args.endindex):
            w.write(generate_config(i) + "\n")
            w.write("\n")

    return 0


if __name__ == "__main__":
    main()
        
