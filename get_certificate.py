import os
import sys
import argparse
import configparser
import random
import string
import subprocess
from godaddypy import Client, Account


def get_parser():
    parser = argparse.ArgumentParser(description='Python script to generate certificate for name.suffix.domain on Godaddy', add_help=True)
    parser.add_argument("-c", "--config", help="Path to the godaddy configuration file")
    parser.add_argument("-n", "--name",   help="Host's name", default=None)
    parser.add_argument("-i", "--ip",     help="Host's IP address")
    parser.add_argument("-s", "--suffix", help="Host's suffix", default="worker")
    parser.add_argument("-d", "--domain", help="Host's domain")
    parser.add_argument("-o", "--output", help="Output folder", default="./cert")
    return parser


def normalize_args(args, skip_list=[]):
    normalized_args = {}
    for key,value in args.__dict__.items():
        if key not in skip_list:
            normalized_args[key] = value if not value or os.path.isabs(value) else os.path.normpath(os.path.join(os.getcwd(), value))
        else:
            normalized_args[key]=value
    return argparse.Namespace (**normalized_args)


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]
    args,_ = get_parser().parse_known_args(argsl)
    args = normalize_args(args, ["name", "ip", "suffix", "domain"])
    args.name = args.name.lower() if args.name else ''.join(random.choice(string.ascii_lowercase) for i in range(32))
    args.suffix = args.suffix.lower()
    args.domain = args.domain.lower()

    name_with_suffix = ".".join([args.name, args.suffix])
    full_name = ".".join([name_with_suffix, args.domain])
    print("Generating certificate for", full_name)
    
    config = configparser.ConfigParser()                                                                                                                                    
    config.read(args.config)

    print("Creating Godaddy client")
    acc = Account(api_key=config.get('godaddy', 'key'), api_secret=config.get('godaddy', 'secret'))
    cli = Client(acc)

    print("Getting domains")
    try:
        domains = cli.get_domains()
    except Exception as err:
        print("Failed to get domains\n", err)
        return 0

    if args.domain not in domains:
        print("Domain", args.domain, "not found")
        return 0

    print("Getting records for the domain", args.domain)
    records = cli.get_records(args.domain, record_type='A', name=name_with_suffix)
    print("Records found\n", records)

    if not records:
        print("Adding new record", name_with_suffix, "to the domain", args.domain)
        try:
            cli.add_records(args.domain, [{"data": args.ip, "name": name_with_suffix, "ttl": 600, "type": "A"}])
        except Exception as err:
            print("Failed to add record", name_with_suffix, "to the domain", args.domain, "\n", err)
    elif records[0]["data"] != args.ip:
        print("Updating IP for the first record that corresponds search criteria:", name_with_suffix, "in the domain", args.domain)
        record = records[0]
        record["data"] = args.ip
        try:
            cli.update_record(args.domain, record)
        except Exception as err:
            print("Failed to update IP for the record", name_with_suffix, "in the domain", args.domain, "\n", err)

    params = [ "./acme/acme.sh", "--issue", "--home", args.output, "--days", "90", "--dns", "dns_gd", "--debug", "-d", full_name ]
    env = os.environ.copy()
    env.update( {"GD_Key": config.get('godaddy', 'key'), "GD_Secret": config.get('godaddy', 'secret')} )
    print("Running acme.sh\n", params)
    try:
        subprocess.run(params, env=env)
    except Exception as err:
        print("Failed to run acme.sh\n", params, "\n", err)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))