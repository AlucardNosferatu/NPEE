import json
import os


def create_empty_json_files_safe():
    x = input("请输入年份: ").strip()
    if not x:
        print("错误：输入不能为空！")
        return
    y = input("请输入科目: ").strip()
    if not y:
        print("错误：输入不能为空！")
        return
    z = input("请输入最大题号: ").strip()
    if not z:
        print("错误：输入不能为空！")
        return
    created_count = 0
    for i in range(1, int(z) + 1):
        filename = f"{x}-{y}-{i}.json"

        # 检查文件是否已存在
        if os.path.exists(filename):
            print(f"警告：文件 {filename} 已存在，跳过...")
            continue

        # 创建空JSON文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)

        created_count += 1
        print(f"已创建: {filename}")

    print(f"\n完成！成功创建 {created_count} 个文件，跳过了 {int(z) - created_count} 个已存在的文件。")


if __name__ == "__main__":
    create_empty_json_files_safe()
