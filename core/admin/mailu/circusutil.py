from circus.client import CircusClient
from circus.util import DEFAULT_ENDPOINT_SUB, DEFAULT_ENDPOINT_DEALER

def get_services():
    client = CircusClient(endpoint=DEFAULT_ENDPOINT_DEALER)
    get_watchers_cmd = {'command': 'list'}
    watchers = client.call(get_watchers_cmd)
    get_procs_cmd = {'command': 'list', 'properties': {}}
    services = {}
    for watcher in watchers['watchers']:
        get_proc_cmd = {'command': 'list', 'properties': {'name': watcher}}
        proc = client.call(get_proc_cmd)
        services[watcher] = {'status': proc['status'], 'pid': ','.join([str(pid) for pid in proc['pids']])}
    return services