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

    def __init__(self):
        self.sy = {
            'Nc': sympy.Symbol('Nc'),
            'Tc': sympy.Symbol('Tc'),
            'Nm': sympy.Symbol('Nm'),
            'Tm': sympy.Symbol('Tm'),
            'Rh': sympy.Symbol('Rh'),
            'Ta': sympy.Symbol('Ta'),
            'Ef': sympy.Symbol('Ef')
        }
        self.hr_equ = sympy.Eq(
            self.sy['Nc'] / (self.sy['Nc'] + self.sy['Nm']),
            self.sy['Rh']
        )
        self.hr_equ_vars = {'Nc', 'Nm', 'Rh'}
        self.ta_equ = sympy.Eq(
            self.sy['Rh'] * self.sy['Tc'] + (1 - self.sy['Rh']) * self.sy['Tm'],
            self.sy['Ta']
        )
        self.ta_equ_vars = {'Rh', 'Tc', 'Tm', 'Ta'}
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


def hit_rate(cond):
    result = {}
    nc = cond['Cache']['Nc']
    tc = cond['Cache']['Tc']
    nm = cond['MEM']['Nm']
    tm = cond['MEM']['Tm']
    h = nc / (nc + nm)
    result['HitRate'] = h
    ta = h * tc + (1 - h) * tm
    result['AveTime'] = ta
    result['Efficiency'] = tc / ta
    return result


if __name__ == '__main__':
    conditions = {'Nm': 100, 'Tm': 250, 'Nc': 1900, 'Tc': 50}
    cs = CacheSys()
    Effi = cs.solve(cond=conditions, need='Ef')
    HitR = cs.solve(cond=conditions, need='Rh')
    AveTime = cs.solve(cond=conditions, need='Ta')
    print('Done')
