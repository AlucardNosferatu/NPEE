import sympy

from DiscreteRV import DiscreteRandomVar, GeometricDist
from ContinuousRV import ContinuousRandomVar


def drv_function(drv_x: DiscreteRandomVar, gx):
    gx_var = list(gx.free_symbols)[0]
    if drv_x.rv_type == 'finite':
        old_seg_list = drv_x.regions[:-1]
        old_law_list = drv_x.dist_laws[1:]
        new_pair_dict = {}
        for i in range(0, len(old_seg_list)):
            old_seg_point = old_seg_list[i][1]
            new_sp: object = gx.subs(gx_var, old_seg_point)
            if new_sp in new_pair_dict:
                new_pair_dict[new_sp] = new_pair_dict[new_sp] + old_law_list[i]
            else:
                new_pair_dict[new_sp] = old_law_list[i]
        new_pair_list: list[tuple] = sorted(
            new_pair_dict.items(),
            key=lambda x: x[0],
            reverse=False
        )
        new_seg_list = []
        new_law_list = [0]
        for i in range(0, len(new_pair_list)):
            new_seg_list.append(new_pair_list[i][0])
            new_law_list.append(new_pair_list[i][1])
        drv_y = DiscreteRandomVar(seg_p=new_seg_list, laws=new_law_list)
    else:
        y_equ_to_gx = sympy.Symbol('y')
        new_regions = gx.subs(gx_var, drv_x.regions)
        xs_with_same_gx = sympy.solve(sympy.Eq(new_regions, y_equ_to_gx), gx_var)
        new_laws = drv_x.dist_laws

        drv_y = None
    return drv_y


class CRVFunction:
    def __init__(self, crv_x: ContinuousRandomVar, gx):
        pass


if __name__ == '__main__':
    # sp1 = [-1, 0, 1]
    # f1 = [
    #     sympy.sympify(0),
    #     sympy.Rational(3, 10),
    #     sympy.Rational(8, 10),
    #     sympy.sympify(1)
    # ]

    rv1 = GeometricDist(sympy.Rational(1, 3))
    x_sym = sympy.Symbol('x')
    drv_f = drv_function(drv_x=rv1, gx=sympy.Mod(x_sym, 3))
