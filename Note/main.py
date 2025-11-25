import json

import openpyxl
from openpyxl.utils import get_column_letter


def replace_in_excel(input_file, output_file="输出.xlsx", replace_configs=None):
    """
    在Excel中根据配置替换内容，输出到新文件，支持自动搜索定位

    参数:
        input_file: 输入Excel文件路径
        output_file: 输出Excel文件路径，默认"输出.xlsx"
        replace_configs: 替换配置列表，每个配置为字典，格式:
                        {"cell": "A1", "old": "原内容", "new": "新内容"}
    """
    if replace_configs is None:
        with open('测试.json', 'r', encoding='utf-8') as f:
            replace_configs = json.load(f)

    # 加载工作簿
    wb = openpyxl.load_workbook(input_file)
    # 处理第一个工作表（可根据需要修改为指定工作表）
    sheet = wb.active

    for config in replace_configs:
        cell_pos = config["cell"]
        old_val = config["old"]
        new_val = config["new"]

        # 1. 尝试获取配置指定的单元格内容
        target_cell = None
        try:
            target_cell = sheet[cell_pos]
            current_val = target_cell.value
        except Exception as e:
            print(repr(e))
            # print(f"警告：单元格 {cell_pos} 不存在，将直接搜索定位")
            current_val = None

        # 2. 检查当前单元格内容是否与old_val一致
        # 处理空值情况：单元格为空且old_val不为空，则判定为不一致
        if current_val != old_val:
            print(f"单元格 {cell_pos} 内容与目标不符，开始搜索 {old_val}...")
            # 3. 遍历整个工作表搜索old_val
            found = False
            # 获取有效数据范围（避免全表遍历浪费资源）
            max_row = sheet.max_row
            max_col = sheet.max_column

            for row in range(1, max_row + 1):
                for col in range(1, max_col + 1):
                    col_letter = get_column_letter(col)
                    cell = sheet[f"{col_letter}{row}"]
                    if cell.value == old_val:
                        # 找到匹配项，更新为新值
                        target_cell = cell
                        target_cell.value = new_val
                        print(f"已在 {col_letter}{row} 找到并替换")
                        found = True
                        break  # 找到第一个匹配项即停止（如需替换全部可删除此句）
                if found:
                    break

            if not found:
                print(f"警告：未找到内容 {old_val}，跳过替换")
                continue
        else:
            # 内容一致，直接替换
            target_cell.value = new_val
            print(f"已在 {cell_pos} 完成替换")

    # 保存到新文件（不覆盖原文件）
    wb.save(output_file)
    print(f"操作完成，结果已保存至 {output_file}")


# 使用示例
if __name__ == "__main__":
    # 输入文件路径
    input_excel = "测试.xlsx"
    # 输出文件路径（默认"输出.xlsx"，可自定义）
    output_excel = "输出.xlsx"
    # 执行替换
    replace_in_excel(input_excel, output_excel)
