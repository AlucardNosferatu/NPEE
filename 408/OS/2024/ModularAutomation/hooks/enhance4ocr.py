def h0(params):
    params['cv']['key_lb'] = [0, 128, 0]
    params['cv']['key_ub'] = [128, 255, 128]
    return params
