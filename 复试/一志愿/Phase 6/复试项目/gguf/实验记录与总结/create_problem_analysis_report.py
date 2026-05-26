# -*- coding: utf-8 -*-
"""
生成问题分析报告 Word 文档
nanoGPT 转 GGUF 后模型停不下来的原因分析
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
import os

def create_problem_analysis_report():
    doc = Document()
    
    # 设置文档标题
    title = doc.add_heading('nanoGPT 转 GGUF 模型停不下来问题分析', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加元信息
    doc.add_paragraph()
    meta = doc.add_paragraph()
    meta.add_run('分析时间：').bold = True
    meta.add_run('2026-05-26')
    meta.add_run('\n分析目标：').bold = True
    meta.add_run('解释 nanoGPT 转 GGUF 后模型无法自动停止的原因')
    meta.add_run('\n分析结论：').bold = True
    meta.add_run('模型训练流程设计导致模型未学习 EOS token，无法主动停止')
    
    doc.add_paragraph()
    
    # ==================== 一、问题现象 ====================
    doc.add_heading('一、问题现象', level=1)
    
    doc.add_paragraph('在 LM Studio 中加载 GGUF 模型后，生成文本时模型无法自动停止，持续输出直到达到最大 token 限制或内存耗尽。')
    
    doc.add_paragraph()
    
    # ==================== 二、根本原因 ====================
    doc.add_heading('二、根本原因分析', level=1)
    
    doc.add_heading('2.1 训练数据编码方式', level=2)
    
    doc.add_paragraph('查看 nanoGPT 的数据准备代码 `data/shakespeare/prepare.py`（第 19-22 行）：')
    code1 = doc.add_paragraph()
    code1.add_run('enc = tiktoken.get_encoding("gpt2")').italic = True
    doc.add_paragraph('train_ids = enc.encode_ordinary(train_data)  # ← 关键！')
    doc.add_paragraph('val_ids = enc.encode_ordinary(val_data)')
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('tiktoken 的两种编码方法：').bold = True
    
    # 创建表格
    table1 = doc.add_table(rows=3, cols=3)
    table1.style = 'Table Grid'
    
    # 表头
    header_cells = table1.rows[0].cells
    header_cells[0].text = '方法'
    header_cells[1].text = '行为'
    header_cells[2].text = '是否添加 EOS'
    for cell in header_cells:
        cell.paragraphs[0].runs[0].bold = True
    
    # 数据
    data1 = [
        ('encode_ordinary(text)', '只编码文本内容', '❌ 不添加'),
        ('encode(text, allowed_special={"<|endoftext|>"})', '包含特殊 token', '✅ 可以添加')
    ]
    
    for i, (method, behavior, eos) in enumerate(data1, 1):
        row_cells = table1.rows[i].cells
        row_cells[0].text = method
        row_cells[1].text = behavior
        row_cells[2].text = eos
    
    doc.add_paragraph()
    
    doc.add_heading('2.2 训练数据统计', level=2)
    
    doc.add_paragraph('Shakespeare 数据集的换行符统计：')
    
    # 创建表格
    table2 = doc.add_table(rows=4, cols=2)
    table2.style = 'Table Grid'
    
    # 表头
    header_cells2 = table2.rows[0].cells
    header_cells2[0].text = '类型'
    header_cells2[1].text = '数量'
    for cell in header_cells2:
        cell.paragraphs[0].runs[0].bold = True
    
    # 数据
    data2 = [
        ('总字符数', '1,115,394'),
        ('换行符总数', '40,000'),
        ('单换行符（同行内换行）', '32,779')
    ]
    
    for i, (type_name, count) in enumerate(data2, 1):
        row_cells = table2.rows[i].cells
        row_cells[0].text = type_name
        row_cells[1].text = count
    
    doc.add_paragraph()
    
    doc.add_heading('2.3 模型学到的内容', level=2)
    
    model_learned = [
        ('✅ Token 198', '"\\n" - 单换行符，表示同行内换行'),
        ('✅ Token 198 连续模式', '"\\n\\n" - 双换行符，表示段落分隔/对话切换'),
        ('❌ Token 50256', '"<|endoftext|>" - 模型从未见过，从未学习')
    ]
    
    for token, desc in model_learned:
        p = doc.add_paragraph()
        p.add_run(token).bold = True
        p.add_run(' ' + desc)
    
    doc.add_paragraph()
    
    # ==================== 三、技术细节 ====================
    doc.add_heading('三、技术细节：模型 generate 方法分析', level=1)
    
    doc.add_paragraph('查看 nanoGPT 的 `model.py` 第 306-330 行的 generate 方法：')
    
    doc.add_paragraph('def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):', style='Quote')
    doc.add_paragraph('    for _ in range(max_new_tokens):  # ← 硬循环 max_new_tokens 次！', style='Quote')
    doc.add_paragraph('        # ... 生成逻辑 ...', style='Quote')
    doc.add_paragraph('        idx = torch.cat((idx, idx_next), dim=1)', style='Quote')
    doc.add_paragraph('    return idx', style='Quote')
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('关键发现：').bold = True
    doc.add_paragraph('• ❌ 没有 EOS token 检测逻辑', style='List Bullet')
    doc.add_paragraph('• ❌ 没有检查 idx_next == 50256（EOS token ID）', style='List Bullet')
    doc.add_paragraph('• ✅ 完全依赖 max_new_tokens 硬截断', style='List Bullet')
    
    doc.add_paragraph()
    
    # ==================== 四、为什么停不下来 ====================
    doc.add_heading('四、为什么停不下来', level=1)
    
    reasons = [
        ('训练数据设计', 'nanoGPT 训练时使用 encode_ordinary()，训练数据中不包含 EOS token (50256)'),
        ('模型未学习', '模型从训练开始就从未见过 EOS token，因此无法理解其含义'),
        ('生成逻辑', '即使 tokenizer 正确识别了 EOS token，模型本身也不会主动生成它'),
        ('LLM 行为', 'LLM 会持续预测下一个 token，没有"停止"的概念，除非遇到 EOS 或达到上限')
    ]
    
    for i, (title, desc) in enumerate(reasons, 1):
        p = doc.add_paragraph()
        p.add_run(f'{i}. {title}：').bold = True
        p.add_run(desc)
    
    doc.add_paragraph()
    
    # ==================== 五、解决方案 ====================
    doc.add_heading('五、解决方案（不修改代码，仅说明）', level=1)
    
    doc.add_heading('方案一：在 LM Studio 中设置上限', level=2)
    solutions1 = [
        '在 LM Studio 的生成设置中，配置合理的 max_tokens 上限（如 200-500）',
        '设置 stop 序列为 "\n\n" 或空行模式',
        '这是最简单直接的解决方案，不需要重新训练模型'
    ]
    for sol in solutions1:
        doc.add_paragraph(sol, style='List Bullet')
    
    doc.add_paragraph()
    
    doc.add_heading('方案二：修改训练数据预处理', level=2)
    solutions2 = [
        '修改 data/shakespeare/prepare.py，在每个样本末尾添加 EOS token',
        '使用 enc.encode() 替代 enc.encode_ordinary()，并设置 allowed_special',
        '需要重新训练模型'
    ]
    for sol in solutions2:
        doc.add_paragraph(sol, style='List Bullet')
    
    doc.add_paragraph()
    
    doc.add_heading('方案三：修改模型生成逻辑', level=2)
    solutions3 = [
        '修改 model.py 的 generate() 方法，添加 EOS 检测',
        '在循环中检查 idx_next == 50256，遇到则 break',
        '需要重新训练模型'
    ]
    for sol in solutions3:
        doc.add_paragraph(sol, style='List Bullet')
    
    doc.add_paragraph()
    
    doc.add_heading('方案四：配置 LLMs 的停止序列', level=2)
    solutions4 = [
        '在 LM Studio 中，为模型配置自定义的停止序列',
        '例如将 "\n\n"（双换行）或特定模式设为停止信号',
        '虽然不是完美的 EOS，但可以利用模型学到的段落分隔模式'
    ]
    for sol in solutions4:
        doc.add_paragraph(sol, style='List Bullet')
    
    doc.add_paragraph()
    
    # ==================== 六、验证建议 ====================
    doc.add_heading('六、验证建议', level=1)
    
    verification = [
        '在 LM Studio 中生成文本时，观察是否正确输出换行符（\n）',
        '检查模型是否学会了对话格式（说话者切换时的双换行）',
        '测试不同的 max_tokens 设置，找到合理的上限',
        '尝试设置 stop 序列，看是否能改善停止行为'
    ]
    
    for ver in verification:
        doc.add_paragraph(ver, style='List Bullet')
    
    doc.add_paragraph()
    
    # ==================== 七、结论 ====================
    doc.add_heading('七、结论', level=1)
    
    conclusion = doc.add_paragraph()
    conclusion.add_run('问题的根源在于 ').bold = False
    conclusion.add_run('训练流程的设计').bold = True
    conclusion.add_run('：nanoGPT 故意在训练时不使用 EOS token，是为了简化训练流程，但这导致模型无法学习"停止"的概念。')
    
    doc.add_paragraph()
    doc.add_paragraph('这不是转换流程（nanoGPT → GGUF）的问题，而是模型训练阶段的设计选择。')
    
    doc.add_paragraph()
    doc.add_paragraph('最实用的解决方案是：')
    doc.add_paragraph('1. 在 LM Studio 中设置合理的 max_tokens 上限', style='List Number')
    doc.add_paragraph('2. 或配置自定义的 stop 序列（如双换行符）', style='List Number')
    
    doc.add_paragraph()
    doc.add_paragraph('如果需要模型能够正确响应 EOS token，必须重新训练模型，并在训练数据预处理阶段添加 EOS token。')
    
    doc.add_paragraph()
    
    # 保存文档
    output_path = os.path.join(os.path.dirname(__file__), '实验记录与总结', 'EOS停止问题分析报告.docx')
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc.save(output_path)
    print(f'✅ 文档已保存到：{output_path}')
    return output_path

if __name__ == '__main__':
    create_problem_analysis_report()
