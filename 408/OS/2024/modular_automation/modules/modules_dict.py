from modules.console import console_login, console_send, console_get_ap_cli, console_get_radio_info, \
    console_iwpriv_site_survey, console_iwpriv_stat, console_iwpriv_reg
from modules.excel_handler import read_template, read_testcases, write_summary
from modules.nmap_api import nmap_init, nmap_scan

m_dict = {

    'READ_TEMPLATE': read_template, 'READ_TESTCASES': read_testcases, 'WRITE_SUMMARY': write_summary,

    'CONSOLE_LOGIN': console_login, 'CONSOLE_SEND': console_send,
    'CONSOLE_GET_AP_CLI': console_get_ap_cli, 'CONSOLE_GET_RADIO_INFO': console_get_radio_info,
    'CONSOLE_IWPRIV_SITE_SURVEY': console_iwpriv_site_survey, 'CONSOLE_IWPRIV_STAT': console_iwpriv_stat,
    'CONSOLE_IWPRIV_REG': console_iwpriv_reg,

    'NMAP_INIT': nmap_init, 'NMAP_SCAN': nmap_scan,

}

# 打包时修改这个来实现依赖裁剪
