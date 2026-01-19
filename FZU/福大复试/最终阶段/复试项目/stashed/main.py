from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Chrome 配置
options = Options()
options.add_argument('--headless=new')  # 推荐的新 headless 写法（更稳定）
# options.add_argument('--headless')        # 旧写法，大部分情况也还行
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

try:
    # 现代推荐写法（service + options 分开）
    driver = webdriver.Chrome(
        service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
        options=options
    )

    print("浏览器启动成功！")
    driver.get("https://x.com")
    time.sleep(3)

    print("页面标题:", driver.title)
    print("当前URL:", driver.current_url)
    print("测试通过 ✓")

except Exception as e:
    print("发生错误：")
    print(str(e))

finally:
    try:
        driver.quit()
    except:
        pass