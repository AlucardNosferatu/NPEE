import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------- 核心配置 ----------------------
TARGET_URL = "https://yz.chsi.com.cn/kyzx/tjxx/"  # 研招网调剂信息页
LIST_XPATH = '/html/body/div[1]/div[2]/div[2]/div[1]/ul'  # 你找到的列表XPath
CHECK_INTERVAL = 10 * 60  # 刷新间隔：10分钟（可改，比如5分钟就是5*60）
# CHECK_INTERVAL = 1  # 测试用1秒，正式用改回10*60


# ------------------------------------------------------

def init_browser():
    """初始化Chrome浏览器（自动适配驱动，不用手动配）"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    return driver


def get_notice_list(driver):
    """抓取当前页面的所有调剂公告（标题+时间）- 已修正定位逻辑"""
    # 显式等待：等列表加载完成（最多等15秒，防止页面加载慢）
    wait = WebDriverWait(driver, 15)
    notice_ul = wait.until(EC.presence_of_element_located((By.XPATH, LIST_XPATH)))

    # 抓取所有公告条目（ul下的所有li）
    notice_items = notice_ul.find_elements(By.XPATH, './/li')  # 相对路径，只找ul下的li
    notice_dict = {}  # 用字典存：标题 → 时间，方便后续对比

    for item in notice_items:
        try:
            # ---------------------- 修正1：标题定位（核心） ----------------------
            # 原逻辑：.//div[1]/a[2] → 只适配第一条，其他报错
            # 新逻辑：取div.title里最后一个a标签，所有公告都适配
            title = item.find_element(By.XPATH, './/div[@class="title"]/a[last()]').text.strip()

            # ---------------------- 修正2：时间定位（核心） ----------------------
            # 原逻辑：找span[@class='time'] → 页面里实际是div[@class='time']
            # 新逻辑：精准定位时间div，且简化提取
            time_elem = item.find_element(By.XPATH, './/div[@class="time"]')
            publish_time = time_elem.text.strip() if time_elem else "未知时间"

            if title:  # 过滤空标题
                notice_dict[title] = publish_time
        except Exception as e:
            # 个别条目结构异常时跳过，打印异常方便排查（可选）
            print(f"⚠️  单条公告抓取失败：{str(e)[:50]}")
            continue

    return notice_dict


if __name__ == "__main__":
    # 初始化浏览器并打开页面
    driver_ = init_browser()
    driver_.get(TARGET_URL)
    print("✅ 已打开研招网调剂页面，开始首次抓取...")

    # 首次抓取，作为基准
    last_notices = get_notice_list(driver_)
    print(f"📌 首次抓取到 {len(last_notices)} 条调剂公告：")
    for title_, time_ in last_notices.items():
        print(f"  {time_} - {title_}")

    # 循环刷新监控（按间隔刷新，对比变化）
    try:
        while True:
            print(f"\n⏳ 等待 {CHECK_INTERVAL // 60 if CHECK_INTERVAL >= 60 else CHECK_INTERVAL} 秒后刷新...")
            time.sleep(CHECK_INTERVAL)

            # 刷新页面
            driver_.refresh()
            print("🔄 页面已刷新，开始抓取新信息...")

            # 抓取最新公告
            current_notices = get_notice_list(driver_)

            # 对比：找新增的公告
            new_notices = {k: v for k, v in current_notices.items() if k not in last_notices}
            if new_notices:
                # 有新增！打印提醒（后续可加声音/弹窗提醒）
                print("\n🚨 发现新增调剂公告！！！")
                for title_, time_ in new_notices.items():
                    print(f"  🆕 {time_} - {title_}")
                # 更新基准数据
                last_notices = current_notices
            else:
                print("📝 暂无新增调剂公告")
    except KeyboardInterrupt:
        # 按Ctrl+C停止脚本
        print("\n🛑 手动停止监控")
    finally:
        # 关闭浏览器
        driver_.quit()
        print("👋 浏览器已关闭，监控结束")
