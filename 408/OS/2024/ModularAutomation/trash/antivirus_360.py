import os

from core.flow_chart import FlowChart

if __name__ == '__main__':
    # noinspection SpellCheckingInspection
    params = {
        '360epp': {
            # 'work_dir': r'C:\Users\16413\Desktop\Job\Business\RJ_HIBG\安全扫描\国内\X30E-R231',
            'scan_folder': '升级文件',
            'log_path': r'C:\Program Files (x86)\360\360safe\business\runtime\antivirus\avlog\avlog.db',
            'log_table': 'scandetail',
            'txt_path': r'C:\Users\16413\Desktop\Job\Business\RJ_HIBG\安全扫描\国内\X30E-R231\360扫描结果.txt',
        }
    }
    fc = FlowChart(prerequisite=params)
    fc.load_map(hook_script='antivirus_360.py', map_json='360反病毒测试.pos')
    end = False
    while not end:
        end = fc.run_step()
    os.abort()
