import re

from modules.console_parsers.ifconfig import IFConfig


class IWConfig:

    def __init__(self, text):
        # 源数据字符串
        self.iwconfig = None
        self.text = text
        # 格式化后的内容
        self.format()

    def effective_interface(self, ifconfig_text, wireless_type):
        """
        获取生效的接口
        :param ifconfig_text                ifconfig 命令回显
        :param wireless_type                2.4G或5G
        :return ["ra0", "rax1"...]          接口列表
        """
        ret_intf_array = []
        iwconfig_intf = [item for item in self.iwconfig]

        # 获取ifconfig生效接口
        m_ifconfig = IFConfig(ifconfig_text)
        if_intf = m_ifconfig.get_intf_name_list()

        for intf in iwconfig_intf:
            if intf["name"] in if_intf:
                if wireless_type == "2.4G" and int(intf["channel"]) <= 13 and intf["ssid"] != "":
                    ret_intf_array.append(intf)

                if wireless_type == "5G" and int(intf["channel"]) > 13 and intf["ssid"] != "":
                    ret_intf_array.append(intf)

        return ret_intf_array

    def format(self):
        """
        获取信息中符合查询条件的值
        """
        self.iwconfig = []
        # 用切片分开数据
        iface_array = re.split(r"\n\s+\n|\n\n", self.text.strip())

        # 去除头尾的空格
        for iface_block in iface_array:
            # 处理头尾空字符
            iface_block = iface_block.strip()
            # 获取接口的名称
            iface_name = iface_block[:10].strip()

            # 接口未生效时，数据全部留空
            if "no wireless extensions." in iface_block:
                continue

            # 匹配SSID
            match_ssid = re.findall(r"ESSID:\"(.*)\"", iface_block)
            if len(match_ssid) != 1:
                ssid = ""
            else:
                ssid = match_ssid[0]

            # 匹配Channel
            match_channel = re.findall(r"Channel[=,:](\d+)\s+A", iface_block)
            if len(match_channel) != 1:
                channel = "-1"
            else:
                channel = match_channel[0]

            # 匹配bssid
            match_bssid = re.findall(r"Access Point:\s+(.*?)\s+B", iface_block)
            if len(match_bssid) != 1:
                bssid = ""
            else:
                bssid = match_bssid[0]

            # 匹配bit-rate
            match_bit = re.findall(r"Bit Rate\S(.*?)\s+T", iface_block)
            if len(match_bit) != 1:
                bit_rate = ""
            else:
                bit_rate = match_bit[0].split()[0]
                if "Gb" in match_bit[0]:
                    bit_rate = float(bit_rate) * 1000
                bit_rate = str(bit_rate)

            # 匹配txpower
            match_txpower = re.findall(r"Tx-Power:(.*)\s+dBm", iface_block)
            if len(match_txpower) != 1:
                txpower = ""
            else:
                txpower = match_txpower[0]

            self.iwconfig.append({
                "name": iface_name,
                "ssid": ssid,
                "channel": channel,
                "bssid": bssid,
                "bit_rate": bit_rate,
                "txpower": txpower
            })
