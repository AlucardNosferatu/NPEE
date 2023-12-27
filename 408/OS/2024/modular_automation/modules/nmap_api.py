import json
import threading
import time

import nmap


def nmap_init(params: dict):
    port_scanner = nmap.PortScanner()
    params['nmap']['port_scanner'] = port_scanner
    return params


def nmap_scan(params: dict):
    def scan_async(hosts, ports, arguments, p_container_, nmap_scan_result_):
        p_container_.clear()
        nmap_scan_result_.clear()
        # noinspection PyArgumentList
        result = port_scanner.scan(
            hosts=hosts, ports=ports, arguments=arguments, p_container=p_container_
        )
        nmap_scan_result_.append(result)

    nmap_scan_params = params['nmap']
    port_scanner: nmap.PortScanner = nmap_scan_params['port_scanner']
    nmap_scan_host = nmap_scan_params['scan_host']
    del nmap_scan_params['scan_host']
    nmap_scan_port = nmap_scan_params['scan_port']
    del nmap_scan_params['scan_port']
    nmap_scan_args = nmap_scan_params['scan_args']
    del nmap_scan_params['scan_args']
    p_container = []
    nmap_scan_result = []
    scan_thread = threading.Thread(
        target=scan_async,
        args=(nmap_scan_host, nmap_scan_port, nmap_scan_args, p_container, nmap_scan_result)
    )
    scan_thread.start()
    if 'async' in nmap_scan_params.keys() and nmap_scan_params['async']:
        nmap_scan_params['async_process'] = p_container
        nmap_scan_params['async_result'] = nmap_scan_result
        return params
    else:
        while len(p_container) <= 0:
            time.sleep(0.5)
        print('NMAP starts scanning.')
        while len(nmap_scan_result) <= 0:
            print('NMAP is scanning...')
            time.sleep(10)
        scan_thread.join()
        result_dict = nmap_scan_result[0]
        nmap_scan_params['scan_result'] = result_dict
        result_txt = json.dumps(obj=result_dict, indent=4)
        if 'save_txt' in nmap_scan_params.keys():
            with open(nmap_scan_params['save_txt'], 'w') as f:
                f.writelines(result_txt)
        return params


if __name__ == '__main__':
    print('Done')
