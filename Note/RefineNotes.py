import glob
import os
import pickle

from CropNotes import copy_sheets_simple
from DatesAnalyzer import IncrementalDateAnalyzer

if __name__ == '__main__':
    # 准备真题问题列表
    pkl_files = glob.glob(os.path.join('日期', "**", "*.pkl"), recursive=True)
    # 假设这是您已有的RAG结果
    analyzer = IncrementalDateAnalyzer(top_k=250, memory_limit=250)
    for pkl_file in pkl_files:
        with open(pkl_file, "rb") as f:
            # 3. 调用dump，把字典写入文件
            rag_result = pickle.load(f)
            analyzer.update(rag_result)
    top_k = analyzer.get_top_dates_df(top_n=20)['日期'].to_list()
    copy_sheets_simple(
        "C:\\Users\\16413\\Desktop\\NPEE\\统计\\WWII\\工作日志.xlsx",
        "工作摘要.xlsx",
        top_k
    )
