import re


class IFConfig:

    def __init__(self, text):
        # 源数据字符串
        self.ifconfig = None
        self.text = text
        # 格式化
        self.format()

    def get_intf_name_list(self):
        return [item["name"] for item in self.ifconfig]

    def format(self):
        """
        获取信息中符合查询条件的值
        """
        self.ifconfig = []
        # 用切片分开数据
        iface_array = self.text.split("\r\n")
        # 去除头尾的空格
        for iface_block in iface_array:
            # 处理头尾空字符
            iface_block = iface_block.strip()
            # 获取接口的名称
            iface_name = iface_block[:10].strip()

            # 接口未生效时，数据全部留空 (ifconfig可以省略)
            if "no wireless extensions." in iface_block:
                self.ifconfig.append({
                    "name": iface_name,
                    "mac": "",
                    "ip": "",
                    "bcast": "",
                    "mask": "",
                    "mtu": "",
                    "rx_packets": "",
                    "tx_packets": ""
                })
                continue

            # 匹配mac
            match_mac = re.findall(r"HWaddr\s(.*)\s+", iface_block)
            if len(match_mac) != 1:
                mac = ""
            else:
                mac = match_mac[0]

            # 匹配ip
            match_ip = re.findall(r"inet addr:(.*)\s+B", iface_block)
            if len(match_ip) != 1:
                ip = ""
            else:
                ip = match_ip[0]

            # 匹配bcast
            match_bcast = re.findall(r" Bcast:(.*)\s+M", iface_block)
            if len(match_bcast) != 1:
                bcast = ""
            else:
                bcast = match_bcast[0]

            # 匹配mask
            match_mask = re.findall(r" Mask:(.*)\s+i", iface_block)
            if len(match_mask) != 1:
                mask = ""
            else:
                mask = match_mask[0]

            # 匹配mtu
            match_mtu = re.findall(r" MTU:(.*)\s+M", iface_block)
            if len(match_mtu) != 1:
                mtu = ""
            else:
                mtu = match_mtu[0]

            # 匹配rx-packets
            match_rx = re.findall(r" RX packets:(.*)\s+e", iface_block)
            if len(match_rx) != 1:
                rx = ""
            else:
                rx = match_rx[0]

            # 匹配tx-packets
            match_tx = re.findall(r" TX packets:(.*)\s+e", iface_block)
            if len(match_tx) != 1:
                tx = ""
            else:
                tx = match_tx[0]

            self.ifconfig.append({
                "name": iface_name,
                "mac": mac,
                "ip": ip,
                "bcast": bcast,
                "mask": mask,
                "mtu": mtu,
                "rx_packets": rx,
                "tx_packets": tx
            })
