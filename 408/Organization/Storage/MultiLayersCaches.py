import sympy


class CacheSys:
    hr_equ = None
    hr_equ_vars = None
    ta_equ = None
    ta_equ_vars = None
    eff_equ = None
    eff_equ_vars = None
    sy = None
    equ_dict = None

    def __init__(self, mode='串行访存'):
        self.sy = {
            # 缓存访问次数
            'Nc': sympy.Symbol('Nc'),
            # 缓存访问时间（访问缓存所需的时间）
            'Tc': sympy.Symbol('Tc'),
            # 内存访问次数
            'Nm': sympy.Symbol('Nm'),
            # 内存访问时间（直接访问内存所需的时间）
            'Tm': sympy.Symbol('Tm'),
            # 命中率（0 ≤ Rh ≤ 1，表示请求在缓存中找到数据的概率）
            'Rh': sympy.Symbol('Rh'),
            # 平均访问时间（单位通常是纳秒或时钟周期，表示访问数据的平均耗时）
            'Ta': sympy.Symbol('Ta'),
            # 效率（Ef = Tc / Ta，表示缓存系统相比直接访问内存的效率提升倍数）
            'Ef': sympy.Symbol('Ef')
        }
        # 命中率
        self.hr_equ = sympy.Eq(
            self.sy['Nc'] / (self.sy['Nc'] + self.sy['Nm']),
            self.sy['Rh']
        )
        self.hr_equ_vars = {'Nc', 'Nm', 'Rh'}
        # 平均访问时间：物理意义：命中率越高，平均访问时间越接近缓存时间 Tc，反之接近内存时间 Tm。
        if mode == '串行访存':
            self.ta_equ = sympy.Eq(
                self.sy['Rh'] * self.sy['Tc'] + (1 - self.sy['Rh']) * (self.sy['Tm'] + self.sy['Tc']),
                self.sy['Ta']
            )
        elif mode == '并行访存':
            self.ta_equ = sympy.Eq(
                self.sy['Rh'] * self.sy['Tc'] + (1 - self.sy['Rh']) * self.sy['Tm'],
                self.sy['Ta']
            )
        else:
            raise ValueError('mode必须是“串行访存”或者“并行访存”')
        self.ta_equ_vars = {'Rh', 'Tc', 'Tm', 'Ta'}
        # 效率：物理意义：效率值 Ef > 1 表示缓存系统比直接访问内存更快，值越大提升越明显。
        self.eff_equ = sympy.Eq(self.sy['Tc'] / self.sy['Ta'], self.sy['Ef'])
        self.eff_equ_vars = {'Tc', 'Ta', 'Ef'}
        self.equ_dict = {
            'hr': [self.hr_equ, self.hr_equ_vars],
            'ta': [self.ta_equ, self.ta_equ_vars],
            'eff': [self.eff_equ, self.eff_equ_vars]
        }

    def solve(self, cond: dict, need):
        solvable = True
        known_c = []
        while solvable:
            solvable = False
            known_c = list(cond.keys())
            lack_c_hr = self.hr_equ_vars.difference(known_c)
            lack_c_ta = self.ta_equ_vars.difference(known_c)
            lack_c_eff = self.eff_equ_vars.difference(known_c)
            if len(lack_c_hr) == 1:
                cond = self.reduce_unk(lack_c_hr, cond, equ_type='hr')
                solvable = True
            if len(lack_c_ta) == 1:
                cond = self.reduce_unk(lack_c_ta, cond, equ_type='ta')
                solvable = True
            if len(lack_c_eff) == 1:
                cond = self.reduce_unk(lack_c_eff, cond, equ_type='eff')
                solvable = True
        if need in known_c:
            return True, cond[need]
        else:
            return False, None

    def reduce_unk(self, lack_c, cond, equ_type):
        known_c = list(cond.keys())
        need = lack_c.pop()
        temp_equ = self.equ_dict[equ_type][0]
        for key in self.equ_dict[equ_type][1]:
            if key in known_c:
                temp_equ = temp_equ.subs(self.sy[key], cond[key])
        cond[need] = sympy.solve(temp_equ, self.sy[need])[0]
        return cond


if __name__ == '__main__':
    conditions = {'Nm': 100, 'Tm': 250, 'Nc': 1900, 'Tc': 50}
    cs = CacheSys()
    Effi = cs.solve(cond=conditions, need='Ef')
    HitR = cs.solve(cond=conditions, need='Rh')
    AveTime = cs.solve(cond=conditions, need='Ta')
    print('Done')
