class WCList:

    def __init__(self, text) -> None:
        # 源数据字符串
        self.wlanconfig = None
        self.text = text
        # 格式化
        self.format()

    def get_client(self, mac):
        """
            获取指定终端的信息
        """
        print(self.wlanconfig)
        for item in self.wlanconfig:
            if item["mac"].upper() == mac.upper():
                return item

    def format(self):
        self.wlanconfig = []
        try:
            iface_array = self.text.split("\n")[2:-1]
        except Exception as e:
            print(repr(e))
            return

        for i in iface_array:
            data_array = i.split()
            txrate = data_array[3].replace('M', '')
            rxrate = data_array[4].replace('M', '')
            maxrate = data_array[6].replace('M', '')

            self.wlanconfig.append({
                "mac": data_array[0],
                "channel": data_array[2],
                "txrate": txrate,
                "rxrate": rxrate,
                # "rssi": data_array[5].split("/")[0],
                "rssi": data_array[5],
                "maxrate": maxrate,
                "accoctime": data_array[7],
                "utilization": data_array[8],
                "floornoise": data_array[9],
                "powersavemode": data_array[10],
                "ifname": data_array[11],
                "ssid": data_array[12],
                "wifiup": data_array[13],
                "wifidown": data_array[14]
            })


class WCRadio:
    def __init__(self, text) -> None:
        # 源数据字符串
        self.wlanconfig = None
        self.text = text
        # 格式化
        self.format()

    def format(self):
        self.wlanconfig = {}
        try:
            iface_array = self.text.split("\r\n")[1:-1]
        except Exception as e:
            print(repr(e))
            return

        for pair in iface_array:
            pair = pair.split(':')
            key, value = pair[0], pair[1]
            try:
                value = int(value)
            except Exception as e:
                _ = e
                try:
                    value = float(value)
                except Exception as e:
                    _ = e
            self.wlanconfig[key] = value
