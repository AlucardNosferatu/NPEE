import sympy


class RandomEvent:
    prob_de = 0
    prob_nu = 0
    prob = None
    include = None
    exclude = None
    independent = None
    be_included = None
    Calculable = False

    def __init__(self, prob_nu=None, prob_de=None):
        self.Calculable = False
        self.include = []
        self.exclude = []
        self.independent = []
        self.be_included = []
        if prob_de is not None and prob_nu is not None:
            self.set_prob(prob_de=prob_de, prob_nu=prob_nu)

    def refresh_prob(self):
        self.prob = sympy.Rational(self.prob_nu, self.prob_de)
        if self.prob in [sympy.Rational(0, 1), sympy.Rational(1, 1)]:
            self.include.clear()
            self.exclude.clear()
            self.independent.clear()
            self.be_included.clear()
            self.independent.append('all')
        self.Calculable = True

    def set_prob(self, prob_nu: int = None, prob_de: int = None, prob: sympy.Rational = None):

        if prob is not None:
            self.prob_de = int(prob.denominator)
            self.prob_nu = int(prob.numerator)
            self.refresh_prob()
        elif prob_de is not None and prob_nu is not None:
            if not (prob_de != 0 and 1 >= prob_nu / prob_de >= 0):
                raise ValueError('Plz input valid prob.')
            else:
                self.prob_de = prob_de
                self.prob_nu = prob_nu
                self.refresh_prob()
        else:
            raise ValueError('You must specify prob.')

    def set_relation(self, b_event: 'RandomEvent', rel: str, both_side=False):
        if rel is 'INC':
            if self.Calculable and b_event.Calculable:
                if self.prob < b_event.prob:
                    print('B⊆A, P(A)≥P(B), This setting has been ignored.')
                    return
            self.include.append(b_event)
            for b_inc in b_event.include:
                if b_inc not in self.include:
                    self.include.append(b_inc)
            for inc in self.include:
                if inc in self.exclude:
                    self.exclude.remove(inc)
            if both_side:
                b_event.set_relation(self, 'BE_INC')
        elif rel is 'BE_INC':
            if self.Calculable and b_event.Calculable:
                if self.prob > b_event.prob:
                    print('B⊆A, P(A)≥P(B), This setting has been ignored.')
                    return
            self.be_included.append(b_event)
            for b_be_inc in b_event.be_included:
                if b_be_inc not in self.be_included:
                    self.be_included.append(b_be_inc)
            for be_inc in self.be_included:
                if be_inc in self.exclude:
                    self.exclude.remove(be_inc)
            if both_side:
                b_event.set_relation(self, 'INC')
        elif rel is 'EQU':
            self.include = b_event.include.copy()
            self.be_included = b_event.be_included.copy()
            self.include.append(b_event)
            self.be_included.append(b_event)
            if b_event in self.exclude:
                self.exclude.remove(b_event)
            if b_event in self.independent:
                self.independent.remove(b_event)
            if b_event.Calculable:
                self.set_prob(prob=b_event.prob)
            if both_side:
                b_event.set_relation(self, 'EQU')
        elif rel is 'EXC':
            for b_inc in [b_event] + b_event.include:
                if b_inc in self.include:
                    self.include.remove(b_inc)
                if b_inc in self.independent:
                    self.independent.remove(b_inc)
            if b_event in self.be_included:
                self.be_included.remove(b_event)
            self.exclude.append(b_event)
            if both_side:
                b_event.set_relation(self, 'EXC')
        elif rel is 'IND':
            poss_1or0_self = self.Calculable and self.prob in [sympy.Rational(0, 1), sympy.Rational(1, 1)]
            poss_1or0_b = b_event.Calculable and b_event.prob in [sympy.Rational(0, 1), sympy.Rational(1, 1)]
            if not poss_1or0_self and poss_1or0_b:
                if b_event in self.include:
                    self.include.remove(b_event)
                if b_event in self.be_included:
                    self.be_included.remove(b_event)
                if b_event in self.exclude:
                    self.exclude.remove(b_event)
                self.independent.append(b_event)
            if both_side:
                b_event.set_relation(self, 'IND')
        else:
            print('You moron!')

    def uninstall(self, b_event: 'RandomEvent'):
        if self in b_event.independent:
            b_event.independent.remove(self)
        if self in b_event.include:
            b_event.include.remove(self)
        if self in b_event.be_included:
            b_event.be_included.remove(self)
        if self in b_event.exclude:
            b_event.exclude.remove(self)

    def __add__(self, other: 'RandomEvent'):
        assert type(other) is RandomEvent
        new_event = RandomEvent()
        if other.Calculable and self.Calculable:
            product = (self * other)
            if product.prob is not None:
                new_event.set_prob(prob=self.prob + other.prob - product.prob)
            product.uninstall(self)
            product.uninstall(other)
            del product
        ne_poss_1or0 = 'all' in new_event.independent
        self_poss_1or0 = 'all' in self.independent
        other_poss_1or0 = 'all' in other.independent
        if not ne_poss_1or0 and not self_poss_1or0:
            new_event.set_relation(self, 'INC', True)
        if not ne_poss_1or0 and not other_poss_1or0:
            new_event.set_relation(other, 'INC', True)
        return new_event

    def __mul__(self, other: 'RandomEvent'):
        assert type(other) is RandomEvent
        new_event = RandomEvent()
        if other in self.exclude and self in other.exclude:
            new_event.set_prob(prob_de=1, prob_nu=0)
        if other in self.include and self in other.be_included and other.Calculable:
            new_event.set_prob(prob=other.prob)
        if self in other.include and other in self.be_included and self.Calculable:
            new_event.set_prob(prob=self.prob)
        self_poss_1or0 = 'all' in self.independent
        other_poss_1or0 = 'all' in other.independent
        if other.Calculable and self.Calculable:
            mutual_ind = other in self.independent and self in other.independent
            if self_poss_1or0 or other_poss_1or0 or mutual_ind:
                new_event.set_prob(prob=self.prob * other.prob)
        ne_poss_1or0 = 'all' in new_event.independent
        if not ne_poss_1or0 and not self_poss_1or0:
            new_event.set_relation(self, 'BE_INC', True)
        if not ne_poss_1or0 and not other_poss_1or0:
            new_event.set_relation(other, 'BE_INC', True)
        return new_event

    def __neg__(self):
        new_event = RandomEvent()
        if self.Calculable:
            new_event.set_prob(prob=1 - self.prob)
        new_event.set_relation(self, 'EXC', True)
        for e in self.exclude:
            new_event.set_relation(e, 'INC', True)
        for e in self.include:
            new_event.set_relation(e, 'EXC', True)
        for e in self.independent:
            new_event.set_relation(e, 'IND', True)
        return new_event


def test_seq_1():
    event_a = RandomEvent()
    event_a.set_prob(1, 4)
    print('事件A概率是：', event_a.prob)
    event_b = RandomEvent()
    event_b.set_prob(1, 3)
    print('事件B概率是：', event_b.prob)
    event_a_or_b_1 = event_a + event_b
    print('事件A+B概率是：', event_a_or_b_1.prob)
    print('设置令A包含B')
    event_a.set_relation(event_b, 'INC', True)
    print('设置令B包含于A')
    event_b.set_relation(event_a, 'BE_INC', True)
    print('设置令A包含于B')
    event_a.set_relation(event_b, 'BE_INC', True)
    event_a_or_b_2 = event_a + event_b
    print('事件A+B概率是：', event_a_or_b_2.prob)
    print('设置令AB互斥')
    event_a.set_relation(event_b, 'EXC', True)
    event_a_or_b_3 = event_a + event_b
    print('事件A+B概率是：', event_a_or_b_3.prob)
    print('设置令AB独立')
    event_a.set_relation(event_b, 'IND', True)
    event_a_or_b_4 = event_a + event_b
    print('事件A+B概率是：', event_a_or_b_4.prob)
    print('设置令AB为相同事件')
    event_a.set_relation(event_b, 'EQU', True)
    event_a_or_b_5 = event_a + event_b
    print('事件A+B概率是：', event_a_or_b_5.prob)


def test_seq_2():
    event_a = RandomEvent()
    event_a.set_prob(0, 1)
    event_b = RandomEvent()
    event_b.set_prob(1, 2)
    event_a_and_b = event_a * event_b
    event_a_or_b = event_a + event_b
    print('Done')


if __name__ is '__main__':
    pass
    # todo:更多层级的关系链处理（可能需要递归）
