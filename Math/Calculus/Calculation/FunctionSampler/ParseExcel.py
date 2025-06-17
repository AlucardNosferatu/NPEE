import re

import openpyxl

properties = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']


def process_excel_file(file_path):
    # 打开工作簿
    workbook = openpyxl.load_workbook(file_path)

    # 获取指定工作表
    sheet = workbook['20250619']

    # 创建结果字典
    result_dict = {}

    # 处理D5到D45，步长为5
    operations = {}
    for i in range(5, 50, 5):
        # 获取D列单元格的值
        d_cell = sheet[f'D{i}']
        d_value = d_cell.value if d_cell.value else ''

        # 提取直到第一个左括号(全角)之前的文本作为key
        match = re.search(r'[^（]*', d_value)
        key = match.group(0).strip() if match else d_value.strip()
        operations[key] = d_value
        # 提取E列对应的值
        values = []
        for j in range(1, 5):
            e_cell = sheet[f'E{i + j}']
            if e_cell.value is not None:
                examples = e_cell.value.split('：###')[1].split('###-')
                examples = [example.strip('#') for example in examples]
                values.append(examples)

        # 添加到结果字典
        if key:
            result_dict[key] = values

    # 关闭工作簿
    workbook.close()
    for key in operations.keys():
        op_desc = '运算类型：' + operations[key]
        print(op_desc)
        combo = [
            ['不满足', '不满足'],
            ['不满足', '满足'],
            ['满足', '不满足'],
            ['满足', '满足']
        ]
        examples = result_dict[key]
        for j in range(13):
            property = '性质' + properties[j]
            print('===' + property + '讨论===')
            for i in range(4):
                condition = property + '情形' + str(i) + '：f(x)' + combo[i][0] + property + '，' + 'g(x)' + combo[i][
                    1] + property
                print(condition)
                print('>>> ' + examples[i][j])
        print('')
        print('')
        print('')
    return result_dict


if __name__ == "__main__":
    # 请替换为实际的文件路径
    file_path = r'C:\Users\16413\Desktop\NPEE\统计\WWII\工作日志.xlsx'
    data = process_excel_file(file_path)

    # 打印结果
    for key, values in data.items():
        print(f"{key}: {values}")
