import os
import base64
import os.path
import subprocess

from protoslib import protos, exceptions
from circus import get_arbiter
from time import sleep

ENV_VARIABLES = {
    'WEBMAIL': 'rainloop',
    'WEB_WEBMAIL': '/webmail',
    'ADMIN': 'true',
    'WEB_ADMIN': '/admin',
    'HOSTNAMES': '', # set at runtime
    'DOMAIN': 'protos.io',
    'TLS_FLAVOR': 'cert',
    'RELAYNETS': '172.16.0.0/12',
    'MESSAGE_SIZE_LIMIT': '5000000',
    'FETCHMAIL_DELAY': '600',
    'RECIPIENT_DELIMITER': '+',
    'DMARC_RUA': 'admin',
    'DMARC_RUF': 'admin',
    'WELCOME': 'true',
    'WELCOME_SUBJECT': 'Welcome to your new Mailu email account',
    'WELCOME_BODY': 'Welcome to your new email account, if you can read this, then Mailu is configured properly and running on your Protos platform!',

    'HOST_REDIS': '127.0.0.1',
    'RATELIMIT_STORAGE_URL': 'redis://127.0.0.1',
    'HOST_ADMIN': '127.0.0.1:8080',
    'HOST_SMTP': 'smtp:11025',
    'HOST_AUTHSMTP': 'smtp:11026',
    'HOST_IMAP': 'imap:11143',
    'HOST_POP3': 'imap:11110',
    'HOST_WEBMAIL': '127.0.0.1',
    'HOST_ANTISPAM': '127.0.0.1:11334',
    'FRONT_ADDRESS': '127.0.0.1',
}

PROTOS_URL = 'http://172.17.0.3:9999/'
PROTOS_APP_ID = 'bb1pq5rj02j1hjk38j0g'


def set_proc_vars():
    rainloop_proc = {'name': 'rainloop', 'cmd': '/mailu/rainloop/start.sh', 'working_dir': '/var/www', 'numprocesses': 1}
    rsyslog_proc = {'name': 'rsyslog', 'cmd': '/usr/sbin/rsyslogd -n', 'working_dir': '/', 'numprocesses': 1}
    redis_proc = {'name': 'redis', 'cmd': '/usr/bin/redis-server', 'working_dir': '/', 'numprocesses': 1}
    nginx_proc = {'name': 'nginx', 'cmd': '/mailu/nginx/start.py', 'working_dir': '/mailu/nginx', 'numprocesses': 1, 'env': ENV_VARIABLES}
    mailu_proc = {'name': 'admin', 'cmd': '/mailu/admin/start.sh', 'working_dir': '/mailu/admin' ,'numprocesses': 1, 'env': ENV_VARIABLES}
    dovecot_proc = {'name': 'dovecot', 'cmd': '/mailu/dovecot/start.py', 'working_dir': '/mailu/dovecot' ,'numprocesses': 1, 'env': ENV_VARIABLES}
    postfix_proc = {'name': 'postfix', 'cmd': '/mailu/postfix/start.py', 'working_dir': '/mailu/postfix' ,'numprocesses': 1, 'env': ENV_VARIABLES}
    rspamd_proc = {'name': 'rspamd', 'cmd': '/mailu/rspamd/start.py', 'working_dir': '/mailu/rspamd' ,'numprocesses': 1, 'env': ENV_VARIABLES}

    # all_processes = [rainloop_proc, rsyslog_proc, nginx_proc, redis_proc, mailu_proc, dovecot_proc, postfix_proc, rspamd_proc]
    all_processes = [rsyslog_proc, nginx_proc, redis_proc, mailu_proc, postfix_proc, dovecot_proc, rainloop_proc]
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
    global ENV_VARIABLES
    ENV_VARIABLES['HOSTNAMES'] = app_info['name'] + '.' + domain

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