import os
import base64
import os.path
import subprocess

from protoslib import protos, exceptions
from circus import get_arbiter
from time import sleep

WEBMAIL = 'rainloop'
WEB_WEBMAIL = '/webmail'
ADMIN = 'true'
WEB_ADMIN = '/admin'
HOSTNAMES = '' # set at runtime
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

PROTOS_URL = 'http://172.17.0.6:9999/'
PROTOS_APP_ID = 'bb1pq5rj02j1hjk38j0g'

def set_proc_vars():
    rainloop_proc = {'cmd': '/mailu/rainloop/start.sh', 'working_dir': '/var/www', 'numprocesses': 1}
    rsyslog_proc = {'cmd': '/usr/sbin/rsyslogd -n', 'working_dir': '/', 'numprocesses': 1}
    redis_proc = {'cmd': '/usr/bin/redis-server', 'working_dir': '/', 'numprocesses': 1}
    nginx_proc = {'cmd': '/mailu/nginx/start.py', 'working_dir': '/mailu/nginx', 'numprocesses': 1,
                "env": {'TLS_FLAVOR': TLS_FLAVOR, 'HOSTNAMES': HOSTNAMES, 'ADMIN': ADMIN, 'HOST_ADMIN': HOST_ADMIN,
                'HOST_SMTP': HOST_SMTP, 'WEB_WEBMAIL': WEB_WEBMAIL, 'WEB_ADMIN': WEB_ADMIN}}
    mailu_proc = {'cmd': '/mailu/admin/start.sh', 'working_dir': '/mailu/admin' ,'numprocesses': 1,
                'env': {'DOMAIN': DOMAIN, 'HOST_SMTP': HOST_SMTP, 'HOST_IMAP': HOST_IMAP, 'HOST_POP3': HOST_POP3,
                'HOST_AUTHSMTP': HOST_AUTHSMTP, 'PROTOS_URL': PROTOS_URL, 'APPID': PROTOS_APP_ID, 'HOSTNAMES': HOSTNAMES,
                'DMARC_RUA': DMARC_RUA, 'DMARC_RUF': DMARC_RUF}}
    dovecot_proc = {'cmd': '/mailu/dovecot/start.py', 'working_dir': '/mailu/dovecot' ,'numprocesses': 1,
                    'env': {'DOMAIN': DOMAIN, 'HOSTNAMES': HOSTNAMES, 'WEBMAIL': WEBMAIL, 'PATH': os.environ['PATH']}}
    postfix_proc = {'cmd': '/mailu/postfix/start.py', 'working_dir': '/mailu/postfix' ,'numprocesses': 1,
                    'env': {'DOMAIN': DOMAIN, 'HOSTNAMES': HOSTNAMES, 'RELAYNETS': RELAYNETS,
                            'MESSAGE_SIZE_LIMIT': MESSAGE_SIZE_LIMIT, 'FETCHMAIL_DELAY': FETCHMAIL_DELAY,
                            'RECIPIENT_DELIMITER': RECIPIENT_DELIMITER, 'DMARC_RUA': DMARC_RUA, 'DMARC_RUF': DMARC_RUF,
                            'WELCOME': WELCOME, 'WELCOME_SUBJECT': WELCOME_SUBJECT, 'WELCOME_BODY': WELCOME_BODY}}
    all_processes = [rainloop_proc, rsyslog_proc, nginx_proc, redis_proc, mailu_proc, dovecot_proc, postfix_proc]
    # all_processes = [nginx_proc]
    return all_processes

def do_circus(event_loop=None):
    arbiter = get_arbiter(set_proc_vars(), loop=event_loop)
    try:
        arbiter.start()
    finally:
        arbiter.stop()


def create_certificates(cert, issuercert, privatekey):
    with open('/certs/cert.pem', mode='wb') as f:
        f.write(base64.b64decode(cert))
        f.write(base64.b64decode(issuercert))
    with open('/certs/key.pem', mode='wb') as f:
        f.write(base64.b64decode(privatekey))

    if not os.path.isfile('/certs/dhparam.pem'):
        print('Creating /certs/dhparam.pem')
        subprocess.call(['openssl', 'dhparam', '-dsaparam', '-out', '/certs/dhparam.pem', '4096'])

def do_protos():
    client = protos.Protos(PROTOS_APP_ID, PROTOS_URL)
    domain = client.get_domain()
    app_info = client.get_app_info()
    print(domain)
    print(app_info)
    global HOSTNAMES
    HOSTNAMES = app_info['name'] + '.' + domain

    # #client.delete_resource('b78b0f0c0c3115097f02e0b049336217')

    #rsc= {'type': 'dns', 'value': {'host': 'mail', 'value': '192.168.1.1', 'type': 'A'}}
    mx_record = {'type': 'dns', 'value': {'host': '@', 'value': app_info['name'] + '.' + domain, 'type': 'MX', 'ttl': 300}}
    try:
        rsc_mx = client.create_resource(mx_record)
    except exceptions.ProtosException as e:
        if "already registered" not in str(e):
            raise e
        else:
            mx_rsc_id = str(e).split(' ')[1]
            rsc_mx = client.get_resource(mx_rsc_id)
    print(rsc_mx)

    certficate = {'type': 'certificate', 'value': {'domains': [app_info['name']]}}
    try:
        rsc_cert = client.create_resource(certficate)
    except exceptions.ProtosException as e:
        if "already registered" not in str(e):
            raise e
        else:
            rsc_cert_id = str(e).split(' ')[1]
            rsc_cert = client.get_resource(rsc_cert_id)
    while rsc_cert['status'] != 'created':
        sleep(10)
        rsc_cert = client.get_resource(rsc_cert['id'])
        print("waiting for certificate to be created")

    create_certificates(rsc_cert['value']['certificate'], rsc_cert['value']['issuercertificate'], rsc_cert['value']['privatekey'])

    # rsc_id = '14bafec7d4e9d3977b9e2cb582ad627b'
    # rsc = client.get_resource(rsc_id)
    # print(rsc)
    # client.delete_resource(rsc_id)

    # client.register_provider('dns')
    # client.deregister_provider('dns')

if __name__== "__main__":
    do_protos()
    print('------------------- Starting all processes ---------------------')
    do_circus()