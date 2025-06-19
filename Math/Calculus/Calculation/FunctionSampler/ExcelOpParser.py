from FunctionSampler.ExcelCFG import op2_row_index, op1_variation_code, op2_variation_code, op1_sheet_name, \
    op2_sheet_name


def num2col(num):
    return '' if num == 0 else num2col((num - 1) // 26) + chr((num - 1) % 26 + ord('A'))


def prop2num(prop_index):
    return prop_index * 2 + 3


def op_get_col(prop_index):
    col_num = prop2num(prop_index)
    return num2col(col_num)


def op1op2row(op_index):
    return op_index * 5 + 2


def op2op2row(op_index):
    return op2_row_index[op_index]


def op1_get_row(op_index, variation_code):
    offset = op1_variation_code.index(variation_code)
    return offset + op1op2row(op_index=op_index)


def op2_get_row(op_index, variation_code):
    offset = op2_variation_code.index(variation_code)
    return offset + op2op2row(op_index=op_index)


def op1_read(op_index, variation_code, prop_index, workbook):
    col = op_get_col(prop_index)
    row = op1_get_row(op_index=op_index, variation_code=variation_code)
    op1_sheet = workbook[op1_sheet_name]
    return op1_sheet[col + str(row)].value


def op2_read(op_index, variation_code, prop_index, workbook):
    col = op_get_col(prop_index)
    row = op2_get_row(op_index=op_index, variation_code=variation_code)
    op2_sheet = workbook[op2_sheet_name]
    return op2_sheet[col + str(row)].value


def op1_write(new_value, op_index, variation_code, prop_index, workbook):
    col = op_get_col(prop_index)
    row = op1_get_row(op_index=op_index, variation_code=variation_code)
    op1_sheet = workbook[op1_sheet_name]
    op1_sheet[col + str(row)] = new_value
    return op1_sheet[col + str(row)].value


def op2_write(new_value, op_index, variation_code, prop_index, workbook):
    col = op_get_col(prop_index)
    row = op2_get_row(op_index=op_index, variation_code=variation_code)
    op2_sheet = workbook[op2_sheet_name]
    op2_sheet[col + str(row)] = new_value
    return op2_sheet[col + str(row)].value
