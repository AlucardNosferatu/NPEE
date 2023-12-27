import lupa.lua54

from modules.console import console_login, console_send

lua = lupa.lua54.LuaRuntime()


def lua_func_wrapper(params):
    lua_code = params['lua']['lua_code']
    func_name = lua_code.split('\n')[1].strip().split(' ')[1].split('(')[0]
    # noinspection SpellCheckingInspection
    exec(r"{}=lua_code+';\nreturn {}'".format(func_name, func_name))
    exec("{}=lua.execute({})".format(func_name, func_name))
    if 'func_dict' not in params['lua'].keys():
        params['lua']['func_dict'] = {}
    params['lua']['func_dict'][func_name] = eval(func_name)
    return params


def lua_func_execute(params):
    func_name = params['lua']['func_name']
    func_args = params['lua']['func_args']
    i = 0
    args_str = []
    # noinspection PyUnusedLocal
    for arg in func_args:
        exec('arg{}=arg'.format(i))
        args_str.append('arg{}'.format(i))
        i += 1
    args_str = ','.join(args_str)
    # noinspection PyUnusedLocal
    func = params['lua']['func_dict'][func_name]
    result = eval('func({})'.format(args_str))
    params['lua']['result'] = result
    return params


if __name__ == '__main__':
    # todo: simplify modification process
    lc = r'''
    function filterExecShell(str)
        return string.gsub(str, "([\n\r`&$;|><])", "\\%1")
    end
    '''
    lc2 = '''
    function startCheck(params,filterExecShell,c_send)
        params.isLanPing = filterExecShell(params.isLanPing)
        params.isWanPing = filterExecShell(params.isWanPing)
        local res = c_send(string.format('echo "%s" "%s"',params.isLanPing,params.isWanPing))
        return res
    end
    '''

    lc3 = '''
    function curl_shell(host, md5)
        local shell = "curl '"..host.."' -H 'Authorization: "..md5.."' -H 'Req-From: mobile'"
        return shell
    end
    '''
    host = 'http://192.168.110.229:20290/%E5%9B%BD%E5%86%85/H20M-R226/%E8%AE%BE%E5%A4%87%E4%BF%A1%E6%81%AF.txt'
    lc4 = '''
    function getMd5(sn, ip, c_send)
        local time = os.time()
        local shell = "echo -n '"..time..sn..ip.."' |/usr/sbin/rg_crypto -t A|cut -d ' ' -f1"
        return c_send(shell)
    end
    '''
    sn = 'G1RUBGA002337'
    ip = '192.168.110.229:20290'
    params_ = {
        'console': {
            'console_type': 'ssh',
            'dut_ip': '192.168.110.1',
            'ssh_pass': '57e541f69676ce62'
        }, 'lua': {}
    }


    def console_send_lite(cmd_str):
        global params_
        params_['console']['send_string'] = cmd_str
        params_['console']['format'] = 'str'
        params_['console']['wait'] = 5
        params_ = console_send(params=params_)
        return params_['console']['echo_string']


    params_ = console_login(params=params_)

    params_['lua']['lua_code'] = lc4
    params_ = lua_func_wrapper(params=params_)
    params_['lua']['func_name'] = 'getMd5'
    # noinspection PyTypeChecker
    params_['lua']['func_args'] = [sn, ip, console_send_lite]
    params_ = lua_func_execute(params=params_)
    md5 = params_['lua']['result']
    md5 = md5.split('\r\n')[3]
    params_['lua']['lua_code'] = lc3
    params_ = lua_func_wrapper(params=params_)
    params_['lua']['func_name'] = 'curl_shell'
    # noinspection PyTypeChecker
    params_['lua']['func_args'] = [host, md5]
    params_ = lua_func_execute(params=params_)
    cs = params_['lua']['result']
    print(cs)
