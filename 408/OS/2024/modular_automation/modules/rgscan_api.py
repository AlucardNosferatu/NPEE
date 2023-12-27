import json
import os
import re
import time
import zipfile

from modules.http_api import http_post, http_get

report_download_path = 'reports'
accept_encoding = 'gzip, deflate, br'
accept_language = 'zh-CN,zh;q=0.9,en;q=0.8'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 ' \
             'Safari/537.36'
x_req_with = 'XMLHttpRequest'
timeout_hours = 2
cookie = 'style_color=deepblue; threshold=80; tb=; p_len=10; adminid=118; adminname=ceshi; admintype=1; random={}; ' \
         'SYS_TIMEOUT={}; hwtype=box; p_level=3'.format('{}', timeout_hours * 60 * 60)
rg_scan_ip = '172.27.5.249'


class RGScan:
    token = ''
    server_ip = ''
    server_url = ''
    assets_group_id = None

    def __init__(self, rg_scan_token, server_ip=None, assets_group_id=None):
        self.token = rg_scan_token
        if server_ip is None:
            self.server_ip = rg_scan_ip
        else:
            self.server_ip = server_ip
        self.server_url = 'https://' + self.server_ip
        if assets_group_id is None:
            self.assets_group_id = 0
        else:
            self.assets_group_id = assets_group_id

    def get_headers(self):
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': accept_encoding,
            'Accept-Language': accept_language,
            'User-Agent': user_agent,
            'X-Requested-With': x_req_with,
            'Cookie': cookie.format(self.token),
            'Referer': self.server_url + '/main/'
        }
        return headers

    def add_target(self, address, name):
        headers = self.get_headers()
        url = self.server_url + '/hyberchannel/newtask/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        csrf_token = re.findall('"csrf_token" value="(.*?)"', result.text)[0]

        headers = self.get_headers()
        headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        headers['Content-Type'] = 'multipart/form-data; boundary=----WebKitFormBoundaryarABxQY4JYPidel1'
        body = '''------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="csrf_token"

{}
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="rayscan_enable_sysscan"

true
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="rayscan_enable_webscan"

true
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="rayscan_enable_crack"

true
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="task_type"

0
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="vul_id"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="target_mode"

0
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="target"

{}
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="file"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ag_id"

0
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="name"

{}
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="schedule"

0
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="week"

1
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="month"

1
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="date"

{}
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="time"

{}
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="vul_plugin"

1
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="scan_plugin"

2
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="dist_engine"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="scan_prior"

1
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="vul_trtid"

138
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="scan_trtid"

139
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="alarm_modal_receive"

0
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="submit_verify"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="host_alive"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_more_false_alarm"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="show_exfml_vuln"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_eneble_randomscan"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_eneble_smb"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_timeout_plugin"

30
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_timeout_net"

30
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_count_host"

5
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_count_scan"

200
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_count_scanhost"

15
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_count_scantcp"

19
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="sys_engine_timeout"

0
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="account_snmp_connect"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="account_snmp_port"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="account_wsus_server"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="account_wsus_port"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="account_wsus_username"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="account_wsus_password"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="account_wsus_https"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="starturl"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="otherurl"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="domain"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="path"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="excurl"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="atobj_type"

none
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="atobj_user"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="atobj_pass"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="atobj_cookie"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="atobj_url"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="atobj_data"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="cer"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ca_key_pass"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ca_jks_base64"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="threadnum"

5
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="casesense"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="similarpage"

20
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="dirfilenum"

100
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="network_retry"

3
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="network_timeout"

30
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="scan_engine_timeout"

0
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="network_proxy_type"

none
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="network_proxy_ip"

127.0.0.1
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="network_proxy_port"

8080
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="network_proxy_user"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="network_proxy_pass"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="hiddenlink_keyword"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="trojan"

on
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_depth"

5
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_crawlemethod"

1
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_useragent"

Mozilla/5.0 compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_autofill"

1
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_pagecountlimit"

1000
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_pagesizelimit"

5120
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_excurl"

logout.,sigout.,exit.
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_excfiletype"

.rar,.wmv,.doc,.docx,.avi,.rmvb,.asf,.asx,.mid,.bin,.cab,.exe,.ico,.mdb,.mov,.mp3,.mp4,.mpeg,.mpg,.msi,.pdf,.ppt,.psd,.ra,.ram,.rm,.rpm,.tar,.tgz,.tif,.tiff,.wav,.wma,.xls,.zip
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="http_excparam"

ASP.NET_SessionID,ASPSESSIONID,PHPSESSID,SITESERVER,sessid,__VIEWSTATE,__VIEWSTATEENCRYPTED,__EVENTVALIDATION,__EVENTTARGET,__EVENTARGUMENT,jsessionid,cfid,cftoken,authenticity_token
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_telnet_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_telnet_mix"

1
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_telnet_user"

2
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_telnet_pwd"

3
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="telnet_port"

23
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_telnet_param"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_ftp_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_ftp_mix"

4
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_ftp_user"

5
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_ftp_pwd"

6
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ftp_port"

21
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_ssh_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_ssh_mix"

7
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_ssh_user"

8
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_ssh_pwd"

9
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ssh_port"

22
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_pop3_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_pop3_mix"

10
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_pop3_user"

11
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_pop3_pwd"

12
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="pop3_port"

110
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_smb_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_smb_mix"

13
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_smb_user"

14
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_smb_pwd"

15
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="smb_port"

445
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_snmp_type"

normal
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_snmp_pwd"

18
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="snmp_port"

161
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_rdp_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_rdp_mix"

19
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_rdp_user"

20
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_rdp_pwd"

21
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="rdp_port"

3389
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_smtp_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_smtp_mix"

40
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_smtp_user"

41
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_smtp_pwd"

42
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="smtp_port"

25
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_tomcat_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_tomcat_mix"

50
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_tomcat_user"

51
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_tomcat_pwd"

52
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="tomcat_port"

8080
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_oracle_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_oracle_mix"

22
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_oracle_user"

23
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_oracle_pwd"

24
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="oracle_port"

1521
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="oracle_sid"


------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_redis_type"

normal
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_redis_pwd"

43
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="redis_port"

6379
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mysql_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mysql_mix"

25
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mysql_user"

26
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mysql_pwd"

27
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="mysql_port"

3306
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_postgres_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_postgres_mix"

28
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_postgres_user"

29
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_postgres_pwd"

30
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="postgres_port"

5432
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mssql_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mssql_mix"

31
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mssql_user"

32
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mssql_pwd"

33
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="mssql_port"

1433
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_db2_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_db2_mix"

34
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_db2_user"

35
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_db2_pwd"

36
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="db2_port"

50000
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mongodb_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mongodb_mix"

37
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mongodb_user"

38
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mongodb_pwd"

39
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="mongodb_port"

27017
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_mongodb_name"

admin
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_sybase_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_sybase_mix"

44
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_sybase_user"

45
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_sybase_pwd"

46
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="sybase_port"

5000
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_informix_type"

mix
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_informix_mix"

47
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_informix_user"

48
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ct_informix_pwd"

49
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="informix_port"

9090
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_speed"

3
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="engine_maxthread"

5
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="alive_host_detect"

arp
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="alive_host_detect"

icmp
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="alive_host_detect"

tcp
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="alive_host_port_range"

standard
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="alive_host_port_rangecus"

80,443,5432
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="alive_host_port_type"

syn
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="ratelimit_val_select"

K/s
------WebKitFormBoundaryarABxQY4JYPidel1
Content-Disposition: form-data; name="vul_category"


------WebKitFormBoundaryarABxQY4JYPidel1--
                '''.format(csrf_token, address, name, time.strftime("%Y-%m-%d"), time.strftime("%H:%M"))
        url = self.server_url + '/hyberchannel/newtask/save/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        return result.text

    def get_scan_status(self, name):
        headers = self.get_headers()
        headers['Host'] = self.server_ip
        headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        headers['Connection'] = 'keep-alive'
        headers['Cookie'] += '; em=em; reset=threshold'

        body = {
            "sEcho": "2", "iColumns": "8", "sColumns": "", "iDisplayStart": "0", "iDisplayLength": "25",
            "mDataProp_0": "0", "mDataProp_1": "1", "mDataProp_2": "2", "mDataProp_3": "3", "mDataProp_4": "4",
            "mDataProp_5": "5", "mDataProp_6": "6", "mDataProp_7": "7", "sSearch": name, "bRegex": "", "sSearch_0": "",
            "bRegex_0": "false", "bSearchable_0": "true", "sSearch_1": "", "bRegex_1": "false", "bSearchable_1": "true",
            "sSearch_2": "", "bRegex_2": "false", "bSearchable_2": "true", "sSearch_3": "", "bRegex_3": "false",
            "bSearchable_3": "true", "sSearch_4": "", "bRegex_4": "false", "bSearchable_4": "true", "sSearch_5": "",
            "bRegex_5": "false", "bSearchable_5": "true", "sSearch_6": "", "bRegex_6": "false", "bSearchable_6": "true",
            "sSearch_7": "", "bRegex_7": "false", "bSearchable_7": "true", "iSortCol_0": "1", "sSortDir_0": "desc",
            "iSortingCols": "1", "bSortable_0": "false", "bSortable_1": "true", "bSortable_2": "false",
            "bSortable_3": "false", "bSortable_4": "false", "bSortable_5": "false", "bSortable_6": "false",
            "bSortable_7": "false"
        }
        url = self.server_url + '/taskmgr/taskalllist/query/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['params'] = body
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_get(params=params)
        result = params['http']['response']

        result.close()
        return json.loads(result.text)

    def generate_report(self, name):
        headers = self.get_headers()
        url = self.server_url + '/statistic/report/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        csrf_token = re.findall('"csrf_token" value="(.*?)"', result.text)[0]

        body = {'csrf_token': csrf_token}
        url = self.server_url + '/statistic/report/gettasklist/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        task_id = None
        for i in json.loads(result.text)['aData']:
            if name in i['name']:
                task_id = i['id']

        headers = self.get_headers()
        headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        headers['Content-Type'] = 'multipart/form-data; boundary=----WebKitFormBoundaryXEuIQw7pW7t7q2RR'
        body = '''------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="csrf_token"

{}
------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="report_mode"

0
------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="taskids"

{}
------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="labelids"


------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="report_type"

html
------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="report_method"

detail
------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="report_method_by"

by_vul
------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="file_name"

{}
------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="report_zippwd"


------WebKitFormBoundaryXEuIQw7pW7t7q2RR
Content-Disposition: form-data; name="reporttemplate"

1
------WebKitFormBoundaryXEuIQw7pW7t7q2RR--
                            '''.format(csrf_token, task_id, name)
        url = self.server_url + '/statistic/report/savenew/'

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        key = re.findall('key=(.*?)"', result.text)[0]
        return key

    def download_report(self, name, report_id, file_path='', folder_abs=''):
        headers = self.get_headers()
        url = self.server_url + '/statistic/report/download/'
        body = {'key': report_id}

        params = {'http': {}}
        params['http']['url'] = url
        params['http']['data'] = body
        params['http']['data_format'] = 'url_encoded'
        params['http']['headers'] = headers
        params['http']['raw'] = True
        params = http_post(params=params)
        result = params['http']['response']

        if name not in os.listdir(report_download_path):
            os.makedirs(r"{}\{}".format(report_download_path, name))
        with open(file_path, 'wb') as f:
            f.write(result.content)
            f.close()
        zip_file = zipfile.ZipFile(file_path)
        zip_list = zip_file.namelist()  # 得到压缩包里所有文件
        for f in zip_list:
            zip_file.extract(f, folder_abs)
            # 循环解压文件到指定目录
        zip_file.close()  # 关闭文件，必须有，释放内存
        os.remove(file_path)

        file_path = os.path.join(folder_abs, f)
        zip_file = zipfile.ZipFile(file_path)
        zip_list = zip_file.namelist()  # 得到压缩包里所有文件
        for f in zip_list:
            zip_file.extract(f, folder_abs)
            # 循环解压文件到指定目录
        zip_file.close()  # 关闭文件，必须有，释放内存
        os.remove(file_path)

        list_dir = os.listdir(r"{}\{}".format(report_download_path, name))
        for i in list_dir:
            if '详细' in i:
                src_file = r"{}\{}".format(report_download_path, name) + '\\' + i
                dst_file = r"{}\{}\{}-RGSCAN.html".format(report_download_path, name, name)
                os.rename(src_file, dst_file)


def rgscan_start(params):
    login_token = params['rgscan']['login_token']
    params['rgscan']['rgscan_obj'] = RGScan(rg_scan_token=login_token)
    return params


def rgscan_scan_target(params):
    rgscan_obj: RGScan = params['rgscan']['rgscan_obj']
    target_ip = params['rgscan']['target_ip']
    target_desc = params['rgscan']['target_desc']
    finished = False
    while not finished:
        try:
            rgscan_obj.add_target(address=target_ip, name=target_desc)
            finished = True
        except Exception as e:
            _ = e
    return params


def rgscan_get_scan_status(params):
    rgscan_obj: RGScan = params['rgscan']['rgscan_obj']
    target_desc = params['rgscan']['target_desc']
    finished = False
    while not finished:
        try:
            scan_status = rgscan_obj.get_scan_status(name=target_desc)
            params['rgscan']['scan_status'] = scan_status
            finished = True
        except Exception as e:
            _ = e
    return params


def rgscan_generate_report(params):
    rgscan_obj: RGScan = params['rgscan']['rgscan_obj']
    target_desc = params['rgscan']['target_desc']
    finished = False
    while not finished:
        try:
            report_id = rgscan_obj.generate_report(name=target_desc)
            params['rgscan']['report_id'] = report_id
            finished = True
        except Exception as e:
            _ = e
    return params


def rgscan_download_report(params):
    rgscan_obj: RGScan = params['rgscan']['rgscan_obj']
    target_desc = params['rgscan']['target_desc']
    report_id = params['rgscan']['report_id']
    file_path = r"{}\{}\{}-RGSCAN.zip".format(report_download_path, target_desc, target_desc)
    folder_abs = r"{}\{}".format(report_download_path, target_desc)
    finished = False
    while not finished:
        try:
            rgscan_obj.download_report(
                name=target_desc, report_id=report_id, file_path=file_path, folder_abs=folder_abs
            )
            finished = True
        except Exception as e:
            _ = e
    return params


if __name__ == '__main__':
    # rgscan_instance = RGScan(rg_scan_token='c56armw72eguna9kybhcbqd3pfetsvz4')
    # key = rgscan_instance.generate_report(name='EW3000GX_12045245')
    # file_path = r"{}\{}\{}-RGSCAN.zip".format('../reports', 'EW3000GX_12045245', 'EW3000GX_12045245')
    # folder_abs = r"{}\{}".format('../reports', 'EW3000GX_12045245')
    # rgscan_instance.download_report(
    #     name='EW3000GX_12045245', report_id=key, file_path=file_path, folder_abs=folder_abs
    # )
    print('Done')
