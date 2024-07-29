import time
from modules.console import console_login, console_send
from modules.console_parsers.ate_rx_stat import ATERXStat


def console_iwpriv_set(params):
    ap_cli = params['console']['ap_cli']
    iwpriv_key = params['console']['iwpriv_key']
    iwpriv_val = params['console']['iwpriv_val']
    params['console']['send_string'] = 'iwpriv {} set {}={}'.format(ap_cli, iwpriv_key, iwpriv_val)
    params['console']['format'] = 'str'
    params['console']['wait'] = 0.1
    params = console_send(params=params)
    return params


def console_ate_start(params):
    params['console']['iwpriv_key'] = 'ATE'
    params['console']['iwpriv_val'] = 'ATESTART'
    params = console_iwpriv_set(params=params)
    return params


def console_ate_stop(params):
    params['console']['iwpriv_key'] = 'ATE'
    params['console']['iwpriv_val'] = 'ATESTOP'
    params = console_iwpriv_set(params=params)
    return params


def console_ate_rx_set(params):
    params['console']['iwpriv_key'] = 'ATECTRLBANDIDX'
    params['console']['iwpriv_val'] = 0
    params = console_iwpriv_set(params=params)
    params['console']['iwpriv_key'] = 'ResetCounter'
    params['console']['iwpriv_val'] = 0
    params = console_iwpriv_set(params=params)
    rx_params = params['rf_test_params']['rx']
    for key in rx_params['set_order']:
        val = rx_params[key]
        params['console']['iwpriv_key'] = key
        params['console']['iwpriv_val'] = val
        params = console_iwpriv_set(params=params)
    return params


def console_ate_tx_set(params):
    params = console_ate_tx_stop(params=params)
    rx_params = params['rf_test_params']['rx']
    for key in rx_params['set_order']:
        val = rx_params[key]
        params['console']['iwpriv_key'] = key
        params['console']['iwpriv_val'] = val
        params = console_iwpriv_set(params=params)
    tx_params = params['rf_test_params']['tx']
    for key in tx_params['set_order']:
        val = tx_params[key]
        params['console']['iwpriv_key'] = key
        params['console']['iwpriv_val'] = val
        params = console_iwpriv_set(params=params)
    params['console']['iwpriv_key'] = 'ATE'
    params['console']['iwpriv_val'] = 'TXCOMMIT'
    params = console_iwpriv_set(params=params)
    return params


def console_ate_rx_start(params):
    params['console']['iwpriv_key'] = 'ATE'
    params['console']['iwpriv_val'] = 'RXFRAME'
    params = console_iwpriv_set(params=params)
    return params


def console_ate_tx_start(params):
    params['console']['iwpriv_key'] = 'ATE'
    params['console']['iwpriv_val'] = 'TXFRAME'
    params = console_iwpriv_set(params=params)
    return params


def console_ate_rx_stop(params):
    params['console']['iwpriv_key'] = 'ATE'
    params['console']['iwpriv_val'] = 'RXSTOP'
    params = console_iwpriv_set(params=params)
    return params


def console_ate_tx_stop(params):
    params['console']['iwpriv_key'] = 'ATE'
    params['console']['iwpriv_val'] = 'TXSTOP'
    params = console_iwpriv_set(params=params)
    return params


def console_ate_rx_clear_counter(params):
    params['console']['iwpriv_key'] = 'ATERXSTATRESET'
    params['console']['iwpriv_val'] = 0
    params = console_iwpriv_set(params=params)
    return params


def console_ate_rx_read(params):
    params['console']['format'] = 'str'
    params['console']['wait'] = 1
    params['console']['send_string'] = 'clear'
    params = console_send(params=params)
    params['console']['send_string'] = 'dmesg -c > /dev/null'
    params = console_send(params=params)
    params['console']['iwpriv_key'] = 'ATERXSTAT'
    params['console']['iwpriv_val'] = 0
    params = console_iwpriv_set(params=params)
    params['console']['send_string'] = 'dmesg -c | grep set_ate_show_rx_stat -A22'
    params['console']['wait'] = 5
    params = console_send(params=params)
    params['rf_test_params']['rx_stat_raw'] = params['console']['echo_string']
    params['rf_test_params']['rx_stat'] = ATERXStat(text=params['rf_test_params']['rx_stat_raw'])
    return params


if __name__ == '__main__':
    params_ = {
        'console': {
            'console_type': 'ssh',
            'dut_ip': '192.168.110.1',
            'ssh_pass': '1b762f4ae9e6a903',
            'ap_cli': 'ra0'
        },
        'rf_test_params': {
            'rx': {
                # use in rx
                'set_order': ['ATETXBW', 'ATETXANT', 'ATERXANT', 'ATETXMODE', 'ATETXMCS', 'ATECHANNEL'],
                'ATETXBW': 0,
                'ATETXANT': 7,
                'ATERXANT': 7,
                'ATETXMODE': 1,
                'ATETXMCS': 7,
                'ATECHANNEL': 1
            },
            'tx': {
                # use in tx
                'set_order': ['ATEDA', 'ATESA', 'ATEBSSID', 'ATETXGI', 'ATETXCNT', 'ATETXLEN', 'ATETXPOW0'],
                'ATEDA': '00:11:22:33:44:55',
                'ATESA': '00:aa:bb:cc:dd:ee',
                'ATEBSSID': '00:11:22:33:44:55',
                'ATETXGI': 1,
                'ATETXCNT': 10000,
                'ATETXLEN': 1024,
                'ATETXPOW0': 63
            }
        }
    }
    params_ = console_login(params=params_)
    params_ = console_ate_start(params=params_)
    params_ = console_ate_rx_set(params=params_)
    params_ = console_ate_rx_clear_counter(params=params_)
    params_ = console_ate_rx_start(params=params_)
    time.sleep(5)
    params_ = console_ate_rx_read(params=params_)
    print('Done')
