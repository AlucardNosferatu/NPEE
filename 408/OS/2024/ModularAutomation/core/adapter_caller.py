# 操作Adapter的范例
import time

from FlowChartEngine.core.adapter import Adapter


if __name__ == '__main__':
    adapter = Adapter(logger_name='FactoryTest')
    # 初始化接口，入参为日志存放在logs下的文件夹名称，可填可不填
    adapter.console_set_type(console_type='telnet')
    adapter.console_set_dut_ip(dut_ip='192.168.110.1')
    adapter.console_set_port(port=23)
    adapter.console_set_password(password='abcdefg')
    # 配置控制台类型、IP地址、端口号、登陆密码
    adapter.console_do_login()
    # 连接并登录控制台
    success, echo_string = adapter.console_send_and_recv_in_ret(send_string='uci show sysinfo', wait='2.0')
    # 发送uci show sysinfo等待2秒后读取回显echo_string
    adapter.timer_set(t_name='uci')
    # 打点计时，时刻1记录在名为uci的时刻表上
    time.sleep(2)
    adapter.timer_set(t_name='uci')
    # 打点计时，时刻2记录在名为uci的时刻表上
    success, time_list = adapter.timer_get_in_ret(t_name='uci')
    # 获取名为uci的时刻表
    success, echo_string_ptr, t_table_ptr, dt_ptr = adapter.console_do_read_until_in_ret(
        wait_string='upinit_finished', wait_timeout=30
    )
    # 直到读取到upinit_finished为止，持续监听控制台，30秒内如果没读到就放弃
    # 期间读取到的控制台回显为echo_string_ptr
    # 开始读取到结束读取的计时时刻表t_table_ptr
    # 开始到结束的计时dt_ptr
    success, logger = adapter.log_get_logger_in_ret()
    # 获取日志记录器
    logger.info('演示进行中')
    logger.warn('警告')
    logger.error('错误')
    # 手动调用日志记录器写入日志
