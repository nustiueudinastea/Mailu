import os

from protoslib import protos
from circus import get_arbiter

WEBMAIL = 'rainloop'
WEB_WEBMAIL = '/webmail'
ADMIN = 'true'
WEB_ADMIN = '/admin'
HOSTNAMES = 'mail.protos.io'
DOMAIN = 'protos.io'
TLS_FLAVOR = 'cert'
RELAYNETS = '172.16.0.0/12'
MESSAGE_SIZE_LIMIT = '5000000'
FETCHMAIL_DELAY= '600'
RECIPIENT_DELIMITER = '+'
DMARC_RUA = 'admin'
DMARC_RUF = 'admin'
WELCOME = 'true'
WELCOME_SUBJECT = 'Welcome to your new Mailu email account'
WELCOME_BODY = 'Welcome to your new email account, if you can read this, then Mailu is configured properly and running on your Protos platform!'

HOST_ADMIN = '127.0.0.1:8080'
HOST_SMTP = 'smtp:11025'
HOST_AUTHSMTP = 'smtp:11026'
HOST_IMAP = 'imap:11143'
HOST_POP3 = 'imap:11110'
HOST_WEBMAIL = 'webmail'

rainloop_proc = {'cmd': '/mailu/rainloop/start.sh', 'working_dir': '/var/www', 'numprocesses': 1}
rsyslog_proc = {'cmd': '/usr/sbin/rsyslogd -n', 'working_dir': '/', 'numprocesses': 1}
redis_proc = {'cmd': '/usr/bin/redis-server', 'working_dir': '/', 'numprocesses': 1}
nginx_proc = {'cmd': '/mailu/nginx/start.py', 'working_dir': '/mailu/nginx', 'numprocesses': 1,
              "env": {'TLS_FLAVOR': TLS_FLAVOR, 'HOSTNAMES': HOSTNAMES, 'ADMIN': ADMIN, 'HOST_ADMIN': HOST_ADMIN,
              'HOST_SMTP': HOST_SMTP, 'WEB_WEBMAIL': WEB_WEBMAIL, 'WEB_ADMIN': WEB_ADMIN}}
mailu_proc = {'cmd': '/mailu/admin/start.sh', 'working_dir': '/mailu/admin' ,'numprocesses': 1,
              'env': {'DOMAIN': DOMAIN, 'HOST_SMTP': HOST_SMTP, 'HOST_IMAP': HOST_IMAP, 'HOST_POP3': HOST_POP3,
              'HOST_AUTHSMTP': HOST_AUTHSMTP}}
dovecot_proc = {'cmd': '/mailu/dovecot/start.py', 'working_dir': '/mailu/dovecot' ,'numprocesses': 1,
                'env': {'DOMAIN': DOMAIN, 'HOSTNAMES': HOSTNAMES, 'WEBMAIL': WEBMAIL, 'PATH': os.environ['PATH']}}
postfix_proc = {'cmd': '/mailu/postfix/start.py', 'working_dir': '/mailu/postfix' ,'numprocesses': 1,
                'env': {'DOMAIN': DOMAIN, 'HOSTNAMES': HOSTNAMES, 'RELAYNETS': RELAYNETS,
                        'MESSAGE_SIZE_LIMIT': MESSAGE_SIZE_LIMIT, 'FETCHMAIL_DELAY': FETCHMAIL_DELAY,
                        'RECIPIENT_DELIMITER': RECIPIENT_DELIMITER, 'DMARC_RUA': DMARC_RUA, 'DMARC_RUF': DMARC_RUF,
                        'WELCOME': WELCOME, 'WELCOME_SUBJECT': WELCOME_SUBJECT, 'WELCOME_BODY': WELCOME_BODY}}
all_processes = [rainloop_proc, rsyslog_proc, nginx_proc, redis_proc, mailu_proc, dovecot_proc, postfix_proc]

def do_circus():
    arbiter = get_arbiter(all_processes)
    try:
        arbiter.start()
    finally:
        arbiter.stop()


def do_protos():
    client = protos.Protos('babc48rj02j3q36u8hdg', 'http://127.0.0.1:9999/')
    print(client.get_domain())

    #client.delete_resource('b78b0f0c0c3115097f02e0b049336217')

    rsc= {'type': 'dns', 'value': {'host': 'mail', 'value': '192.168.1.1', 'type': 'A'}}
    rsc = client.create_resource(rsc)
    print(rsc)
    rsc = client.get_resource(rsc['id'])
    print(rsc)
    client.delete_resource(rsc['id'])

    client.register_provider('dns')
    client.deregister_provider('dns')

if __name__== "__main__":
  do_circus()