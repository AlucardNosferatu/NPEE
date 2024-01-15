import os

from core.flow_chart import FlowChart

if __name__ == '__main__':
    # noinspection SpellCheckingInspection
    params = {
        'tes': {
            # 'work_dir': r'C:\Users\16413\Desktop\Job\Business\RJ_HIBG\安全扫描\国内\X30E-R231',
            'scan_folder': '升级文件',
            'pic_path': r'C:\Users\16413\Desktop\Job\Business\RJ_HIBG\安全扫描\国内\X30E-R231\TES扫描结果.png'
        }
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='antivirus_tes.py', map_json='TES反病毒测试.pos')
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
