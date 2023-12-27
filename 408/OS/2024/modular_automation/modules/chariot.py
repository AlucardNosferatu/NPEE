#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import threading
import time

import cv2
import mss
import numpy
import psutil as psutil
import pythoncom
import win32gui
import win32process
import wmi as wmi
from kill_thread import kill_thread
from mttkinter import mtTkinter

from modules.misc import time_format

chariot_path = "C:/Program Files (x86)/Ixia/IxChariot"
snapshot_wait = 30
measure_cache_size = 100
measure_delta_t = 1.0
measure_period = 5.0


class IxChariotAPI(object):
    """
        用于自动化ixchariot打流tst任务脚本 本对象只限于一个tst文件的操作
        包含流的创建、打流过程监控、打流数据回收、打流任务结束
    """

    def __init__(self) -> None:
        # 路径
        self.rssi_list = None
        self.group_pairs = None
        self.pair_num = None
        self.flow_directions = None
        self.chariot_path = chariot_path
        # 基础参数
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s][%(filename)s %(lineno)d] %(levelname)s : %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.duration = 60
        self.reinit_times = None
        self.reinit_period = None
        # 实例化
        self.tcl = mtTkinter.Tcl()
        # 自定义成员
        self.total_pair_num = 1  # 当前tst的pair编号
        self.run_flag = False  # 是否执行标识位
        self.data_is_lost = False  # 执行run完成后，是否存在数据丢失
        self.data = []  # 吞吐总数据

        # 基础环境参数配置
        self.set_paths()
        self.set_duration()
        self.load_dll()
        self.set_run_options()

        self.thr_meas_cache = []
        self.thr_meas_thread = []
        self.mcs = [measure_cache_size]
        self.mdt = [measure_delta_t]
        self.mp = [measure_period]

    def __del__(self) -> None:
        """
            清理函数 清空tcl脚本对象
        """
        self.tcl.tk.quit()
        self.tcl.quit()

    ##################################
    # 设置脚本基础配置
    ##################################

    def set_paths(self):
        """
            设置tcl脚本 工作路径及保存路径
        """
        self.tcl.setvar('ixchariot_installation_dir', self.chariot_path)
        self.tcl.setvar('work_dir', os.getcwd())
        self.logger.info(
            "设置Ixchariot安装路径: [{}]  Ixchariot tst保存路径: [{}]".format(self.chariot_path, os.getcwd())
        )

    def set_duration(self, duration=None):
        """
            设置tcl脚本 ixchariot打流时长 单位秒 非必须
        """
        self.duration = int(duration) if duration else self.duration
        self.tcl.setvar('duration', str(self.duration))
        self.logger.info("设置执行时长[{}]秒".format(self.duration))
        if duration:
            self.set_run_options()

    def set_reinit(self, times, period):
        """
            设置是否重新初始化 非必须
        """
        self.reinit_times = times
        self.reinit_period = period
        self.logger.info("设置重新执行次数 [{}]  重新执行间隔时间 [{}]".format(times, period))
        self.set_run_options()

    def load_dll(self):
        """
            加载tcl参数
        """
        self.tcl.eval("""cd $ixchariot_installation_dir
            load ChariotExt
            package require ChariotExt
            global auto_index
            file mkdir $work_dir
            cd $work_dir""")
        self.logger.info("加载ixchariot环境参数...ok")

    def set_run_options(self):
        """
            设置执行配置
        """
        run_minutes = str(round(self.duration / 60)) if round(self.duration / 60) else '1'
        self.tcl.eval("""set test [chrTest new]
            set runOpts [chrTest getRunOpts $test]
            chrRunOpts set $runOpts TEST_END FIXED_DURATION
            chrRunOpts set $runOpts REPORTING_TYPE BATCH 
            chrRunOpts set $runOpts STOP_ON_INIT_ERR False
            chrRunOpts set $runOpts STOP_AFTER_NUM_PAIRS_FAIL 9999
            chrRunOpts set $runOpts TEST_DURATION $duration
            chrRunOpts set $runOpts POLL_ENDPOINTS True
            chrRunOpts set $runOpts POLL_TIME {}
            chrRunOpts set $runOpts POLL_RETRIEVING_TYPE RETRIEVE_TIMING_RECORD""".format(run_minutes))
        if self.reinit_times and self.reinit_period:
            self.tcl.eval("chrRunOpts set $runOpts ALLOW_PAIR_REINIT_RUN True")
            self.tcl.eval("chrRunOpts set $runOpts PAIR_REINIT_MAX_RUN {}".format(self.reinit_times))
            self.tcl.eval("chrRunOpts set $runOpts PAIR_REINIT_RETRY_INTERVAL_RUN {}".format(self.reinit_period))
        self.logger.info("Ixchariot Set Run Option 设置运行参数...ok")

    def add_pair(
            self, ep1: str, ep2: str, flows_per_pair: int = 1, script="Throughput", protocol="TCP",
            rate_limit="unlimited", group_name="autotest"
    ):
        """
            添加流
            :param flows_per_pair       int         流数量
            :param ep1                  string      endpoint1 ip地址
            :param ep2                  string      endpoint2 ip地址
            :param script               string      打流脚本 Throughput/High_Performance_Throughput
            :param protocol             string      打流协议 tcp/udp
            :param rate_limit           string      打流脚本限速
            :param group_name           string      组名称 仅取64位长度 不能为中文
        """
        # endpoint1 IP
        self.tcl.setvar('ep1', ep1)
        # endpoint2 IP
        self.tcl.setvar('ep2', ep2)
        # 脚本路径
        self.tcl.setvar('script', self.chariot_path + '/Scripts/{}.scr'.format(script))
        # 协议
        self.tcl.setvar('protocol', protocol.upper())
        # 限速
        if rate_limit != "unlimited":
            self.tcl.setvar('sendRate', ("%10.3f" % rate_limit).replace(' ', '0') + 'Mb')
        else:
            self.tcl.setvar('sendRate', 'unlimited')
        # 组名称
        self.tcl.setvar('groupName', group_name[:64])
        # 创建流
        for cnt in range(flows_per_pair):
            # 创建pair
            self.tcl.eval('set pair{} [chrPair new]'.format(self.total_pair_num))
            # 设置groupName
            self.tcl.eval('chrPair set $pair{} COMMENT $groupName'.format(self.total_pair_num))
            # 设置endpoint
            self.tcl.eval('chrPair set $pair{} E1_ADDR $ep1 E2_ADDR $ep2'.format(self.total_pair_num))
            # 设置protocol
            self.tcl.eval('chrPair set $pair{} PROTOCOL  $protocol'.format(self.total_pair_num))
            # 指定脚本
            self.tcl.eval('chrPair useScript $pair{} $script'.format(self.total_pair_num))
            # 限速
            self.tcl.eval('chrPair setScriptVar $pair{} send_data_rate $sendRate'.format(self.total_pair_num))
            # 添加pair
            self.tcl.eval('chrTest addPair $test $pair{}'.format(self.total_pair_num))
            # 信息打印
            self.logger.info(
                "添加pair[{}]\t组名[{}]\tep1[{}]\tep2[{}]\t协议[{}]\t脚本[{}]\t限速设置[{}]".format(
                    self.total_pair_num,
                    group_name[:64],
                    ep1, ep2, protocol,
                    script, rate_limit
                )
            )
            # 总pair数+1
            self.total_pair_num += 1

    ##################################
    # 脚本执行相关函数
    ##################################

    def run(self, timeout=10):
        """
            开始打流
            开始前记得先调用add_pair添加流
        """
        # 开始
        start_time = time.time()
        self.set_start()
        # 等待至设置的打流时间结束
        self.logger.info("等待至设置的打流时间结束->[{}]秒".format(self.duration))
        while time.time() - start_time < self.duration + 3:
            if hasattr(self, 'halt') and self.halt:
                print('检测到强制停止命令，开始执行强制停止')
                self.force_stop()
                return 0
            time.sleep(1)
        # 开始检测是否自动结束
        self.logger.info("检测是否完成打流...")
        while time.time() - start_time < self.duration + 3 + timeout:
            if self.is_stopped():
                self.logger.info("打流完成...")
                return 1
            self.logger.info("打流未完成完成, 继续检测...超时[{}/{}]".format(int(time.time() - start_time), timeout))
            time.sleep(3)
        # 没有正常结束，存在异常 强制终止
        self.logger.info("打流超时未正常结束，强制终止...")
        self.force_stop()
        return 0

    def set_start(self):
        """
            开始打流操作
            外部调用时不要调用本函数
        """
        self.tcl.eval('chrTest start $test')
        self.tcl.setvar('testIsStopped', '0')
        self.run_flag = True
        self.logger.info("打流开始...")

    def set_abandon(self):
        """
            抛弃打流操作
        """
        self.logger.info('Abandon打流...')
        try:
            self.tcl.eval('chrTest abandon $test')
            self.logger.info('Abandon打流...success')
            return 1
        except Exception as e:
            self.logger.info('无法abandon... {}'.format(e))
            return 0

    def set_stop(self):
        """
            结束打流操作
        """
        self.logger.info('停止打流...')
        try:
            self.tcl.eval('chrTest stop $test')
            self.logger.info('停止打流...success')
            return 1
        except Exception as e:
            self.logger.info('无法停止打流... {}'.format(e))
            return 0

    def force_stop(self):
        """
            强制结束打流
        """
        # 结束打流，如果卡住需要abandon
        stop_res = self.set_stop()
        if not stop_res:
            return 0
        self.logger.info("等待打流结束 -> [12]秒")
        time.sleep(12)
        # 获取状态
        if self.is_stopped():
            self.logger.info("强制结束成功...")
            return 1
        # 触发abandon后再重新检测
        self.logger.info("未成功停止, abandon...")
        self.set_abandon()
        time.sleep(3)
        if self.is_stopped():
            self.logger.info("abandon成功...")
            return 1
        self.logger.info("abandon失败...")
        return 0

    def is_stopped(self) -> int:
        """
            获取打流是否结束
        """
        self.tcl.eval("set testIsStopped [chrTest isStopped $test]")
        return self.tcl.getvar("testIsStopped")

    def get_pair_run_status(self):
        """
            获取每条流打流完成后的状态信息
        """
        status_list = []
        for i in range(1, self.total_pair_num):
            status_list.append(self.tcl.eval(f'chrPair get $pair{i} RUNSTATUS'))
        return status_list

    def get_throughput(self):
        """
            获取打流结果
        """
        total_bytes = 0
        total_measured_time = 0
        self.data = {
            "total_throughput": 0,
            "pair_data": []
        }

        for i in range(1, self.total_pair_num):
            # 获取pair流的吞吐 均值、最大值、最小值
            tp = self.tcl.eval('chrPairResults get $pair{} THROUGHPUT'.format(i))
            # 添加新数据
            self.data["pair_data"].append({
                "flows_per_pair": i,
                "pair_throughput_avg": round(float(tp.split()[0]), 3),
                "pair_time_record": [],
            })
            # print(self.data["pair_data"][-1]["pair_throughput_avg"])

            # 指针赋值
            p_data = self.data["pair_data"][-1]["pair_time_record"]
            self.logger.info("pair{} 数据".format(i))

            # 获取全部数据的每个数据颗粒的编号 或称handle
            count = int(self.tcl.eval('chrPair getTimingRecordCount $pair{}'.format(i)))
            min_handle = self.tcl.eval('chrPair getTimingRecord $pair{} {}'.format(i, 0))
            max_handle = self.tcl.eval('chrPair getTimingRecord $pair{} {}'.format(i, int(count) - 1))

            # 获取pair的发送数据量/耗时 并求和
            pair_bytes_sent_e1 = float(self.tcl.eval('chrCommonResults get $pair{} BYTES_SENT_E1'.format(i)))
            pair_bytes_recv_e1 = float(self.tcl.eval('chrCommonResults get $pair{} BYTES_RECV_E1'.format(i)))
            total_bytes += (pair_bytes_sent_e1 + pair_bytes_recv_e1)
            pair_elapsed_time = float(self.tcl.eval('chrTimingRec get {} ELAPSED_TIME'.format(max_handle)))
            total_measured_time += pair_elapsed_time

            # 获取每个时刻的数据
            for handle in range(int(min_handle), int(max_handle) + 1):
                measured_time = float(self.tcl.eval('chrCommonResults get {} MEAS_TIME'.format(handle)))
                bytes_sent_e1 = float(self.tcl.eval('chrCommonResults get {} BYTES_SENT_E1'.format(handle)))
                bytes_recv_e1 = float(self.tcl.eval('chrCommonResults get {} BYTES_RECV_E1'.format(handle)))
                elapsed_time = float(self.tcl.eval('chrTimingRec get {} ELAPSED_TIME'.format(handle)))
                # print(measured_time)

                # Bytes转Bit 换算Mbps
                if measured_time == 0:
                    throughput = 0
                else:
                    throughput = (bytes_sent_e1 + bytes_recv_e1) * 8 / measured_time / 1000000
                p_data.append({
                    "elapsed_time": elapsed_time,
                    "measured_time": measured_time,
                    "bytes_sent_e1": bytes_sent_e1,
                    "bytes_recv_e1": bytes_recv_e1,
                    "throughput": throughput,
                })

        # 计算总吞吐 并赋值 (会有一点点误差 ±1%)
        self.data["total_throughput"] = round(
            total_bytes * 8 / 1000000 / total_measured_time * (self.total_pair_num - 1), 3)
        # import json
        # with open("./data.txt", "a") as f:
        #     f.write(json.dumps(self.data))
        # print(self.data["total_throughput"])
        return self.data

    def get_rssi(self):
        # 存在上行打流pair
        if any('up' in fd for fd in self.flow_directions):
            # 获取每个pair的rssi
            pairs_rssi = []
            for i in range(self.pair_num - 1):
                try:
                    pairs_rssi.append(
                        float(self.tcl.eval('chrPairResults get $pair' + str(i + 1) + ' RSSI_E1').split()[0]))
                except Exception as e:
                    _ = e
                    # traceback.self.logger.info_exc()
                    pairs_rssi.append(None)
            # 计算每个group的平均rssi
            self.rssi_list = []
            for group_pair in self.group_pairs:
                g_rssi = [pairs_rssi[pair] for pair in group_pair if pairs_rssi[pair]]
                g_rssi = round(sum(g_rssi) / len(g_rssi), 1) if g_rssi else ''
                self.rssi_list.append(g_rssi)
            self.logger.info('分组RSSI：', self.rssi_list)
            return self.rssi_list
        else:
            self.rssi_list = None
            return self.rssi_list

    def save_tst(self, filename=None):
        if not filename:
            filename = "{}-{}Mbps".format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), "00.000")
        self.tcl.setvar('result', os.path.join(os.getcwd(), filename + '.tst'))
        self.tcl.eval('chrTest save $test $result')
        self.logger.info('打流文件已保存为：{}'.format(os.path.join(os.getcwd(), filename + '.tst')))
        # self.tcl.eval('chrTest delete $test force')
        self.tcl.eval('return')
        time.sleep(1)
        if self.data_is_lost:
            self.logger.info('Throughput Test Data Lost')
        time.sleep(1)

    @staticmethod
    def save_jpg(tst_filename='test', jpg_filename='test'):
        def my_process(filename='test'):
            os.system('{}.tst'.format(filename))

        def enum_windows(hwnd, target_handle):
            title = win32gui.GetWindowText(hwnd)
            # print(hwnd, title)
            if '.tst' in title:
                target_handle.append(hwnd)

        def get_screen_by_mss(filename='test'):
            sct = mss.mss()
            start = time.time()
            img = sct.grab({'top': 0, 'left': 0, 'width': 1920, 'height': 1080})  # 截图
            # noinspection PyTypeChecker
            img = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)  # 转换色值
            end = time.time()
            print(end - start)
            cv2.imwrite('{}.jpg'.format(filename), img)

        handle = []
        c_started = False
        print('TST路径:{}.tst'.format(tst_filename))
        while not c_started:
            while len(handle) > 0:
                chariot_pid = str(win32process.GetWindowThreadProcessId(handle.pop(0))[1])
                print('刷新进程，准备杀死{}'.format(chariot_pid))
                os.system('taskkill /PID {} /F'.format(chariot_pid))
            p = threading.Thread(target=my_process, args=(tst_filename,))
            p.start()
            print('等待Chariot打开TST文件')
            time.sleep(snapshot_wait)
            win32gui.EnumWindows(enum_windows, handle)
            c_started = len(handle) == 1
        print('开始截图')
        get_screen_by_mss(filename=jpg_filename)
        print('结束截图，关闭Chariot')
        chariot_pid = str(win32process.GetWindowThreadProcessId(handle[0])[1])
        print('结束截图，准备杀死{}'.format(chariot_pid))
        os.system('taskkill /PID {} /F'.format(chariot_pid))

    def monitor_config(self, new_config=None):
        if new_config is None:
            try:
                msg = {
                    'mcs': self.mcs[0],
                    'mdt': self.mdt[0],
                    'mp': self.mp[0]
                }
                ret = True
            except Exception as e:
                msg = '获取测速参数出错:{}'.format(repr(e))
                ret = False
            return ret, msg
        else:
            try:
                self.mcs[0] = new_config['mcs']
                self.mdt[0] = new_config['mdt']
                self.mp[0] = new_config['mp']
                msg = '设置测速参数成功'
                ret = True
            except Exception as e:
                msg = '设置测速参数出错:{}'.format(repr(e))
                ret = False
            return ret, msg

    def monitor_start(self):
        def continuous_measurement(ic_api: IxChariotAPI):
            def measure_once(dt=1.0, p_obj=None):
                def get_bytes(pid_=None, p_obj_=None):
                    # noinspection PyUnresolvedReferences
                    def get_pid():
                        pythoncom.CoInitialize()
                        wmi_obj = wmi.WMI()
                        services = wmi_obj.Win32_Service()
                        for i in services:
                            if i.DisplayName == 'Ixia Performance Endpoint':
                                pythoncom.CoUninitialize()
                                return int(i.ProcessId)
                        pythoncom.CoUninitialize()
                        return -1

                    try:
                        if p_obj_ is None:
                            if pid_ is None:
                                pid_ = get_pid()
                            assert pid_ > 0, '没有找到打流端点服务对应的进程，无法进行流量统计！'
                            p_obj_ = psutil.Process(pid_)
                        io_counters = p_obj_.io_counters()
                        return io_counters.other_bytes, pid_, p_obj_
                    except Exception as e__:
                        msg_ = '流量统计异常:{}'.format(repr(e__))
                        print(msg_)
                        return 0, -1, None

                try:
                    t_bytes_old, pid, p_obj = get_bytes(p_obj_=p_obj)
                    time.sleep(dt)
                    t_bytes_new, pid, p_obj = get_bytes(pid_=pid, p_obj_=p_obj)
                    db = t_bytes_new - t_bytes_old
                    thr_ = db / dt
                    return thr_, db, dt, p_obj
                except Exception as e_:
                    msg__ = '单次测速异常:{}'.format(repr(e_))
                    print(msg__)
                    return 0, 0, delta_t, None

            process_obj = None
            while True:
                while len(ic_api.thr_meas_cache) > ic_api.mcs[0]:
                    ic_api.thr_meas_cache.pop(0)
                thr, delta_b, delta_t, process_obj = measure_once(dt=ic_api.mdt[0], p_obj=process_obj)
                timestamp = datetime.datetime.now().strftime(time_format)
                msg___ = '连续测速报告 吞吐:{} 字节变化量:{} 测量时差:{} 测量完成时刻:{}'.format(
                    thr, delta_b, delta_t, timestamp
                )
                print(msg___)
                ic_api.thr_meas_cache.append(
                    {'thr': thr, 'delta_b': delta_b, 'delta_t': delta_t, 'timestamp': timestamp})
                time.sleep(ic_api.mp[0])

        try:
            if len(self.thr_meas_thread) > 0:
                msg = '连续测速已经启动'
                ret = False
            else:
                cm_thread = threading.Thread(target=continuous_measurement)
                self.thr_meas_thread.append(cm_thread)
                cm_thread.start()
                msg = '连续测速现在启动'
                ret = True
        except Exception as e:
            msg = '启动连续测速出错:{}'.format(repr(e))
            ret = False
        return ret, msg

    def monitor_read(self, points_count):
        try:
            msg = []
            while len(msg) < points_count:
                if len(self.mcs) <= 0:
                    break
                msg.append(self.mcs.pop(0))
            ret = True
        except Exception as e:
            msg = '读取测速结果出错:{}'.format(repr(e))
            ret = False
        return ret, msg

    def monitor_stop(self):
        try:
            cm_thread = self.thr_meas_thread.pop(0)
            kill_thread(cm_thread)
            msg = '连续测速已停止'
            ret = True
        except Exception as e:
            msg = '停止连续测速出错:{}'.format(repr(e))
            ret = False
        return ret, msg


def chariot_init(params):
    chariot_init_params = params['chariot']
    ic_api = IxChariotAPI()
    chariot_init_params['ic_api'] = ic_api
    return params


def chariot_set_duration(params):
    sd_params = params['chariot']
    ic_api: IxChariotAPI = sd_params['ic_api']
    duration = sd_params['duration']
    ic_api.set_duration(duration=duration)
    return params


def chariot_add_pairs(params):
    ap_params = params['chariot']
    ic_api: IxChariotAPI = ap_params['ic_api']
    pairs = ap_params['pairs']
    for pair in pairs:
        # pair = {
        #     'ep1': '',  # 必填
        #     'ep2': '',  # 必填
        #     'flows_per_pair': 1,  # 可选
        #     'script': 'Throughput',  # 可选
        #     'protocol': 'TCP',  # 可选
        #     'rate_limit': 'unlimited',  # 可选
        #     'group_name': 'autotest'  # 可选
        # }
        ic_api.add_pair(**pair)
    return params


def chariot_run(params):
    run_params = params['chariot']
    ic_api: IxChariotAPI = run_params['ic_api']
    try:
        if 'timeout' in run_params.keys():
            timeout = run_params['timeout']
            ic_api.run(timeout=timeout)
        else:
            ic_api.run()
        status_list = ic_api.get_pair_run_status()
        text_list = ['finished', 'finished with warnings']
        run_params['exception'] = None
        for sta in status_list:
            if sta not in text_list:
                run_params['exception'] = sta
                break
    except Exception as e:
        run_params['exception'] = e
    return params


def chariot_get_thr(params):
    gt_params = params['chariot']
    ic_api: IxChariotAPI = gt_params['ic_api']
    ic_api.get_throughput()
    thr_data = ic_api.data
    gt_params['thr_data'] = thr_data
    return params


def chariot_save_tst(params):
    st_params = params['chariot']
    ic_api: IxChariotAPI = st_params['ic_api']
    if 'tst_filename' in st_params.keys():
        tst_filename = st_params['tst_filename']
        ic_api.save_tst(filename=tst_filename)
    else:
        ic_api.save_tst()
    return params


def chariot_save_jpg(params):
    sp_params = params['chariot']
    ic_api: IxChariotAPI = sp_params['ic_api']
    tst_filename = sp_params['tst_filename']
    jpg_filename = sp_params['jpg_filename']
    ic_api.save_jpg(tst_filename=tst_filename, jpg_filename=jpg_filename)
    return params


def chariot_monitor_config(params):
    cmc_params = params['chariot']
    ic_api: IxChariotAPI = cmc_params['ic_api']
    if 'new_config' in cmc_params.keys():
        new_config = cmc_params['new_config']
        del cmc_params['new_config']
    else:
        new_config = None
    ret, msg = ic_api.monitor_config(new_config=new_config)
    cmc_params['msg'] = msg
    return params


def chariot_monitor_start(params):
    cms_params = params['chariot']
    ic_api: IxChariotAPI = cms_params['ic_api']
    ret, msg = ic_api.monitor_start()
    cms_params['msg'] = msg
    return params


def chariot_monitor_read(params):
    cmr_params = params['chariot']
    ic_api: IxChariotAPI = cmr_params['ic_api']
    points_count = cmr_params['points_count']
    del cmr_params['points_count']
    ret, msg = ic_api.monitor_read(points_count=points_count)
    cmr_params['msg'] = msg
    return params


def chariot_monitor_stop(params):
    cms_params = params['chariot']
    ic_api: IxChariotAPI = cms_params['ic_api']
    ret, msg = ic_api.monitor_stop()
    cms_params['msg'] = msg
    return params


if __name__ == '__main__':
    params_ = {'chariot': {}}
    params_ = chariot_init(params=params_)
    params_['chariot']['duration'] = 15
    params_ = chariot_set_duration(params=params_)
    params_['chariot']['pairs'] = [
        {
            'ep1': '192.168.110.1', 'ep2': '192.168.110.1', 'flows_per_pair': 10, 'script': 'Throughput',
            'protocol': 'TCP',
            'rate_limit': 'unlimited', 'group_name': 'autotest'
        }
    ]
    params_ = chariot_add_pairs(params=params_)
    params_ = chariot_run(params=params_)
    params_ = chariot_get_thr(params=params_)
    print('Done')
    # a = IxChariotAPI("C:/Users/ruijie/Desktop/ixc_tst")
    # a.set_duration(10)
    # a.add_pair(
    #     ep1="192.168.115.128", ep2="192.168.115.169", flows_per_pair=10, script="Throughput", group_name='autotest'
    # )
    # a.run()
    # a.get_throughput()
    # a.save_tst()
