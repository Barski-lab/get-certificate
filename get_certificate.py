import sys
import os
import configparser
import subprocess
from godaddypy import Client, Account


config_file = sys.argv[1]
name = sys.argv[2]
ip = sys.argv[3]
domain = sys.argv[4]
suffix = "worker"

config = configparser.ConfigParser()                                                                                                                                    
config.read(config_file)

acc = Account(api_key=config.get('godaddy', 'key'), api_secret=config.get('godaddy', 'secret'))
cli = Client(acc)

try:
    records = cli.get_records(domain, record_type='A', name=name)
except Exception as err:
    print("Failed to fetch records for", domain, err)
    exit()

if not records:
    cli.add_records(domain, {"data": ip, "name": name, "ttl": 1800, "type": "A"})
elif records[0]["data"] != ip:
    records[0]["data"] = ip                                                                                                                    
    cli.update_record(domain, records)   

env = os.environ.copy()
env.update( {"GD_Key": config.get('godaddy', 'key'), "GD_Secret": config.get('godaddy', 'secret')} )
subprocess.run( [ "./acme/acme.sh", "--issue", "--dns", "dns_gd", "-d", ".".join([name, suffix, domain]) ], env=env )










    
                                                                                                                                                                        
