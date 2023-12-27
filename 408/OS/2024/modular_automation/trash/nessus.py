from modules.http_api import http_post, http_get, http_delete

# 穷逼没资格搞自动化！
# noinspection SpellCheckingInspection
access_key = '9e3e3f3a16806dfbf42a396cf4499d54ec1873dee7b2975d5365275a9b6b8ee1'
secret_key = '859ce3d40de149e47d74af77cb90a5194f863256c94cc138d0b8519fa42eb2a6'
nessus_host = '172.28.15.253'
nessus_port = 8834
default_folder = 'My Scans'
default_template = 'advanced'
base_url = "https://{}:{}/".format(nessus_host, nessus_port)
nessus_header = {
    'X-ApiKeys': 'accessKey={};secretKey={}'.format(access_key, secret_key),
    'Content-type': 'application/json',
    'Accept': 'text/plain'
}


def nessus_post(params):
    nessus_post_params = params['nessus']
    api = nessus_post_params['api']
    del nessus_post_params['api']
    params['http'] = {}
    params['http']['headers'] = nessus_header
    params['http']['url'] = "{}{}".format(base_url, api)
    if 'data' in nessus_post_params.keys():
        params['http']['data'] = nessus_post_params['data']
        del nessus_post_params['data']
    if 'params' in nessus_post_params.keys():
        params['http']['params'] = nessus_post_params['params']
        del nessus_post_params['params']
    params = http_post(params=params)
    return params


def nessus_get(params):
    nessus_get_params = params['nessus']
    api = nessus_get_params['api']
    del nessus_get_params['api']
    params['http'] = {}
    params['http']['headers'] = nessus_header
    params['http']['url'] = "{}{}".format(base_url, api)
    if 'data' in nessus_get_params.keys():
        params['http']['data'] = nessus_get_params['data']
        del nessus_get_params['data']
    if 'params' in nessus_get_params.keys():
        params['http']['params'] = nessus_get_params['params']
        del nessus_get_params['params']
    params = http_get(params=params)
    return params


def nessus_delete(params):
    nessus_delete_params = params['nessus']
    api = nessus_delete_params['api']
    del nessus_delete_params['api']
    params['http'] = {}
    params['http']['headers'] = nessus_header
    params['http']['url'] = "{}{}".format(base_url, api)
    if 'data' in nessus_delete_params.keys():
        params['http']['data'] = nessus_delete_params['data']
        del nessus_delete_params['data']
    if 'params' in nessus_delete_params.keys():
        params['http']['params'] = nessus_delete_params['params']
        del nessus_delete_params['params']
    params = http_delete(params=params)
    return params


def nessus_get_template_uuid(params):
    if 'template_name' in params['nessus'].keys():
        template_name = params['nessus']['template_name']
        del params['nessus']['template_name']
    else:
        template_name = default_template
    params['nessus']['api'] = 'editor/scan/templates'
    params = nessus_get(params=params)
    response = params['http']['response']
    del params['http']['response']
    params['nessus']['template_uuid'] = None
    if response is not int:
        templates = response['templates']
        for template in templates:
            if template['name'] == template_name:
                params['nessus']['template_uuid'] = template['uuid']
                break
    return params


def nessus_get_folder_id(params):
    if 'folder_name' in params['nessus'].keys():
        folder_name = params['nessus']['folder_name']
        del params['nessus']['folder_name']
    else:
        folder_name = default_folder
    params['nessus']['api'] = 'scans'
    params = nessus_get(params=params)
    response = params['http']['response']
    del params['http']['response']
    params['nessus']['folder_id'] = None
    if response is not int:
        folders = response['folders']
        for folder in folders:
            if folder['name'] == folder_name:
                params['nessus']['folder_id'] = folder['id']
                break
    return params


def nessus_get_scan_id(params):
    scan_name = params['nessus']['scan_name']
    del params['nessus']['scan_name']
    params = nessus_get_folder_id(params=params)
    folder_id = params['nessus']['folder_id']
    del params['nessus']['folder_id']
    params['nessus']['scan_id'] = None
    if folder_id is None:
        return params
    params['nessus']['data'] = {'folder_id': folder_id}
    params['nessus']['api'] = 'scans'
    params = nessus_get(params=params)
    response = params['http']['response']
    del params['http']['response']
    if response is not int:
        scans = response['scans']
        for scan in scans:
            if scan['name'] == scan_name:
                params['nessus']['scan_id'] = scan['id']
                break
    return params


def nessus_post_new_scan(params):  # host 是一个列表，存放的是需要扫描的多台主机
    scan_name = params['nessus']['scan_name']
    del params['nessus']['scan_name']

    scan_hosts = params['nessus']['scan_hosts']
    del params['nessus']['scan_hosts']

    params = nessus_get_folder_id(params=params)
    folder_id = params['nessus']['folder_id']
    del params['nessus']['folder_id']
    params['nessus']['scan_id'] = None
    if folder_id is None:
        return params

    params = nessus_get_template_uuid(params=params)
    template_uuid = params['nessus']['template_uuid']
    del params['nessus']['template_uuid']
    params['nessus']['scan_id'] = None
    if template_uuid is None:
        return params

    params['nessus']['data'] = {
        "uuid": template_uuid,
        "settings": {
            "name": scan_name,
            'folder_id': folder_id,
            "enabled": True,
            "text_targets": scan_hosts,
            "agent_group_id": []
        }
    }
    params['nessus']['api'] = 'scans'
    params = nessus_post(params=params)
    response = params['http']['response']
    del params['http']['response']
    if response is not int:
        scan = response['scan']
        params['nessus']['scan_id'] = scan['id']
    return params


def nessus_delete_old_scan(params):
    # params['nessus']['scan_name'] = params['nessus']['scan_name']
    params = nessus_get_scan_id(params=params)
    scan_id = params['nessus']['scan_id']
    del params['nessus']['scan_id']
    if scan_id is None:
        return params
    params['nessus']['api'] = 'scans/{}'.format(scan_id)
    params = nessus_delete(params=params)
    return params


if __name__ == '__main__':
    params_ = {
        'nessus': {
            'scan_name': 'M18-R226'
        }
    }
    params_ = nessus_delete_old_scan(params=params_)
    print('Done')
