import openpyxl

from FunctionSampler.ExcelCFG import default_load_file_path, default_save_file_path
from FunctionSampler.ExcelComboParser import combo2_read, combo3_read, combo2_write, combo3_write
from FunctionSampler.ExcelOpParser import op1_read, op2_read, op1_write, op2_write


class ExcelAPI:
    workbook = None
    load_file_path = None
    save_file_path = None

    def __init__(self, file_path=default_load_file_path):
        self.load_file_path = file_path
        self.workbook = openpyxl.load_workbook(filename=self.load_file_path)

    def read(self, category, variation_code, pair_code=None, op_index=None, prop_index=None):
        if category == 'combo2':
            assert pair_code is not None
            return combo2_read(pair_code=pair_code, variation_code=variation_code, workbook=self.workbook)
        elif category == 'combo3':
            assert pair_code is not None
            return combo3_read(pair_code=pair_code, variation_code=variation_code, workbook=self.workbook)
        elif category == 'op1':
            assert op_index is not None
            assert prop_index is not None
            return op1_read(op_index=2, variation_code=variation_code, prop_index=prop_index, workbook=self.workbook)
        elif category == 'op2':
            assert op_index is not None
            assert prop_index is not None
            return op2_read(op_index=2, variation_code=variation_code, prop_index=prop_index, workbook=self.workbook)
        else:
            raise ValueError('不正确的类别：{}'.format(category))

    def write(self, new_value, category, variation_code, pair_code=None, op_index=None, prop_index=None):
        if category == 'combo2':
            assert pair_code is not None
            return combo2_write(new_value=new_value, pair_code=pair_code, variation_code=variation_code,
                                workbook=self.workbook)
        elif category == 'combo3':
            assert pair_code is not None
            return combo3_write(new_value=new_value, pair_code=pair_code, variation_code=variation_code,
                                workbook=self.workbook)
        elif category == 'op1':
            assert op_index is not None
            assert prop_index is not None
            return op1_write(new_value=new_value, op_index=2, variation_code=variation_code, prop_index=prop_index,
                             workbook=self.workbook)
        elif category == 'op2':
            assert op_index is not None
            assert prop_index is not None
            return op2_write(new_value=new_value, op_index=2, variation_code=variation_code, prop_index=prop_index,
                             workbook=self.workbook)
        else:
            raise ValueError('不正确的类别：{}'.format(category))

    def save(self):
        if self.save_file_path is not None:
            self.workbook.save(self.save_file_path)
        else:
            raise NameError('还没设置保存路径！')

    def set_save_filepath(self, filepath=default_save_file_path):
        if filepath == self.load_file_path:
            raise ValueError('不允许设置与读取路径相同的保存路径！')
        self.save_file_path = filepath
        print('保存路径设置为：{}'.format(self.save_file_path))
