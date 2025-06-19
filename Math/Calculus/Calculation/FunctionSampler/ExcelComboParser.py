from FunctionSampler.ExcelCFG import props13_short, combo2_sheet_name, combo2_col_range, combo2_row_map, \
    combo3_sheet_name, combo3_col_range, combo3_row_map


def combo_init(sheet_name, combo_col_range, workbook):
    combo_sheet = workbook[sheet_name]
    combo_props_pairs = [
        combo_sheet[col + '1'].value if combo_sheet[col + '1'].value else '' for col in combo_col_range
    ]
    combo_props_pairs = [
        [
            props13_short.index(prop_short) for prop_short in pair.split('+')
        ] for pair in combo_props_pairs
    ]
    combo_props_pairs_code = [
        '+'.join([str(code) for code in pair]) for pair in combo_props_pairs
    ]
    combo_col_map = {}
    for i in range(len(combo_props_pairs_code)):
        pair_code = combo_props_pairs_code[i]
        pair_col = combo_col_range[i]
        combo_col_map[pair_code] = pair_col
    return combo_sheet, combo_col_map


def combo2_index_conv(pair_code, variation_code, combo2_col_map):
    set2std_code = {}
    for key in combo2_col_map.keys():
        key_sort = key.split('+').copy()
        key_sort.sort()
        key_sort = '+'.join(key_sort)
        set2std_code[key_sort] = key
    pair_code_sort = pair_code.split('+').copy()
    pair_code_sort.sort()
    pair_code_sort = '+'.join(pair_code_sort)
    if pair_code_sort in set2std_code.keys():
        key = set2std_code[pair_code_sort]
        if key == pair_code:
            return pair_code, variation_code
        else:
            variation_code = list(variation_code)
            variation_code[0], variation_code[1] = variation_code[1], variation_code[0]
            variation_code = ''.join(variation_code)
            return key, variation_code
    else:
        return None, None


def combo3_index_conv(pair_code, variation_code, combo3_col_map):
    set2std_code = {}
    for key in combo3_col_map.keys():
        key_sort = key.split('+').copy()
        key_sort.sort()
        key_sort = '+'.join(key_sort)
        set2std_code[key_sort] = key
    pair_code_sort = pair_code.split('+').copy()
    variation_code_sort = list(variation_code).copy()
    combined = sorted(zip(pair_code_sort, variation_code_sort), key=lambda x: x[0])
    pair_code_sort = [item[0] for item in combined]
    variation_code_sort = [item[1] for item in combined]
    pair_code_sort = '+'.join(pair_code_sort)
    variation_code_sort = ''.join(variation_code_sort)
    if pair_code_sort in set2std_code.keys():
        return pair_code_sort, variation_code_sort
    else:
        return None, None


def combo2_read(pair_code, variation_code, workbook):
    combo2_sheet, combo2_col_map = combo_init(
        sheet_name=combo2_sheet_name, combo_col_range=combo2_col_range, workbook=workbook
    )
    pair_code, variation_code = combo2_index_conv(pair_code, variation_code, combo2_col_map)
    if pair_code is None or variation_code is None:
        return None
    else:
        col = combo2_col_map[pair_code]
        row = combo2_row_map[variation_code]
        return combo2_sheet[col + str(row)].value


def combo3_read(pair_code, variation_code, workbook):
    combo3_sheet, combo3_col_map = combo_init(
        sheet_name=combo3_sheet_name, combo_col_range=combo3_col_range, workbook=workbook
    )
    pair_code, variation_code = combo3_index_conv(pair_code, variation_code, combo3_col_map)
    if pair_code is None or variation_code is None:
        return None
    else:
        col = combo3_col_map[pair_code]
        row = combo3_row_map[variation_code]
        return combo3_sheet[col + str(row)].value


def combo2_write(new_value, pair_code, variation_code, workbook):
    combo2_sheet, combo2_col_map = combo_init(
        sheet_name=combo2_sheet_name, combo_col_range=combo2_col_range, workbook=workbook
    )
    pair_code, variation_code = combo2_index_conv(pair_code, variation_code, combo2_col_map)
    if pair_code is None or variation_code is None:
        return None
    else:
        col = combo2_col_map[pair_code]
        row = combo2_row_map[variation_code]
        combo2_sheet[col + str(row)] = new_value
        return combo2_sheet[col + str(row)].value


def combo3_write(new_value, pair_code, variation_code, workbook):
    combo3_sheet, combo3_col_map = combo_init(
        sheet_name=combo3_sheet_name, combo_col_range=combo3_col_range, workbook=workbook
    )
    pair_code, variation_code = combo3_index_conv(pair_code, variation_code, combo3_col_map)
    if pair_code is None or variation_code is None:
        return None
    else:
        col = combo3_col_map[pair_code]
        row = combo3_row_map[variation_code]
        combo3_sheet[col + str(row)] = new_value
        return combo3_sheet[col + str(row)].value
