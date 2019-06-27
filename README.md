## Python script to generate certificate for name.suffix.domain on Godaddy

1. Insall dependencies

```
   pip install godaddypy configparser
```

2. Create configuration file

```
   [godaddy]           
   key=aaa
   secret=bbb
```

3. Run `python get_certificate.py --help` to see the parameters to set.
```
   Python script to generate certificate for name.suffix.domain on Godaddy

   optional arguments:
     -h, --help                 show this help message and exit
     -c CONFIG, --config CONFIG Path to the godaddy configuration file
     -n NAME,   --name   NAME   Host's name. Default - random 32-character string
     -i IP,     --ip     IP     Host's IP address
     -s SUFFIX, --suffix SUFFIX Host's suffix
     -d DOMAIN, --domain DOMAIN Host's domain
     -o OUTPUT, --output OUTPUT Output folder. Default - ./cert

```
