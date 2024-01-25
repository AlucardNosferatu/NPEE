from modules.modules_dict import m_dict
if __name__ == '__main__':
    params_ = {
        'flowchart': {
            'old_fc_name': '延迟解析',
            'new_fc_name': '延迟解析',
            'new_fc_pre': {
                'cv': {
                    'ocr_extra_config': '-c tessedit_char_whitelist=0123456789ms --psm 6'
                }
            },
            'new_fc_hook': 'mobile_game_delay.py',
            'new_fc_map': '应用延迟测量.pos',
            'new_fc_log': 'mobile_game_delay',
            'node_cat': 'p',
            'node_type': 'CV_CUT_IMG',
            'to_link': 'H1',
            'from_link': 'H1'
        }
    }
    params_ = m_dict['FLOWCHART_INIT'](params=params_)
    params_ = m_dict['FLOWCHART_STEP'](params=params_)
    params_ = m_dict['FLOWCHART_SET_NODE'](params=params_)
