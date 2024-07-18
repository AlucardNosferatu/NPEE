class ATERXStat:
    def __init__(self, text) -> None:
        # 源数据字符串
        self.ars = None
        self.text = text
        # 格式化
        self.format()

    def format(self):
        self.ars = {}
        try:
            info_lines = self.text.split("\r\n")[2:-1]
        except BaseException as e:
            print(repr(e))
            return
        for stat in info_lines:
            stat = stat.strip()
            while '  ' in stat:
                stat = stat.replace('  ', ' ')
            stat = stat.split('] ')[1].split(': ')
            key = stat.pop(0)
            value = ': '.join(stat)
            try:
                self.ars[key] = int(value)
            except BaseException as e:
                print(repr(e))
                self.ars[key] = value
