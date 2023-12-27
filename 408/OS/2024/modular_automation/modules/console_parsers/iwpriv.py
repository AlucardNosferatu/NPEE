class IWPSiteSurvey:
    def __init__(self, text) -> None:
        # 源数据字符串
        self.iwp = None
        self.text = text
        # 格式化
        self.format()

    def format(self):
        self.iwp = []
        try:
            info_lines = self.text.split("\r\n")[3:-2]
        except Exception as e:
            print(repr(e))
            return

        for ap in info_lines:
            ap = ap.strip()
            while '  ' in ap:
                ap = ap.replace('  ', ' ')
            ap = ap.split(' ')
            ap_ = []
            for _ in range(2):
                ap_.append(ap.pop(0))
            for _ in range(12):
                ap_.append(ap.pop(-1))
            ap_.insert(2, ' '.join(ap))
            self.iwp.append(ap_)


class IWPStat:
    def __init__(self, text) -> None:
        # 源数据字符串
        self.iwp = None
        self.text = text
        # 格式化
        self.format()

    def format(self):
        self.iwp = {}
        try:
            info_lines = self.text.split("\r\n")[2:-2]
        except Exception as e:
            print(repr(e))
            return

        for stat in info_lines:
            stat = stat.strip()
            while '  ' in stat:
                stat = stat.replace('  ', ' ')
            if stat.count('=') > 1:
                stat_list = stat.split(',')
            else:
                stat_list = [stat]
            prefix = None
            for stat_ in stat_list:
                if '=' not in stat_:
                    if ':' in stat_:
                        stat_ = stat_.replace(':', '=')
                    else:
                        stat_ = stat_.replace(' ', '=')
                stat_ = stat_.split('=')
                key, value = stat_[0].strip(), stat_[1].strip()
                if prefix is not None:
                    key = prefix + ' ' + key
                else:
                    prefix = key
                self.iwp[key] = value


class IWPReg:
    def __init__(self, text) -> None:
        # 源数据字符串
        self.iwp = None
        self.text = text
        # 格式化
        self.format()

    def format(self):
        self.iwp = {}
        try:
            info_line = self.text.split("\r\n")[1]
        except Exception as e:
            print(repr(e))
            return
        info_line = info_line.split(':')
        mapped, value = info_line[1].strip('[]'), info_line[2]
        self.iwp['value'] = value
        self.iwp['mapped_addr'] = mapped
