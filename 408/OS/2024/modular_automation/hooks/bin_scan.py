import time

# from hooks.selenium.common import NoSuchElementException
# 当需要加载模块依赖中没有的库时用上面那行
from selenium.common import NoSuchElementException


def h0(params):
    return params


# 跳转SCA网址
def h1(params):
    params['web'].__setitem__('goto_url', 'http://ci.cloud.ruijie.net/')
    return params


# SID认证，输入用户名
def h2(params):
    time.sleep(5)
    params['web'].__setitem__('find_value', '//*[@id="login-normal"]/div[2]/form/div[1]/nz-input-group/input')
    params['web'].__setitem__('input_text', 'linhaobo')
    return params


# SID认证，输入密码
def h3(params):
    params['web'].__setitem__('find_value', '//*[@id="login-normal"]/div[2]/form/div[2]/nz-input-group/input')
    params['web'].__setitem__('input_text', 'LostXmas20291224')
    return params


# SID认证，确认登录
def h4(params):
    params['web'].__setitem__('find_value', '//*[@id="login-normal"]/div[2]/form/div[6]/div/button')
    return params


# 进入扫描配置页面
def h5(params):
    time.sleep(5)
    params['web'].__setitem__('find_value', '//*[@id="app"]/div/div[1]/div[2]/div[1]/div/ul/div[14]/li/ul/div[3]/a/li')
    params['web']['div_counter'] = ['a', 'b']
    return params


# 点击项目筛选
def h6(params):
    time.sleep(1)
    params['web'].__setitem__('find_value', '//*[@id="app"]/div/div[2]/section/div/form/div[1]/div/div/div/input')
    if 'c' not in params['web']['div_counter']:
        params['web']['div_counter'].append('c')
    return params


# 查找项目/产品，第一次
def h7(params):
    time.sleep(5)
    params['xpath_index'] = 1
    params['xpath_template'] = '/html/body/div[{}]/div[1]/div[1]/ul/li[{}]/span'.format(
        len(params['web']['div_counter']), '{}'
    )
    params['web']['find_by'] = 'xpath'
    params['web']['find_value'] = params['xpath_template'].format(params['xpath_index'])
    return params


# 检查是否遍历了全部项目
def h8(params):
    find_result = params['web']['find_result']
    if type(find_result) is NoSuchElementException:
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


# 检查遍历的项目是否为目标项目
def h9(params):
    assert 'project_id' in params.keys()
    project_id = params['project_id']
    find_result = params['web']['find_result']
    text_content = find_result.get_property('textContent')
    if text_content != project_id:
        params['if_switch'] = False
    else:
        params['if_switch'] = True
    return params


# 新建任务
def h10(params):
    time.sleep(1)
    params['web'].__setitem__('find_value', '//*[@id="app"]/div/div[2]/section/div/form/div[3]/div/button[2]')
    if 'e' not in params['web']['div_counter']:
        params['web']['div_counter'].append('e')
    return params


# 遍历项目/产品列表的下一个项目/产品
def h11(params):
    params['xpath_index'] += 1
    params['web']['find_by'] = 'xpath'
    params['web']['find_value'] = params['xpath_template'].format(params['xpath_index'])
    return params


# 找到目标项目/产品，点击选中该项目/产品
def h12(params):
    find_result = params['web']['find_result']
    del params['web']['find_result']
    params['web']['click_obj'] = find_result
    return params


# 点击产品筛选
def h13(params):
    time.sleep(1)
    params['web'].__setitem__('find_value', '//*[@id="app"]/div/div[2]/section/div/form/div[2]/div/div/div/input')
    if 'd' not in params['web']['div_counter']:
        params['web']['div_counter'].append('d')
    return params


# 检查遍历的产品是否为目标产品
def h14(params):
    assert 'product_id' in params.keys()
    project_id = params['product_id']
    find_result = params['web']['find_result']
    text_content = find_result.get_property('textContent')
    if text_content != project_id:
        params['if_switch'] = False
    else:
        params['if_switch'] = True
    return params


# 项目和产品均已选中，点击查询
def h15(params):
    time.sleep(1)
    params['web']['find_value'] = '//*[@id="app"]/div/div[2]/section/div/form/div[3]/div/button[1]'
    return params


# 点击修改任务
def h16(params):
    time.sleep(1)
    params['web'][
        'find_value'
    ] = '//*[@id="app"]/div/div[2]/section/div/div[1]/div[5]/div[2]/table/tbody/tr/td[15]/div/button'
    if 'e' not in params['web']['div_counter']:
        params['web']['div_counter'].append('e')
    return params


# 输入基线项目
def h17(params):
    assert 'baseline_project' in params.keys()
    baseline_project = params['baseline_project']
    params['web'].__setitem__(
        'find_value',
        '//*[@id="app"]/div/div[2]/section/div/div[3]/div/div[2]/form/div[1]/div/div/input'
    )
    params['web']['input_text'] = baseline_project
    return params


# 输入项目
def h18(params):
    assert 'project_id' in params.keys()
    project_id = params['project_id']
    params['web'].__setitem__(
        'find_value',
        '//*[@id="app"]/div/div[2]/section/div/div[3]/div/div[2]/form/div[2]/div/div/input'
    )
    params['web']['input_text'] = project_id
    return params


# 输入产品
def h19(params):
    assert 'product_id' in params.keys()
    product_id = params['product_id']
    params['web'].__setitem__(
        'find_value',
        '//*[@id="app"]/div/div[2]/section/div/div[3]/div/div[2]/form/div[3]/div/div/input'
    )
    params['web']['input_text'] = product_id
    return params


# 点击战区下拉框
def h20(params):
    time.sleep(1)
    params['web'].__setitem__(
        'find_value',
        '//*[@id="app"]/div/div[2]/section/div/div[3]/div/div[2]/form/div[4]/div/div/div/input'
    )
    if 'f' not in params['web']['div_counter']:
        params['web']['div_counter'].append('f')
    return params


# 点击家庭互联事业部
def h21(params):
    time.sleep(1)
    params['web'].__setitem__(
        'find_value', '/html/body/div[{}]/div[1]/div[1]/ul/li[12]'.format(len(params['web']['div_counter']))
    )
    return params


# 点击提交BUG下拉框
def h22(params):
    time.sleep(1)
    params['web'].__setitem__(
        'find_value',
        '//*[@id="app"]/div/div[2]/section/div/div[3]/div/div[2]/form/div[5]/div/div/div[1]/input'
    )
    if 'g' not in params['web']['div_counter']:
        params['web']['div_counter'].append('g')
    return params


# 点击不提交BUG
def h23(params):
    time.sleep(1)
    params['web'].__setitem__(
        'find_value', '/html/body/div[{}]/div[1]/div[1]/ul/li[1]'.format(len(params['web']['div_counter']))
    )
    return params


# 输入BIN地址
def h24(params):
    assert 'bin_url' in params.keys()
    bin_url = params['bin_url']
    params['web'].__setitem__(
        'find_value',
        '//*[@id="app"]/div/div[2]/section/div/div[3]/div/div[2]/form/div[6]/div/div/input'
    )
    params['web']['input_text'] = bin_url
    return params


# 点击确认，开始测试
def h25(params):
    time.sleep(1)
    if 'dont_create' in params.keys() and params['dont_create']:
        params['web'].__setitem__('find_value', '//*[@id="app"]/div/div[2]/section/div/div[3]/div/div[3]/div/button[1]')
    else:
        params['web'].__setitem__('find_value', '//*[@id="app"]/div/div[2]/section/div/div[3]/div/div[3]/div/button[2]')
    div_counter: list = params['web']['div_counter']
    if 'e' in div_counter:
        div_counter.remove('e')
    return params


# 查找表格首行的报告生成状态
def h26(params):
    params['web']['find_by'] = 'xpath'
    params['web']['find_value'] = '//*[@id="app"]/div/div[2]/section/div/div[1]/div[3]/table/tbody/tr/td[10]/div/div'
    return params


# 判断报告是否生成
def h27(params):
    find_result = params['web']['find_result']
    text_content = find_result.get_property('textContent')
    if text_content == '是':
        params['if_switch'] = True
    else:
        params['if_switch'] = False
    return params


# 等待10s，点击查询
def h28(params):
    time.sleep(10)
    params = h15(params=params)
    return params


# 点击开源组件漏洞
def h29(params):
    params['web']['find_value'] = '//*[@id="app"]/div/div[1]/div[2]/div[1]/div/ul/div[14]/li/ul/div[6]/a'
    params['web']['div_counter'] = ['a', 'b']
    return params


# 点击项目筛选，这次等久一点
def h30(params):
    time.sleep(10)
    params = h6(params=params)
    return params


# 查询页面，点击查询
def h31(params):
    params['web']['find_value'] = '//*[@id="app"]/div/div[2]/section/div/form/div[12]/div/button[1]'
    return params


# 查询页面，点击导出
def h32(params):
    time.sleep(10)
    params['web']['find_value'] = '//*[@id="app"]/div/div[2]/section/div/form/div[12]/div/button[6]'
    return params


# 结束
def h33(params):
    time.sleep(20)
    return params
