import json
import os
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
        sheet_names = workbook.sheetnames
        sheet_names.sort()
        if os.path.exists('NoteReview.txt'):
            with open(file='NoteReview.txt', mode='r', encoding='utf-8') as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
            never = list(set(sheet_names).difference(set(lines)))
            if len(never) > 0:
                never.sort()
                sheet_name = never[0]
            else:
                # LRU Algorithm
                last_review = {}
                lines.reverse()
                for sn in lines:
                    last_review[sn] = lines.index(sn)
                lrr = 0
                sheet_name = lines[-1]
                for sn in last_review.keys():
                    if last_review[sn] >= lrr:
                        lrr = last_review[sn]
                        sheet_name = sn
        else:
            sheet_name = random.choice(sheet_names)
    worksheet: openpyxl.Worksheet = workbook[sheet_name]
    return worksheet, sheet_name


def read_worksheet(worksheet):
    dim = worksheet.dimensions.split(':')
    dim[0] = 'B2'
    dim = [[remove_digits(d), remove_letters(d)] for d in dim]
    all_layers_hierarchy = {}
    for i in range(ord(dim[0][0]), ord(dim[1][0]) + 1):
        col = chr(i)
        for j in range(int(dim[0][1]), int(dim[1][1]) + 1):
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
    top_layer = all_layers_hierarchy['B']
    top_layer_json_str = json.dumps(top_layer)
    return all_layers_hierarchy, top_layer, top_layer_json_str


def recursive_read(entry, lines=None):
    if lines is None:
        lines = []
    # entry = [val, {}]
    lines.append(entry[0])
    sub_entry_keys = list(entry[1].keys())
    sub_entry_keys.sort()
    for sub_entry_key in sub_entry_keys:
        sub_entry = entry[1][sub_entry_key]
        lines = recursive_read(entry=sub_entry, lines=lines)
    return lines


def replace_keywords_with_underscore(text):
    pattern = r'###(.*?)###'  # 匹配###之间的内容
    replaced_text = re.sub(pattern, lambda m: '__' * len(m.group(1)), text)
    return replaced_text


def extract_keywords(text):
    pattern = r'###(.*?)###'  # 匹配###之间的内容
    keywords = re.findall(pattern, text)
    return keywords


def parse_blanks(lines: list):
    lines_with_blanks = lines.copy()
    answers = []
    for i, line in enumerate(lines_with_blanks):
        line_with_blanks = replace_keywords_with_underscore(text=line)
        answers += extract_keywords(text=line)
        lines_with_blanks[i] = line_with_blanks
    return lines_with_blanks, lines, answers


def verify_input(answer, weight, index):
    my_answer = input('第{}个空:'.format(index))
    print('我的回答:{}'.format(my_answer))
    print('正确回答:{}'.format(answer))
    cmd = ''
    while cmd not in ['Y', 'N']:
        cmd = input('是否正确？[Y/N]:')
    score_delta = {'Y': weight, 'N': 0.0}[cmd]
    return score_delta


if __name__ == '__main__':

    weight_ = 0.5
    while True:
        score_total = 0
        # worksheet_ = get_worksheet(sheet_name='20240414')
        worksheet_, sheet_name_ = get_worksheet()
        all_layers_hierarchy_ = read_worksheet(worksheet_)
        _, top_layer_, top_layer_json_str_ = parse2dict(all_layers_hierarchy_)
        entry_ = top_layer_[random.choice(list(top_layer_.keys()))]
        lines_ = recursive_read(entry=entry_)
        lines_with_blanks_, lines_, answers_ = parse_blanks(lines=lines_)
        if len(answers_) > 0:
            lines_with_blanks_.insert(0, '=============题目=============')
            print('\n'.join(lines_with_blanks_))
            for index_, answer_ in enumerate(answers_):
                score_delta_ = verify_input(answer_, weight_, index_ + 1)
                score_total += score_delta_
                print('目前得分:{}'.format(score_total))
        with open(file='NoteReview.txt', mode='a', encoding='utf-8') as f:
            f.writelines([sheet_name_ + '\n'])
