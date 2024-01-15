import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager


def web_start(params):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument(
        '--disable-blink-features=AutomationControlled'
    )  # 关闭自动控制blink特征
    chrome_options.add_argument('--ignore-urlfetcher-cert-requests')
    chrome_options.add_argument('verify=False')
    if 'web' in params.keys():
        if 'proxy' in params['web'].keys():
            proxy = params['web']['proxy']
            del params['web']['proxy']
            chrome_options.add_argument('--proxy-server={}'.format(proxy))
    else:
        params['web'] = {}
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    if 'browser_path' in params['web'].keys():
        service = Service(executable_path=params['web']['browser_path'])
    else:
        service = Service(executable_path=ChromeDriverManager().install())
    web_driver = webdriver.Chrome(options=chrome_options, service=service)
    params.__setitem__('web', {'driver': web_driver})
    return params


def web_goto(params):
    web_params = params['web']
    web_driver: WebDriver = web_params['driver']
    goto_url = web_params['goto_url']
    del web_params['goto_url']
    try:
        web_driver.get(goto_url)
        web_params['exception'] = None
    except Exception as e:
        web_params['exception'] = e
    return params


def web_find(params):
    by_dict = {
        'xpath': By.XPATH,
        'name': By.NAME,
        'id': By.ID,
        'class_name': By.CLASS_NAME
    }
    web_find_params = params['web']
    web_driver: WebDriver = web_find_params['driver']
    web_find_by = web_find_params['find_by']
    del web_find_params['find_by']
    web_find_value = web_find_params['find_value']
    del web_find_params['find_value']
    try:
        web_find_result = web_driver.find_element(
            by=by_dict[web_find_by], value=web_find_value)
    except Exception as e:
        web_find_result = e
    web_find_params.__setitem__('find_result', web_find_result)
    return params


def web_click(params):
    web_click_params = params['web']
    web_driver: WebDriver = web_click_params['driver']
    web_click_obj: WebElement = web_click_params['click_obj']
    del web_click_params['click_obj']
    web_driver.execute_script("arguments[0].click();", web_click_obj)
    # web_click_obj.click()
    return params


def web_input(params):
    web_input_params = params['web']
    web_input_obj: WebElement = web_input_params['input_obj']
    del web_input_params['input_obj']
    web_input_text = web_input_params['input_text']
    del web_input_params['input_text']
    web_input_obj.clear()
    web_input_obj.send_keys(web_input_text)
    return params


def web_find_by_xpath(params, xpath):
    params['web'].__setitem__('find_by', 'xpath')
    # noinspection SpellCheckingInspection
    params['web'].__setitem__('find_value', xpath)
    params = web_find(params=params)
    found = params['web']['find_result']
    del params['web']['find_result']
    return found


def web_find_by_id(params, id_):
    params['web'].__setitem__('find_by', 'id')
    # noinspection SpellCheckingInspection
    params['web'].__setitem__('find_value', id_)
    params = web_find(params=params)
    found = params['web']['find_result']
    del params['web']['find_result']
    return found


def web_input_compact(params, input_obj, input_text):
    params['web'].__setitem__('input_obj', input_obj)
    params['web'].__setitem__('input_text', input_text)
    params = web_input(params=params)
    return params


def web_click_compact(params, click_obj):
    params['web'].__setitem__('click_obj', click_obj)
    params = web_click(params=params)
    return params


def web_find_input(params):
    web_params = params['web']
    web_find_value = web_params['find_value']
    del web_params['find_value']
    web_input_text = web_params['input_text']
    del web_params['input_text']
    try:
        found = web_find_by_xpath(params=params, xpath=web_find_value)
        if type(found) is not NoSuchElementException:
            params = web_input_compact(
                params=params, input_obj=found, input_text=web_input_text)
        else:
            raise found
        web_params['exception'] = None
    except Exception as e:
        web_params['exception'] = e
    return params


def web_find_click(params):
    web_params = params['web']
    web_find_value = web_params['find_value']
    del web_params['find_value']
    try:
        found = web_find_by_xpath(params=params, xpath=web_find_value)
        if type(found) is not NoSuchElementException:
            params = web_click_compact(params=params, click_obj=found)
        else:
            raise found
        web_params['exception'] = None
    except Exception as e:
        web_params['exception'] = e
    return params


if __name__ == '__main__':
    params_ = web_start(params={})
    params_['web'].__setitem__('goto_url', 'http://ci.cloud.ruijie.net/')
    params_ = web_goto(params=params_)
    wd: WebDriver = params_['web']['driver']
    while True:
        time.sleep(1)
