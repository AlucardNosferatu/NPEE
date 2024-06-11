def h0(params):
    scan_udp, scan_tcp = True, True
    params['nmap']['scan_args'] = '-A -T4 -v -Pn{}{}'.format(
        {True: ' -sU', False: ''}[scan_udp], {True: ' -sT', False: ''}[scan_tcp]
    )
    return params


def h1(params):
    return params
