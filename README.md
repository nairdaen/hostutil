# hostutil

Utility script to modify hosts files.

## Usage
1. Create a text file that follows this format:
```
# start|<section name here>
# Can enter comments beginning with #
<ip 1>  <hostname for ip 1>
...
<ip n>  <hostname for ip n>
# end|<section name here>
```

for example:

```
# start|mydevhosts
# Front end hosts
192.160.0.10    frontend1.foo.bar
192.160.0.20    frontend2.foo.bar

# Back end hosts
192.160.0.40    backend1.foo.bar
192.160.0.80    backend2.foo.bar
# end|mydevhosts
```

and save it as devhosts.txt

2. Invoke the script as a super user `python hosts-merge.py --local-hosts auto merge --custom-hosts devhosts.txt`

3. Ping the domains to verify that hosts are being resolved as expected 

To remove the custom hosts:

1. Invoke the script as a super user `python hosts-merge.py --local-hosts auto remove --section mydevhosts`

## License
Apache 2. See LICENSE.txt

## Why not use DNS instead?
This is not meant to replace DNS, only to make it easier to assign host names to IPs for local development.

## Contribute
Not accepting contributions at this moment