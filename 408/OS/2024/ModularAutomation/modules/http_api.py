import json

import requests


def http_post(params):
    http_post_url = params['http']['url']
    del params['http']['url']
    post_dict = {
        'url': http_post_url,
        'verify': False
    }
    if 'params' in params['http'].keys():
        post_dict['params'] = params['http']['params']
        del params['http']['params']
    if 'data' in params['http'].keys():
        if 'data_format' in params['http'].keys():
            if params['http']['data_format'] == 'url_encoded':
                post_dict['data'] = params['http']['data']
            else:
                raise NotImplementedError
            del params['http']['data_format']
        else:
            post_dict['data'] = json.dumps(params['http']['data'], ensure_ascii=False).encode("utf-8")
        del params['http']['data']
    if 'headers' in params['http'].keys():
        post_dict['headers'] = params['http']['headers']
    if 'timeout' in params['http'].keys():
        post_dict['timeout'] = params['http']['timeout']
    if 'allow_redirects' in params['http'].keys():
        post_dict['allow_redirects'] = params['http']['allow_redirects']
    response = requests.post(**post_dict)
    if response.status_code in [200, 201, 302]:
        if 'raw' in params['http'].keys() and params['http']['raw']:
            del params['http']['raw']
            params['http']['response'] = response
        else:
            params['http']['response'] = json.loads(response.content.decode('utf-8'))
    else:
        params['http']['response'] = response.status_code
    return params


def http_get(params):
    http_get_url = params['http']['url']
    del params['http']['url']
    get_dict = {
        'url': http_get_url,
        'verify': False
    }
    if 'params' in params['http'].keys():
        get_dict['params'] = params['http']['params']
        del params['http']['params']
    if 'data' in params['http'].keys():
        if 'data_format' in params['http'].keys():
            if params['http']['data_format'] == 'url_encoded':
                get_dict['data'] = params['http']['data']
            else:
                raise NotImplementedError
            del params['http']['data_format']
        else:
            get_dict['data'] = json.dumps(params['http']['data'], ensure_ascii=False).encode("utf-8")
        del params['http']['data']
    if 'headers' in params['http'].keys():
        get_dict['headers'] = params['http']['headers']
    if 'timeout' in params['http'].keys():
        get_dict['timeout'] = params['http']['timeout']
    response = requests.get(**get_dict)
    if response.status_code in [200, 201, 302]:
        if 'download_as' in params['http'].keys():
            with open(params['http']['download_as'], 'wb') as f:
                f.write(response.content)
            del params['http']['download_as']
        else:
            if 'raw' in params['http'].keys() and params['http']['raw']:
                del params['http']['raw']
                params['http']['response'] = response
            else:
                params['http']['response'] = json.loads(response.content.decode('utf-8'))
    else:
        params['http']['response'] = response.status_code
    return params


def http_delete(params):
    http_delete_url = params['http']['url']
    del params['http']['url']
    delete_dict = {
        'url': http_delete_url,
        'verify': False
    }
    if 'params' in params['http'].keys():
        delete_dict['params'] = params['http']['params']
        del params['http']['params']
    if 'data' in params['http'].keys():
        if 'data_format' in params['http'].keys():
            if params['http']['data_format'] == 'url_encoded':
                delete_dict['data'] = params['http']['data']
            else:
                raise NotImplementedError
            del params['http']['data_format']
        else:
            delete_dict['data'] = json.dumps(params['http']['data'])
        del params['http']['data']
    if 'headers' in params['http'].keys():
        delete_dict['headers'] = params['http']['headers']
    if 'timeout' in params['http'].keys():
        delete_dict['timeout'] = params['http']['timeout']
    response = requests.delete(**delete_dict)
    if response.status_code in [200, 201, 302]:
        if 'raw' in params['http'].keys() and params['http']['raw']:
            del params['http']['raw']
            params['http']['response'] = response
        else:
            params['http']['response'] = json.loads(response.content.decode('utf-8'))
    else:
        params['http']['response'] = response.status_code
    return params


if __name__ == '__main__':
    print('Done')
