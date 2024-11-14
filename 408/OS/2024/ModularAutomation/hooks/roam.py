import time

from modules.android import android_init_device, android_get_element, android_interact_device


def detect(params, val):
    params['android']['by'] = 'xpath'
    # noinspection SpellCheckingInspection
    params['android']['value'] = val
    params = android_get_element(params=params)
    f = params['android']['found']
    return f


# noinspection SpellCheckingInspection
def collect_from_ui(params, pre_list, now_list, int_list, tim_list, bssid_pre_list, bssid_now_list):
    pre = detect(params, '//*[@resource-id="com.ruijie.wifim:id/tv_pre_rssi"]')
    if len(pre) >= 1:
        pre_list.append(pre[-1].text)
    else:
        pre_list.append('no found')
    now = detect(params, '//*[@resource-id="com.ruijie.wifim:id/tv_now_rssi"]')
    if len(now) >= 1:
        now_list.append(now[-1].text)
    else:
        now_list.append('no found')
    interval = detect(params, '//*[@resource-id="com.ruijie.wifim:id/tv_roam_ping_interval"]')
    if len(interval) >= 1:
        int_list.append(interval[-1].text)
    else:
        int_list.append('no found')
    tim = detect(params, '//*[@resource-id="com.ruijie.wifim:id/tv_time"]')
    if len(tim) >= 1:
        tim_list.append(tim[-1].text)
    else:
        tim_list.append('no found')
    bssid_pre = detect(params, '//*[@resource-id="com.ruijie.wifim:id/tv_pre_bssid"]')
    if len(bssid_pre) >= 1:
        bssid_pre_list.append(bssid_pre[-1].text)
    else:
        bssid_pre_list.append('no found')
    bssid_now = detect(params, '//*[@resource-id="com.ruijie.wifim:id/tv_now_bssid"]')
    if len(bssid_now) >= 1:
        bssid_now_list.append(bssid_now[-1].text)
    else:
        bssid_now_list.append('no found')
    return pre_list, now_list, int_list, tim_list, bssid_pre_list, bssid_now_list


def align_time_stamps(channel1, channel2, threshold):
    # 初始化结果列表
    aligned_channel1 = []
    aligned_channel2 = []

    i, j = 0, 0
    len1, len2 = len(channel1), len(channel2)

    while i < len1 and j < len2:
        time1 = channel1[i]
        time2 = channel2[j]

        # 判断时间差是否在阈值内
        if abs(time1 - time2) <= threshold:
            aligned_channel1.append(time1)
            aligned_channel2.append(time2)
            i += 1
            j += 1
        elif time1 < time2:
            # channel1的时间戳小于channel2，填充NA到channel2
            aligned_channel1.append(time1)
            aligned_channel2.append("NA")
            i += 1
        else:
            # channel2的时间戳小于channel1，填充NA到channel1
            aligned_channel1.append("NA")
            aligned_channel2.append(time2)
            j += 1

    # 处理剩余的时间戳
    while i < len1:
        aligned_channel1.append(channel1[i])
        aligned_channel2.append("NA")
        i += 1

    while j < len2:
        aligned_channel1.append("NA")
        aligned_channel2.append(channel2[j])
        j += 1

    return aligned_channel1, aligned_channel2


def collect_data(uid):
    params = {'android': {'uid': uid}}
    params = android_init_device(params=params)
    f = detect(params, '//*[@resource-id="com.ruijie.wifim:id/tv_roam_num"]')
    h = 394 + 190 + 239 - 11
    pre_list, now_list, int_list, tim_list, bssid_pre_list, bssid_now_list = [], [], [], [], [], []
    if len(f) == 1:
        f = f[0].text
        print(f)
        params['android']['device_action'] = 'swipe'
        params['android']['coordinate_1'] = {'x': 620, 'y': 2200}
        params['android']['coordinate_2'] = {'x': 620, 'y': 2200 - (h + (518 - 345) - 34)}
        params = android_interact_device(params=params)
        time.sleep(1)
        for _ in range(int(f) - 1):
            pre_list, now_list, int_list, tim_list, bssid_pre_list, bssid_now_list = collect_from_ui(
                params, pre_list, now_list, int_list, tim_list, bssid_pre_list, bssid_now_list
            )
            params['android']['device_action'] = 'swipe'
            params['android']['coordinate_1'] = {'x': 620, 'y': 2200}
            params['android']['coordinate_2'] = {'x': 620, 'y': 2200 - h}
            params = android_interact_device(params=params)
            time.sleep(1)
        pre_list, now_list, int_list, tim_list, bssid_pre_list, bssid_now_list = collect_from_ui(
            params, pre_list, now_list, int_list, tim_list, bssid_pre_list, bssid_now_list
        )
    else:
        print('no found')
    print('pre', pre_list)
    print('now', now_list)
    print('int', int_list)
    print('tim', tim_list)
    print('bssid_pre', bssid_pre_list)
    print('bssid_now', bssid_now_list)
    return pre_list, now_list, int_list, tim_list, bssid_pre_list, bssid_now_list


if __name__ == '__main__':
    # collect_data(uid='787f9ead')
    # 示例数据
    channel_1 = [1.1, 2.8, 3.0, 4.1]
    channel_2 = [1.2, 2.2, 4.0, 5.2]
    threshold_ = 0.5
    # 对齐时间戳
    aligned_result = align_time_stamps(channel_1, channel_2, threshold_)
    print('Done')
