#!/usr/bin/python

import jinja2
import os
import socket
import glob

convert = lambda src, dst: open(dst, "w").write(jinja2.Template(open(src).read()).render(**os.environ))

# Actual startup script
if not os.environ.has_key("FRONT_ADDRESS"):
    os.environ["FRONT_ADDRESS"] = socket.gethostbyname("front")
if os.environ["WEBMAIL"] != "none":
    if os.environ.has_key("HOST_WEBMAIL"):
        os.environ["WEBMAIL_ADDRESS"] = os.environ["HOST_WEBMAIL"]
    else:
        os.environ["WEBMAIL_ADDRESS"] = socket.gethostbyname("webmail")

for dovecot_file in glob.glob("/mailu/dovecot/conf/*"):
    convert(dovecot_file, os.path.join("/etc/dovecot", os.path.basename(dovecot_file)))

# Run postfix
os.system("chown -R mail:mail /mail /var/lib/dovecot")
os.execv("/usr/sbin/dovecot", ["/usr/sbin/dovecot", "-c", "/etc/dovecot/dovecot.conf", "-F"])
