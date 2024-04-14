import json
import random
import re

import openpyxl


def remove_digits(text):
    return re.sub(r'\d+', '', text)


def remove_letters(text):
    pattern = "[a-zA-Z]"
    return re.sub(pattern, "", text)


def get_worksheet(sheet_name=None):
    note_path = r'C:\Users\16413\Desktop\NPEE\统计\WWII\工作日志.xlsx'
    workbook: openpyxl.Workbook = openpyxl.load_workbook(filename=note_path)
    if sheet_name is None:
        worksheets = workbook.worksheets
        worksheet: openpyxl.Worksheet = random.choice(worksheets)
    else:
        worksheet: openpyxl.Worksheet = workbook.get_sheet_by_name(name=sheet_name)
    return worksheet


def read_worksheet(worksheet):
    dim = worksheet.dimensions.split(':')
    dim[0] = 'B2'
    dim = [[remove_digits(d), remove_letters(d)] for d in dim]
    all_layers_hierarchy = {}
    for i in range(ord(dim[0][0]), ord(dim[1][0])):
        col = chr(i)
        for j in range(int(dim[0][1]), int(dim[1][1])):
            index = '{}{}'.format(col, j)
            val = worksheet[index].value
            if val is not None:
                if col not in all_layers_hierarchy.keys():
                    all_layers_hierarchy[col] = {}
                all_layers_hierarchy[col][j] = [val, {}]
    return all_layers_hierarchy


def parse2dict(all_layers_hierarchy):
    for col in all_layers_hierarchy.keys():
        if col != 'B':
            current_layer = all_layers_hierarchy[col]
            upper_layer = all_layers_hierarchy[chr(ord(col) - 1)]
            current_layer_keys = list(current_layer.keys())
            current_layer_keys.sort()
            upper_layer_keys = list(upper_layer.keys())
            upper_layer_keys.sort()
            for key in current_layer_keys:
                upper_key = key
                while upper_key not in upper_layer_keys:
                    upper_key -= 1
                upper_layer[upper_key][1][key] = current_layer[key]
    json_str = json.dumps(all_layers_hierarchy['B'])
    return all_layers_hierarchy['B'], json_str


if __name__ == '__main__':
    worksheet_ = get_worksheet()
    all_layers_hierarchy_ = read_worksheet(worksheet_)
    all_layers_hierarchy_, json_str_ = parse2dict(all_layers_hierarchy_)
    print('Done')
