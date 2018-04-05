from mailu import app
from protoslib import exceptions


def create_resource(rsc_data):
    try:
        rsc = app.protos_client.create_resource(rsc_data)
    except exceptions.ProtosException as e:
        if "already registered" not in str(e):
            raise e
        else:
            rsc_id = str(e).split(' ')[1]
            rsc = app.protos_client.get_resource(rsc_id)
    return rsc

def create_spf_record():
    value = "v=spf1 mx a:{} -all".format(app.config["HOSTNAMES"].split(",")[0])
    dns_record = {'type': 'dns', 'value': {'host': '@', 'value': value, 'type': 'TXT', 'ttl': 600}}
    return create_resource(dns_record)

def create_dkim_record(dkim_publickey):
    value = "v=DKIM1; k=rsa; p={}".format(dkim_publickey)
    dns_record = {'type': 'dns', 'value': {'host': "{}._domainkey".format(app.config["DKIM_SELECTOR"]), 'value': value, 'type': 'TXT', 'ttl': 600}}
    return create_resource(dns_record)

def create_dmarc_record():
    value = "v=DMARC1; p=reject; rua=mailto:{}@{}; ruf=mailto:{}@{}; adkim=s; aspf=s".format(app.config['DMARC_RUA'], app.protos_domain, app.config['DMARC_RUF'], app.protos_domain)
    dns_record = {'type': 'dns', 'value': {'host': '_dmarc', 'value': value, 'type': 'TXT', 'ttl': 600}}
    return create_resource(dns_record)
