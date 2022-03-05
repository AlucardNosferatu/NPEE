import sympy


class RandomEvent:
    prob_de = 0
    prob_nu = 0
    prob = None
    include = None
    exclude = None
    ind = None
    be_included = None
    Calculable = False

    def __init__(self, prob_nu=None, prob_de=None):
        self.Calculable = False
        self.include = []
        self.exclude = []
        self.ind = []
        self.be_included = []
        if prob_de is not None and prob_nu is not None:
            self.set_prob(prob_de=prob_de, prob_nu=prob_nu)

    def refresh_prob(self):
        self.prob = sympy.Rational(self.prob_nu, self.prob_de)
        if self.prob in [sympy.Rational(0, 1), sympy.Rational(1, 1)]:
            self.ind.clear()
            self.ind.append('all')
        self.Calculable = True

    def set_prob(
            self,
            prob_nu: int = None,
            prob_de: int = None,
            prob: sympy.Rational = None
    ):

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

    def set_relation(
            self,
            b_event: 'RandomEvent',
            rel: str,
            recursive=0,
            both_side=False
    ):
        if rel == 'INC':

            # region P(AB)≤P(B)
            if self.Calculable and b_event.Calculable:
                if self.prob < b_event.prob:
                    print('B⊆A, P(A)≥P(B), This setting has been ignored.')
                    return
            # endregion

            # region process b_event
            if b_event not in self.include:
                self.include.append(b_event)
            if b_event in self.exclude:
                self.exclude.remove(b_event)
            # endregion

            # region process included events of b_event
            if recursive > 0:
                for b_inc in b_event.include:
                    self.set_relation(b_inc, 'INC', recursive - 1, True)
            # endregion

            # region process in b_event side
            if both_side:
                b_event.set_relation(self, 'BE_INC', recursive)
            # endregion

        elif rel == 'BE_INC':

            # region P(AB)≤P(B)
            if self.Calculable and b_event.Calculable:
                if self.prob > b_event.prob:
                    print('B⊆A, P(A)≥P(B), This setting has been ignored.')
                    return
            # endregion

            # region process b_event
            if b_event not in self.be_included:
                self.be_included.append(b_event)
            if b_event in self.exclude:
                self.exclude.remove(b_event)
            # endregion

            # region process be_included events of b_event
            if recursive > 0:
                for b_be_inc in b_event.be_included:
                    self.set_relation(b_be_inc, 'BE_INC', recursive - 1, True)
            # endregion

            # region process in b_event side
            if both_side:
                b_event.set_relation(self, 'INC', recursive)
            # endregion

        elif rel == 'EXC':

            if b_event in self.include:
                self.include.remove(b_event)
            if b_event in self.ind:
                self.ind.remove(b_event)
            if b_event in self.be_included:
                self.be_included.remove(b_event)
            self.exclude.append(b_event)

            if recursive > 0:
                for b_inc in b_event.include:
                    self.set_relation(b_inc, 'EXC', recursive - 1)

            if both_side:
                b_event.set_relation(self, 'EXC', recursive)

        elif rel == 'IND':
            poss_1or0_self = self.Calculable and self.prob in [
                sympy.Rational(0, 1),
                sympy.Rational(1, 1)
            ]
            poss_1or0_b = b_event.Calculable and b_event.prob in [
                sympy.Rational(0, 1),
                sympy.Rational(1, 1)
            ]
            if not poss_1or0_self and not poss_1or0_b:
                if b_event in self.include:
                    self.include.remove(b_event)
                if b_event in self.be_included:
                    self.be_included.remove(b_event)
                if b_event in self.exclude:
                    self.exclude.remove(b_event)
                self.ind.append(b_event)
            if recursive > 0:
                for b_inc in b_event.include:
                    self.set_relation(b_inc, 'IND', recursive - 1, True)
            if both_side:
                b_event.set_relation(self, 'IND', recursive)
        else:
            print('You moron!')

    def get_relation(self, b_event: 'RandomEvent'):
        rel_list = {
            '包含': b_event in self.include,
            '包含于': b_event in self.be_included,
            '互斥': b_event in self.exclude,
            '独立': b_event in self.ind or 'all' in b_event.ind + self.ind
        }
        mutual_inclusion = not (not rel_list['包含'] or not rel_list['包含于'])
        neither_exc_nor_ind = not rel_list['互斥'] and not rel_list['独立']
        rel_list['相等'] = mutual_inclusion and neither_exc_nor_ind
        complementary_prob = b_event.Calculable and (b_event.prob == 1 - self.prob)
        rel_list['互逆'] = complementary_prob and rel_list['互斥']
        return rel_list

    def uninstall(self, b_event: 'RandomEvent'):
        if self in b_event.ind:
            b_event.ind.remove(self)
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
        ne_poss_1or0 = 'all' in new_event.ind
        self_poss_1or0 = 'all' in self.ind
        other_poss_1or0 = 'all' in other.ind
        if not ne_poss_1or0 and not self_poss_1or0:
            new_event.set_relation(self, 'INC', 0, True)
        if not ne_poss_1or0 and not other_poss_1or0:
            new_event.set_relation(other, 'INC', 0, True)
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
        self_poss_1or0 = 'all' in self.ind
        other_poss_1or0 = 'all' in other.ind
        if other.Calculable and self.Calculable:
            mutual_ind = other in self.ind and self in other.ind
            if self_poss_1or0 or other_poss_1or0 or mutual_ind:
                new_event.set_prob(prob=self.prob * other.prob)
        ne_poss_1or0 = 'all' in new_event.ind
        if not ne_poss_1or0 and not self_poss_1or0:
            new_event.set_relation(self, 'BE_INC', 0, True)
        if not ne_poss_1or0 and not other_poss_1or0:
            new_event.set_relation(other, 'BE_INC', 0, True)
        return new_event

    def __neg__(self):
        new_event = RandomEvent()
        if self.Calculable:
            new_event.set_prob(prob=1 - self.prob)
        new_event.set_relation(self, 'EXC', 0, True)
        for e in self.exclude:
            new_event.set_relation(e, 'INC', 0, True)
        for e in self.include:
            new_event.set_relation(e, 'EXC', 0, True)
        for e in self.ind:
            new_event.set_relation(e, 'IND', 0, True)
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
    event_a.set_relation(event_b, 'INC', 0, True)
    print('设置令B包含于A')
    event_b.set_relation(event_a, 'BE_INC', 0, True)
    print('设置令A包含于B')
    event_a.set_relation(event_b, 'BE_INC', 0, True)
    event_a_or_b_2 = event_a + event_b
    print('事件A+B概率是：', event_a_or_b_2.prob)
    print('设置令AB互斥')
    event_a.set_relation(event_b, 'EXC', 0, True)
    event_a_or_b_3 = event_a + event_b
    print('事件A+B概率是：', event_a_or_b_3.prob)
    print('设置令AB独立')
    event_a.set_relation(event_b, 'IND', 0, True)
    event_a_or_b_4 = event_a + event_b
    print('事件A+B概率是：', event_a_or_b_4.prob)


def test_seq_2():
    event_a = RandomEvent()
    event_a.set_prob(0, 1)
    event_b = RandomEvent()
    event_b.set_prob(1, 1)
    event_c = RandomEvent()
    event_c.set_prob(1, 2)
    event_a_and_c = event_a * event_c
    event_a_or_c = event_a + event_c
    event_b_and_c = event_b * event_c
    event_b_or_c = event_b + event_c
    print(event_a_and_c)
    print(event_a_or_c)
    print(event_b_and_c)
    print(event_b_or_c)
    print('Done')


def test_seq_3():
    event_a = RandomEvent()
    event_a.set_prob(1, 2)
    event_b = RandomEvent()
    event_b.set_prob(1, 3)
    event_c = RandomEvent()
    event_c.set_prob(1, 4)
    event_d = RandomEvent()
    event_d.set_prob(1, 5)
    event_c.set_relation(event_d, 'INC', 0, True)
    event_b.set_relation(event_c, 'INC', 0, True)
    event_a.set_relation(event_b, 'INC', 2, True)


def test_seq_4():
    event_a = RandomEvent()
    event_a.set_prob(1, 2)
    event_b = RandomEvent()
    event_b.set_prob(1, 2)
    event_c = RandomEvent()
    event_c.set_prob(1, 4)
    event_d = RandomEvent()
    event_d.set_prob(1, 5)
    print('执行A包含B')
    event_a.set_relation(event_b, 'INC', 2, True)
    print('执行B被C包含，但是P(C)<P(B)，忽略')
    event_b.set_relation(event_c, 'BE_INC', 2, True)
    print('执行CD互斥')
    event_c.set_relation(event_d, 'EXC', 2, True)
    print('执行DA独立，A包含B，DB也独立')
    event_d.set_relation(event_a, 'IND', 2, True)
    print('执行E=A')
    event_e = -event_a
    print('执行B包含A')
    event_a.set_relation(event_b, 'BE_INC', 2, True)
    rel_a_b = event_a.get_relation(event_b)
    rel_a_c = event_a.get_relation(event_c)
    rel_a_d = event_a.get_relation(event_d)
    rel_b_c = event_b.get_relation(event_c)
    rel_b_d = event_b.get_relation(event_d)
    rel_c_d = event_c.get_relation(event_d)
    rel_a_e = event_a.get_relation(event_e)
    print('rel_a_b', rel_a_b)
    print('rel_a_c', rel_a_c)
    print('rel_a_d', rel_a_d)
    print('rel_b_c', rel_b_c)
    print('rel_b_d', rel_b_d)
    print('rel_c_d', rel_c_d)
    print('rel_a_e', rel_a_e)


if __name__ == '__main__':
    print()
    test_seq_4()
    # todo:测试
