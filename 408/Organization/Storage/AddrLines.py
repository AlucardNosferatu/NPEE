import random


def generate_storage_question():
    # 编址单位配置
    units = [
        {"name": "字节", "size": 1},
        {"name": "半字（2字节）", "size": 2},
        {"name": "字（4字节）", "size": 4},
        {"name": "双字（8字节）", "size": 8}
    ]
    chip_type = random.choice(['DRAM', 'SRAM'])
    unit = random.choice(units)

    address_lines = random.randint(1, 37) // 2 * 2
    # 计算理论容量（字节）
    capacity_bytes = (2 ** address_lines) * unit["size"]

    if chip_type == 'DRAM':
        address_lines_show = address_lines // 2
    elif chip_type == 'SRAM':
        address_lines_show = address_lines
    else:
        raise ValueError('芯片类型错误！')
    question_type = random.choice(["capacity", "address_lines"])

    # 转换为显示单位
    if capacity_bytes >= (1024 ** 3):
        display_unit = 'GB'
        display_cap = f"{capacity_bytes // (1024 ** 3)} {display_unit}"
    elif capacity_bytes >= (1024 ** 2):
        display_unit = 'MB'
        display_cap = f"{capacity_bytes // (1024 ** 2)} {display_unit}"
    elif capacity_bytes >= 1024:
        display_unit = 'KB'
        display_cap = f"{capacity_bytes // 1024} {display_unit}"
    else:
        display_unit = 'B'
        display_cap = f"{capacity_bytes} {display_unit}"

    if question_type == "capacity":
        question = f"某{chip_type}芯片有{address_lines_show}根地址引脚，按{unit['name']}编址，最大存储容量是多少？请用{display_unit}表示。"
        answer = display_cap
    else:
        question = f"某{chip_type}存储芯片容量为{display_cap}，按{unit['name']}编址，需要多少个地址引脚？"
        answer = f"{address_lines_show}根"
    return question, answer


if __name__ == '__main__':
    q, a = generate_storage_question()
    print(f"题目: {q}")
    print(f"答案: {a}\n")
