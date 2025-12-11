from SearchNote import load_json_files, batch_process_questions, progress_callback_
from StatAnalyzer import IncrementalDateAnalyzer

if __name__ == '__main__':
    # 准备真题问题列表
    q_list = load_json_files("真题")
    while len(q_list) > 2:
        q_list.pop()
    # 执行批量处理
    b_res = batch_process_questions(
        questions_list=q_list,
        max_queries_per_keyword=1,
        progress_callback=progress_callback_,
        return_objects=True
    )
    # 假设这是您已有的RAG结果
    rag_results = b_res['questions_results']  # 包含700个元素的大列表
    analyzer = IncrementalDateAnalyzer()
    for rag_item in rag_results:
        analyzer.update(rag_item)
