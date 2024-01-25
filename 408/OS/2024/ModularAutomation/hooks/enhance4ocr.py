def h0(params):
    return params


def h1(params):
    if 'cv' not in params.keys():
        params['cv'] = {}
    params['cv']['key_lb'] = [0, 128, 0]
    params['cv']['key_ub'] = [128, 255, 128]
    params['if_switch'] = 'debug' in params.keys()
    if params['if_switch']:
        params['cv']['img_path'] = params['debug']
        params['cv']['ocr_extra_config'] = '-c tessedit_char_whitelist=0123456789ms --psm 6'
        if 'delay' in params['cv'].keys():
            del params['cv']['delay']
    return params


def h2(params):
    params['cv']['winname'] = params['cv']['ocr_res']
    return params
