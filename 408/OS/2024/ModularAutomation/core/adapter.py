
import datetime
from FlowChartEngine.core.flow_chart import FlowChart
from FlowChartEngine.modules.console import console_close, console_login, console_read_until, console_send
from FlowChartEngine.modules.logger import log_handler_init, log_logger_init
from FlowChartEngine.modules.misc import timer_transience
import uuid


class Adapter(FlowChart):
    default_wait = '1.0'
    default_format = 'str'

    def __init__(self, logger_name):
        self.params_bus['console'] = {}
        self.params_bus['misc'] = {'timer': {}}
        self.params_bus['log'] = {'logger_name': logger_name, 'log_backup_count': 8192}
        self.params_bus = log_logger_init(params=self.params_bus)
        self.params_bus = log_handler_init(params=self.params_bus)

    def console_set_type(self, console_type):
        '''
        设置控制台类型，串口 SSH Telnet
        '''
        if console_type in ['ssh', 'serial', 'telnet']:
            self.params_bus['console']['console_type'] = console_type
            return True
        else:
            logger = self.params_bus['log']['logger']
            logger.error('还未设置控制台类型\n目前仅支持ssh、串口、telnet')
            return False

    def console_set_dut_ip(self, dut_ip):
        logger = self.params_bus['log']['logger']
        logger.info('SSH/Telnet控制台的IP设置为:{}'.format(dut_ip))
        if len(dut_ip.strip().split('.')) == 4:
            self.params_bus['console']['dut_ip'] = dut_ip
            return True
        else:
            logger.error('IP:{}不是有效的DUT IP'.format(dut_ip))
            return False

    def console_set_port(self, port):
        '''
        设置控制台的端口，串口的端口开头是COM，SSH和Telnet端口从1-65535
        '''
        logger = self.params_bus['log']['logger']
        logger.info('控制台的端口设置为:{}'.format(port))
        self.params_bus['console']['port'] = port
        return True

    def console_set_username(self, username):
        logger = self.params_bus['log']['logger']
        logger.info('控制台的用户名设置为:{}'.format(username))
        self.params_bus['console']['username'] = username
        return True

    def console_set_password(self, password):
        '''
        设置控制台的密码，用户名固定是root，要兼容不同用户名以后再说吧
        '''
        logger = self.params_bus['log']['logger']
        logger.info('控制台的密码设置为:{}'.format(password))
        ret = True
        if 'console_type' in self.params_bus['console'].keys():
            if self.params_bus['console']['console_type'] == 'serial':
                self.params_bus['console']['serial_pass'] = password
            elif self.params_bus['console']['console_type'] == 'ssh':
                self.params_bus['console']['ssh_pass'] = password
            elif self.params_bus['console']['console_type'] == 'telnet':
                self.params_bus['console']['telnet_pass'] = password
            else:
                logger.error('不支持的控制台类型:{}\n目前仅支持ssh、串口、telnet'.format(self.params_bus['console']['console_type']))
                ret = False
        else:
            logger.error('还未设置控制台类型\n目前仅支持ssh、串口、telnet')
            ret = False
        return ret

    def console_set_data_format(self, data_format):
        '''
        设置控制台回显的数据格式，可以直接返回字节串解码（防止不同编码导致的解码错误）
        设为str返回字符串，设为bytes返回字节串
        '''
        logger = self.params_bus['log']['logger']
        logger.info('控制台的回显字符串数据格式设置为:{}'.format(data_format))
        if data_format in ['str', 'bytes']:
            self.params_bus['console']['format'] = data_format
            return True
        else:
            logger.error('未定义的回显字符串的数据格式:{}\n仅限bytes和str'.format(data_format))
            return False

    def console_set_wait(self, wait):
        '''
        设置控制台回显的等待时长，兼容float和str传入
        '''
        logger = self.params_bus['log']['logger']
        logger.info('控制台的回显等待时长设置为:{}'.format(wait))
        try:
            wait = float(wait)
            wait = str(wait)
        except Exception as e:
            logger.error('设置回显等待时长为:{}时发生错误:{}'.format(wait, repr(e)))
            logger.error('使用默认配置:{}'.format(Adapter.default_wait))
            wait = Adapter.default_wait
        self.params_bus['console']['wait'] = wait
        return True

    def console_set_send_string(self, send_string):
        '''
        设置控制台将要写入的命令（但不写入）
        '''
        logger = self.params_bus['log']['logger']
        logger.info('控制台即将发送的命令为:{}'.format(send_string))
        try:
            send_string = str(send_string)
        except Exception as e:
            logger.error('设置发送的命令为:{}时发生错误:{}'.format(send_string, repr(e)))
            send_string = ''
        self.params_bus['console']['send_string'] = send_string
        return True

    def console_set_serial_baud_rate(self, baud_rate):
        '''
        设置串口控制台的波特率
        '''
        logger = self.params_bus['log']['logger']
        logger.info('串口控制台的波特率设置为:{}'.format(baud_rate))
        self.params_bus['console']['baud_rate'] = baud_rate
        return True

    def console_set_serial_do_login(self, do_login=False):
        '''
        设置是否在连接后进行登录（仅限串口）
        '''
        logger = self.params_bus['log']['logger']
        logger.info('串口控制台的是否登录?:{}'.format(do_login))
        if do_login:
            self.params_bus['console']['serial_type'] = 'RJ'
        else:
            self.params_bus['console']['serial_type'] = 'NL'
        return True

    def console_do_login(self):
        '''
        连接（登录）控制台
        '''
        logger = self.params_bus['log']['logger']
        if 'console_type' in self.params_bus['console']:
            try:
                self.params_bus = console_login(params=self.params_bus)
                if self.params_bus['console']['exception'] is None:
                    return True
                else:
                    logger.error('串口连接时发生错误:{}'.format(repr(self.params_bus['console']['exception'])))
                    return False
            except Exception as e:
                logger.error('串口连接时发生非预期错误:{}'.format(repr(e)))
                return False

    def console_do_send_string(self, no_echo=False):
        '''
        将已经设置好要发送的命令发送出去并（自动）记录回显到日志中
        no_echo为True时不读取回显，发完结束动作
        '''
        logger = self.params_bus['log']['logger']
        if 'send_string' in self.params_bus['console'].keys():
            self.params_bus['console']['read_echo'] = not no_echo
            self.params_bus = console_send(params=self.params_bus)
            if 'echo_string' in self.params_bus['console'].keys():
                if self.params_bus['console']['exception'] is None:
                    logger.info('回显记录:{}'.format(self.params_bus['console']['echo_string']))
                    return True
                else:
                    logger.error('上一串口动作发生错误:{}'.format(repr(self.params_bus['console']['exception'])))
                    return False
            else:
                logger.error('回显为空')
                return False
        else:
            logger.error('发送的命令还未设置')
            return False

    def console_do_read_until(self, wait_string, echo_string_ptr, t_table_ptr, dt_ptr, wait_timeout=None):
        '''
        仅返回错误状态版的【持续读取直到读到指定内容】
        wait_string: 读到这个内容才停止
        echo_string_ptr: 停止前读取的全部回显
        t_table_ptr: 计时用的临时时间表
        dt_ptr: 到停止为止消耗的时间
        wait_timeout: 超过这个时间就不继续等了，默认None意思是等到天荒地老
        '''
        logger = self.params_bus['log']['logger']
        echo_string_ptr.clear()
        t_table_ptr.clear()
        dt_ptr.clear()
        try:
            self.params_bus['console']['wait_string'] = wait_string
            self.params_bus['console']['wait_timeout'] = wait_timeout
            if not self.timer_set():
                logger.error('记录开始时间时发生错误')
                return False
            t_name = self.params_bus['misc']['timer']['t_name']
            self.params_bus = console_read_until(params=self.params_bus)
            if not self.timer_set(t_name=t_name):
                logger.error('记录结束时间时发生错误')
                return False
            if not self.timer_get(t_name=t_name, t_table_ptr=t_table_ptr):
                logger.error('获取起止时间时发生错误')
                return False
            t2 = t_table_ptr.pop(-1)
            t1 = t_table_ptr.pop(-1)
            if not self.timer_calc(t1=t1, t2=t2, dt_ptr=dt_ptr):
                logger.error('计算时间差时发生错误')
                return False
            if not self.timer_delete(t_name=t_name):
                logger.error('删除临时时间表时发生错误')
                return False
            if not self.console_get_echo_string(echo_string_ptr=echo_string_ptr):
                logger.error('获取回显字符串时发生错误')
                return False
            success = True
        except Exception as e:
            logger.error('发生非预期错误:{}'.format(repr(e)))
            success = False
        return success

    def console_do_read_until_in_ret(self, wait_string, wait_timeout=None):
        '''
        【持续读取直到读到指定内容】结果从return返回版
        参数含义参考console_do_read_until
        '''
        echo_string_ptr = []
        t_table_ptr = []
        dt_ptr = []
        success = self.console_do_read_until(
            wait_string=wait_string,
            echo_string_ptr=echo_string_ptr,
            t_table_ptr=t_table_ptr,
            dt_ptr=dt_ptr,
            wait_timeout=wait_timeout
        )
        return success, echo_string_ptr, t_table_ptr, dt_ptr

    def console_do_close(self):
        self.params_bus = console_close(params=self.params_bus)
        return True

    def console_get_echo_string(self, echo_string_ptr, split_lines=None):
        '''
        读取控制台显示的内容，传入一个空list到echo_string_ptr
        执行完毕后，echo_string_ptr会装有控制台显示的内容
        split_lines被设置为换行字符串时，echo_string_ptr是以行切分的list
        '''
        logger = self.params_bus['log']['logger']
        echo_string_ptr.clear()
        if 'echo_string' in self.params_bus['console'].keys():
            echo_string = self.params_bus['console']['echo_string']
            if split_lines is not None:
                echo_string = echo_string.split(split_lines)
            else:
                echo_string = [echo_string]
            for line in echo_string:
                echo_string_ptr.append(line)
            return True
        else:
            logger.error('回显为空')
            _ = echo_string_ptr
            return False

    def console_get_echo_string_in_ret(self, split_lines=None):
        '''
        回显读取，echo_string_ptr不需要传入，从return的地方传出的版本
        '''
        echo_string_ptr = []
        success = self.console_get_echo_string_std_ret(echo_string_ptr=echo_string_ptr, split_lines=split_lines)
        return success, echo_string_ptr

    def console_send_and_recv(self, send_string, echo_string_ptr, split_lines=None, wait=None, data_format=None):
        '''
        发送并立刻读取回显的整套操作
        如果还没连接（登录）到当前console_type设定的控制台
        会自动进行连接（登录）（但不会检测已存在的控制台对象是否已close）
        '''
        if wait is None:
            wait = Adapter.default_wait
        if data_format is None:
            data_format = Adapter.default_format
        if not self.console_set_wait(wait=wait):
            return False
        if not self.console_set_data_format(data_format=data_format):
            return False
        if self.params_bus['console']['console_type'] not in self.params_bus['console'].keys():
            if not self.console_do_login():
                return False
        if not self.console_set_send_string(send_string=send_string):
            return False
        if not self.console_do_send_string():
            return False
        if not self.console_get_echo_string(echo_string_ptr=echo_string_ptr, split_lines=split_lines):
            return False

    def console_send_and_recv_in_ret(self, send_string, split_lines=None, wait=None, data_format=None):
        '''
        发完立刻读取，echo_string_ptr不需要传入，从return的地方传出的版本
        '''
        echo_string_ptr = []
        success = self.console_send_and_recv(
            send_string=send_string,
            echo_string_ptr=echo_string_ptr,
            split_lines=split_lines,
            wait=wait,
            data_format=data_format
        )
        return success, echo_string_ptr

    def timer_set(self, t_name=None, t_desc=None):
        '''
        记录当前时刻到t_name的表当中
        t_desc可以设置一个字符串用来描述这个时刻点的含义
        t_name如果不设置会自动生成一个uuid
        '''
        logger = self.params_bus['log']['logger']
        if t_name is None:
            t_name = str(uuid.uuid4())
        self.params_bus['misc']['timer']['t_name'] = t_name
        if t_desc is not None:
            self.params_bus['misc']['timer']['t_desc'] = t_desc
        try:
            self.params_bus = timer_transience(params=self.params_bus)
            if self.params_bus['misc']['exception'] is None:
                return True
            else:
                return False
        except Exception as e:
            logger.error('打点计时器记录新时刻时发生错误:{}'.format(repr(e)))
            return False

    def timer_get(self, t_name, t_table_ptr):
        '''
        获取名为t_name的时刻表
        传入一个空list到t_table_ptr
        执行完毕后，t_table_ptr会装有时刻表的内容
        '''
        logger = self.params_bus['log']['logger']
        t_table_ptr.clear()
        if t_name in self.params_bus['misc']['timer']['t_table'].keys():
            for t in self.params_bus['misc']['timer']['t_table'][t_name]:
                t_table_ptr.append(t)
            return True
        else:
            logger.error('时刻总表t_table找不到行索引为:{}的时刻表'.format(t_name))
            return False

    def timer_clear(self, t_name):
        '''
        清空名为t_name的时刻表
        '''
        logger = self.params_bus['log']['logger']
        if t_name in self.params_bus['misc']['timer']['t_table'].keys():
            self.params_bus['misc']['timer']['t_table'][t_name].clear()
            logger.info('时刻总表t_table已清空行索引为:{}的时刻表'.format(t_name))
            return True
        else:
            logger.error('时刻总表t_table找不到行索引为:{}的时刻表'.format(t_name))
            return False

    def timer_delete(self, t_name):
        '''
        删掉名为t_name的时刻表
        '''
        logger = self.params_bus['log']['logger']
        if t_name in self.params_bus['misc']['timer']['t_table'].keys():
            del self.params_bus['misc']['timer']['t_table'][t_name]
            logger.info('时刻总表t_table已删除行索引为:{}的时刻表'.format(t_name))
            return True
        else:
            logger.error('时刻总表t_table找不到行索引为:{}的时刻表'.format(t_name))
            return False

    def timer_get_in_ret(self, t_name):
        '''
        获取时刻表，t_table_ptr不需要传入，从return的地方传出的版本
        '''
        t_table_ptr = []
        success = self.timer_get(t_name=t_name, t_table_ptr=t_table_ptr)
        return success, t_table_ptr

    def timer_calc(self, t1, t2, dt_ptr, with_desc=True, format_str=None):
        '''
        计算t1和t2的时间差
        传入一个空list到dt_ptr
        执行完毕后，dt_ptr会装有时间差结果
        如果传入的t1和t2是带有描述文本的（[t,t_desc_str]这样长度为2的list，也是t_table[t_name]列表中一个元素的格式）
        with_desc需要设置为True，会把t从[t,t_desc_str]里剥离出来计算
        format_str为空时，计算结果直接是datetime.timedelta对象
        如果设置为strftime适配的时间戳格式字符串，会生成对应的时间戳字符串
        '''
        logger = self.params_bus['log']['logger']
        dt_ptr.clear()
        try:
            if with_desc:
                t1: datetime.datetime = t1[0]
                t2: datetime.datetime = t2[0]
            dt: datetime.timedelta = t2 - t1
            if format_str is not None:
                st = datetime.datetime(0, 0, 0, 0, 0, 0, 0)
                et = st + dt
                dt = et.strftime(format=format_str)
            dt_ptr.append(dt)
            return True
        except Exception as e:
            logger.error('计算{}和{}的时间差时发生错误:{}'.format(t1, t2, repr(e)))
            return False

    def timer_calc_in_ret(self, t1, t2, with_desc=True, format_str=None):
        dt_ptr = []
        success = self.timer_calc(t1=t1, t2=t2, dt_ptr=dt_ptr, with_desc=with_desc, format_str=format_str)
        return success, dt_ptr

    def log_get_logger(self, logger_ptr):
        '''
        获取日志接口
        类型：logging.Logger
        使用方法：
        logger.info('消息')
        logger.warn('警告')
        logger.error('错误')
        '''
        logger_ptr.clear()
        logger = self.params_bus['log']['logger']
        logger_ptr.append(logger)
        return True

    def log_get_logger_in_ret(self):
        '''
        获取日志接口，从return返回
        类型：logging.Logger
        使用方法：
        logger.info('消息')
        logger.warn('警告')
        logger.error('错误')
        '''
        logger_ptr = []
        success = self.log_get_logger(logger_ptr=logger_ptr)
        return success, logger_ptr[0]
