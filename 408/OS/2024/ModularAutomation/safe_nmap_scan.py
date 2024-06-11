import ipaddress
import os

from core.flow_chart import FlowChart


def is_valid_ipv4(ip_str):
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ipaddress.AddressValueError:
        return False


def is_valid_pr(pr_str, pr_list):
    pr_list.clear()
    try:
        start = int(pr_str.split('-')[0])
        end_ = int(pr_str.split('-')[1])
        pr_list.append(max(1, start))
        pr_list.append(min(65535, end_))
        valid = True
    except Exception as e:
        _ = e
        valid = False
    return valid


def is_valid_bs(bs_str, bs_ptr):
    bs_ptr.clear()
    try:
        assert int(bs_str) >= 1
        bs_ptr.append(int(bs_str))
        valid = True
    except Exception as e:
        _ = e
        valid = False
    return valid


if __name__ == '__main__':
    dut_ip = ''
    port_range = ''
    port_range_list = []
    batch_size = ''
    batch_size_ptr = []
    while not is_valid_ipv4(dut_ip):
        dut_ip = input('请输入有效的被测IP:')
    while not is_valid_pr(pr_str=port_range, pr_list=port_range_list):
        port_range = input('请输入端口范围:')
        if port_range == '':
            port_range = '1-65535'
    while not is_valid_bs(bs_str=batch_size, bs_ptr=batch_size_ptr):
        batch_size = input('多少个端口保存一次？')
        if batch_size == '':
            batch_size = '4096'
    batch_start = port_range_list[0]
    batch_end = batch_start + batch_size_ptr[0] - 1
    total_end = port_range_list[1]
    if batch_end > total_end:
        batch_end = total_end
    while batch_start <= total_end:
        params = {'nmap': {}}
        params['nmap']['scan_host'] = dut_ip
        params['nmap']['save_txt'] = 'reports/{}_P{}-{}.json'.format(
            params['nmap']['scan_host'], batch_start, batch_end
        )
        params['nmap']['scan_port'] = '{}-{}'.format(batch_start, batch_end)
        print('扫描端口区间：{}'.format(params['nmap']['scan_port']))
        fc = FlowChart(prerequisite=params)
        fc.load_map(hook_script='nmap_scan.py', map_json='NMAP端口扫描测试.pos')
        end = False
        while not end:
            end = fc.run_step()
        batch_start = batch_end + 1
        batch_end = batch_start + batch_size_ptr[0] - 1
        if batch_end > total_end:
            batch_end = total_end
    os.abort()
