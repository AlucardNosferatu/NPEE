import kill_thread
from modules.awvs_api import awvs_add_scan, awvs_add_target, awvs_download_report, awvs_generate_report, \
    awvs_get_report_status, awvs_get_scan_status, awvs_start
from modules.binwalk_api import binwalk_check, binwalk_scan
from modules.console import console_login, console_send, console_close, console_read_loop
from modules.excel_handler import read_template, read_testcases, write_summary
from modules.http_eweb_api import eweb_get_sid, eweb_inject_cmd
from modules.misc import ip_ping, mac_generate, mac_increase, mac_read_record, mac_write_record, timer, nop, \
    interactive_shell, process_kill, timer_transience, get_input_str
from modules.misc_singleton import wifi_connect
from modules.nessus_api import nessus_delete_stop, nessus_export, nessus_find, nessus_get_status, nessus_login, \
    nessus_new_scan, nessus_start_pause
from modules.nmap_api import nmap_init, nmap_scan
from modules.power_supply import ps_init, ps_reset, ps_acdc, ps_range, ps_freq, ps_toggle, ps_volt
from modules.logger import log_logger_init, log_handler_init
from modules.rgscan_api import rgscan_download_report, rgscan_generate_report, rgscan_get_scan_status, \
    rgscan_scan_target, rgscan_start
from modules.rsas_api import rsas_download_report, rsas_generate_report, rsas_get_report_status, rsas_get_scan_status, \
    rsas_scan_target, rsas_start
from modules.web_api import web_click, web_find, web_find_click, web_find_input, web_goto, web_start
from modules.webhook_api import webhook_send
from modules.zap_api import zap_crawl_target, zap_download_report, zap_get_crawl_status, zap_get_scan_status, \
    zap_init_adapter, zap_kill_java, zap_scan_target, zap_start_exe
from modules.mqtt_api import mqtt_init, mqtt_subscribe, mqtt_read_start, mqtt_read_stop

_ = kill_thread.kill_thread
m_dict = {
    'WEBHOOK_SEND': webhook_send,

    'MQTT_INIT': mqtt_init, 'MQTT_SUBSCRIBE': mqtt_subscribe, 'MQTT_READ_START': mqtt_read_start,
    'MQTT_READ_STOP': mqtt_read_stop,

    'BINWALK_SCAN': binwalk_scan, 'BINWALK_CHECK': binwalk_check,

    'LOG_LOGGER_INIT': log_logger_init, 'LOG_HANDLER_INIT': log_handler_init,

    # 'ANDROID_INIT_DEVICE': android_init_device, 'ANDROID_INTERACT_DEVICE': android_interact_device,

    # 'CV_CUT_IMG': cv_cut_img, 'CV_OCR_IMG': cv_ocr_img, 'CV_SHOW_IMG': cv_show_img, 'CV_INIT_CAP': cv_init_cap,
    # 'CV_IS_CAP_OPENED': cv_is_cap_opened, 'CV_READ_CAP': cv_read_cap, 'CV_CLOSE_CAP': cv_close_cap,
    # 'CV_GRAB_CAP': cv_grab_cap, 'CV_KEY_IMG': cv_key_img, 'CV_READ_IMG': cv_read_img,

    'PS_INIT': ps_init, 'PS_RESET': ps_reset, 'PS_ACDC': ps_acdc, 'PS_RANGE': ps_range, 'PS_FREQ': ps_freq,
    'PS_TOGGLE': ps_toggle, 'PS_VOLT': ps_volt,

    'IP_PING': ip_ping, 'WIFI_CONNECT': wifi_connect, 'TIMER': timer, 'TIMER_TRANSIENCE': timer_transience, 'NOP': nop,
    'INTERACTIVE_SHELL': interactive_shell, 'PROCESS_KILL': process_kill, 'GET_INPUT_STR': get_input_str,

    # 'CHARIOT_INIT': chariot_init, 'CHARIOT_SET_DURATION': chariot_set_duration,
    # 'CHARIOT_ADD_PAIRS': chariot_add_pairs, 'CHARIOT_RUN': chariot_run, 'CHARIOT_GET_THR': chariot_get_thr,

    'WEB_START': web_start, 'WEB_GOTO': web_goto, 'WEB_FIND_INPUT': web_find_input, 'WEB_FIND_CLICK': web_find_click,
    'WEB_FIND': web_find, 'WEB_CLICK': web_click,

    'READ_TEMPLATE': read_template, 'READ_TESTCASES': read_testcases, 'WRITE_SUMMARY': write_summary,

    'CONSOLE_LOGIN': console_login, 'CONSOLE_SEND': console_send, 'CONSOLE_CLOSE': console_close,
    'CONSOLE_READ_LOOP': console_read_loop,

    # 'CONSOLE_GET_AP_CLI': console_get_ap_cli, 'CONSOLE_GET_RADIO_INFO': console_get_radio_info,
    # 'CONSOLE_IWPRIV_SITE_SURVEY': console_iwpriv_site_survey, 'CONSOLE_IWPRIV_STAT': console_iwpriv_stat,
    # 'CONSOLE_IWPRIV_REG': console_iwpriv_reg,

    'EWEB_GET_SID': eweb_get_sid, 'EWEB_INJECT_CMD': eweb_inject_cmd,

    # 'WINUI_GET_DESKTOP': winui_get_desktop, 'WINUI_GET_EXPLORER': winui_get_explorer,
    # 'WINUI_LOCATE_WINDOW': winui_locate_window, 'WINUI_LOCATE_ELEMENT': winui_locate_element,
    # 'WINUI_HINT': winui_hint, 'WINUI_CLICK_ELEMENT': winui_click_element,
    # 'WINUI_CAPTURE_WINDOW': winui_capture_window, 'WINUI_CLOSE_WINDOW': winui_close_window,

    # 'DB_CONNECT': db_connect, 'DB_READ_SQL': db_read_sql, 'DB_DISCONNECT': db_disconnect,
    # 'DB_READ_REDIS': db_read_redis, 'DB_WRITE_REDIS': db_write_redis, 'DB_DELETE_REDIS': db_delete_redis,
    # 'DB_EXIST_REDIS': db_exist_redis, 'DB_WRITE_SQL': db_write_sql, 'DB_INSERT_SQL': db_insert_sql,

    'NESSUS_LOGIN': nessus_login, 'NESSUS_NEW_SCAN': nessus_new_scan, 'NESSUS_FIND': nessus_find,
    'NESSUS_START_PAUSE': nessus_start_pause, 'NESSUS_GET_STATUS': nessus_get_status, 'NESSUS_EXPORT': nessus_export,
    'NESSUS_DELETE_STOP': nessus_delete_stop,

    'ZAP_KILL_JAVA': zap_kill_java, 'ZAP_START_EXE': zap_start_exe, 'ZAP_INIT_ADAPTER': zap_init_adapter,
    'ZAP_CRAWL_TARGET': zap_crawl_target, 'ZAP_GET_CRAWL_STATUS': zap_get_crawl_status,
    'ZAP_SCAN_TARGET': zap_scan_target, 'ZAP_GET_SCAN_STATUS': zap_get_scan_status,
    'ZAP_DOWNLOAD_REPORT': zap_download_report,

    'RSAS_START': rsas_start, 'RSAS_SCAN_TARGET': rsas_scan_target, 'RSAS_GET_SCAN_STATUS': rsas_get_scan_status,
    'RSAS_GENERATE_REPORT': rsas_generate_report, 'RSAS_GET_REPORT_STATUS': rsas_get_report_status,
    'RSAS_DOWNLOAD_REPORT': rsas_download_report,

    'AWVS_START': awvs_start, 'AWVS_ADD_TARGET': awvs_add_target, 'AWVS_ADD_SCAN': awvs_add_scan,
    'AWVS_GET_SCAN_STATUS': awvs_get_scan_status, 'AWVS_GENERATE_REPORT': awvs_generate_report,
    'AWVS_GET_REPORT_STATUS': awvs_get_report_status, 'AWVS_DOWNLOAD_REPORT': awvs_download_report,

    'RGSCAN_START': rgscan_start, 'RGSCAN_SCAN_TARGET': rgscan_scan_target,
    'RGSCAN_GET_SCAN_STATUS': rgscan_get_scan_status, 'RGSCAN_GENERATE_REPORT': rgscan_generate_report,
    'RGSCAN_DOWNLOAD_REPORT': rgscan_download_report,

    'NMAP_INIT': nmap_init, 'NMAP_SCAN': nmap_scan,

    'MAC_GENERATE': mac_generate, 'MAC_INCREASE': mac_increase, 'MAC_READ_RECORD': mac_read_record,
    'MAC_WRITE_RECORD': mac_write_record
}

# pyinstaller打包exe时修改这个来实现依赖裁剪
