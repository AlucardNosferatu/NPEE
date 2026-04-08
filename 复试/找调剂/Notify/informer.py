import hashlib
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ===================== 固定配置 =====================
# 你提供的精准 XPath！直接用！
MONITOR_XPATH = "/html/body/div[2]/div[3]/div"

REFRESH_INTERVAL = 300  # 15秒刷新一次
# =====================================================

# 启动浏览器
driver = webdriver.Chrome()
driver.get("https://yz.chsi.com.cn/")

print("=" * 60)
print("👉 操作步骤：")
print("1. 手动登录研招网")
print("2. 进入调剂系统 -> 志愿管理页面")
print("3. 停留在通知页面，输入 start 启动监控")
print("=" * 60)

# 等待启动指令
while True:
    if input("输入 start 开始监控：").strip().lower() == "start":
        break

print("\n✅ 监控启动！强制刷新 + 精准监控目标区域")


# 获取指定区域的哈希值
def get_target_hash():
    try:
        # 自动切换到【最新打开的标签页】
        driver.switch_to.window(driver.window_handles[-1])
        # 等待元素加载（最多5秒）
        wait = WebDriverWait(driver, 5)
        target_elem = wait.until(EC.presence_of_element_located((By.XPATH, MONITOR_XPATH)))
        # 只对这个区域的内容计算哈希
        content = target_elem.text.strip()
        return hashlib.md5(content.encode("utf-8")).hexdigest()
    except Exception as e:
        print(f"⚠️  监控异常：{str(e)}")
        return None


# 初始基准值
old_hash = get_target_hash()

# 主循环
try:
    while True:
        # 切最新Tab
        driver.switch_to.window(driver.window_handles[-1])
        # ✅ 核心修复：用JS强制无缓存刷新（driver.refresh()失效的终极解决方案）
        driver.execute_script("location.reload(true);")
        time.sleep(3)  # 等待页面加载

        # 获取新内容
        new_hash = get_target_hash()

        # 内容变化 = 报警！
        if new_hash and old_hash and new_hash != old_hash:
            print("\n" + "=" * 70)
            print("🔥🔥🔥  目标区域已变化！收到复试通知了！！！")
            print("=" * 70)
            # Windows 蜂鸣警报（响1.5秒）
            try:
                import winsound

                winsound.Beep(2800, 1500)
            except:
                pass
        old_hash = new_hash
        # 日志输出
        current_time = time.strftime("%H:%M:%S")
        print(f"[{current_time}] 已强制刷新 | 监控正常")
        time.sleep(REFRESH_INTERVAL)

except KeyboardInterrupt:
    print("\n🛑 监控已停止")
finally:
    driver.quit()
