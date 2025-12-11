"""
Excel批量转换为docx脚本（动态检测行数）
功能：将Excel每个sheet的内容转换为普通段落，每10个sheet合并到一个docx文件
动态检测每个sheet的实际非空行数
"""

import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
import re
import math
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ExcelToParagraphConverter:
    """Excel转段落式docx转换器（动态检测行数）"""

    def __init__(self, excel_path, output_dir="每10个sheet一组"):
        """
        初始化转换器

        Args:
            excel_path: Excel文件路径
            output_dir: 输出目录
        """
        self.excel_path = excel_path
        self.output_dir = output_dir

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

    def detect_actual_data_range(self, df):
        """
        动态检测DataFrame中的实际数据范围

        返回：(min_row, max_row, min_col, max_col)
        """
        if df.empty:
            return 0, 0, 0, 0

        # 找到非空单元格的行列索引
        non_empty_rows = []
        non_empty_cols = []

        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell = df.iat[i, j]
                if not pd.isna(cell) and str(cell).strip():
                    non_empty_rows.append(i)
                    non_empty_cols.append(j)

        if not non_empty_rows:
            return 0, 0, 0, 0

        min_row = min(non_empty_rows)
        max_row = max(non_empty_rows)
        min_col = min(non_empty_cols)
        max_col = max(non_empty_cols)

        # 扩展范围，确保包含相邻可能相关的行
        # 如果数据量很大，适当扩展
        if max_row - min_row > 100:
            # 对于大数据集，只扩展几行
            min_row = max(0, min_row - 3)
            max_row = min(len(df) - 1, max_row + 3)
        else:
            # 对于小数据集，适当扩展更多
            min_row = max(0, min_row - 5)
            max_row = min(len(df) - 1, max_row + 5)

        return min_row, max_row, min_col, max_col

    def clean_text(self, text):
        """清理文本，移除多余空格和换行"""
        if pd.isna(text):
            return ""

        text = str(text)
        # 移除多余空格和换行，但保留必要的空格
        text = re.sub(r'\s+', ' ', text).strip()
        # 移除表格标记等特殊字符，但保留中文、英文、数字、常用标点
        text = re.sub(r'[^\u4e00-\u9fff\w\s,.?!;:，。？！；：()\-\[\]【】「」《》""'']', '', text)
        return text

    def is_meaningful_cell(self, cell_value):
        """判断单元格是否有意义（非空且有一定长度）"""
        if pd.isna(cell_value):
            return False

        text = str(cell_value).strip()
        # 过滤太短的纯符号或数字
        if len(text) < 2:
            return False

        # 过滤纯公式（如 =SUM(...)）
        if text.startswith('=') and len(text) > 10:
            return False

        # 检查是否包含有意义的内容
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        has_meaningful_text = bool(re.search(r'[a-zA-Z]{3,}|\d+\.\s', text))

        return has_chinese or has_meaningful_text or len(text) > 10

    def extract_meaningful_content(self, df):
        """
        从DataFrame中提取有意义的内容

        策略：
        1. 动态检测数据范围
        2. 优先提取包含###的填空内容
        3. 提取包含编号（如一、二、1.1等）的内容
        4. 提取非空且有意义的单元格内容
        """
        meaningful_lines = []

        # 1. 动态检测数据范围
        min_row, max_row, min_col, max_col = self.detect_actual_data_range(df)

        if min_row == max_row and min_col == max_col:
            return meaningful_lines

        print(f"  数据范围: 行 {min_row}-{max_row}, 列 {min_col}-{max_col}")

        # 2. 优先提取关键内容
        for i in range(min_row, max_row + 1):
            row_content = []
            for j in range(min_col, max_col + 1):
                try:
                    cell = df.iat[i, j]
                    if self.is_meaningful_cell(cell):
                        text = self.clean_text(cell)
                        if text:
                            row_content.append(text)
                except:
                    continue

            # 如果有内容，合并这一行
            if row_content:
                # 尝试智能合并：如果第一列是标题或编号，后面的内容接在冒号后
                if len(row_content) > 1:
                    first_item = row_content[0]
                    # 检查第一项是否是编号或标题
                    if (re.match(r'^[一二三四五六七八九十]、', first_item) or
                        re.match(r'^\d+[\.、]', first_item) or
                        re.match(r'^[A-Za-z]\.[\s]', first_item) or
                        len(first_item) < 20):  # 可能是标题

                        # 标题和内容用冒号连接
                        if not first_item.endswith(('：', ':', '、')):
                            first_item += '：'

                        combined = first_item + ' '.join(row_content[1:])
                    else:
                        combined = ' '.join(row_content)
                else:
                    combined = row_content[0]

                meaningful_lines.append(combined)

        return meaningful_lines

    def set_chinese_font(self, paragraph):
        """设置段落中文字体"""
        run = paragraph.runs[0] if paragraph.runs else paragraph.add_run('')
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        return paragraph

    def create_indented_paragraph(self, doc, text, level=0):
        """创建带缩进的段落"""
        paragraph = doc.add_paragraph()

        # 设置缩进：每级缩进2个字符
        indent_chars = 2 * level
        if indent_chars > 0:
            # 添加缩进空格
            indent_text = '　' * indent_chars  # 使用全角空格
            text = indent_text + text

        run = paragraph.add_run(text)

        # 设置字体
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(10.5)

        # 设置段落格式
        paragraph_format = paragraph.paragraph_format
        paragraph_format.line_spacing = 1.5  # 1.5倍行距
        paragraph_format.space_after = Pt(6)  # 段后间距

        # 首行缩进2字符
        paragraph_format.first_line_indent = Inches(0.25)

        return paragraph

    def process_sheet(self, doc, sheet_name, sheet_index, total_sheets):
        """处理单个sheet，添加到文档中"""
        print(f"  正在处理: {sheet_name} (第{sheet_index+1}/{total_sheets}个)")

        try:
            # 读取sheet，不设header，保留所有数据
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name, header=None)

            # 添加sheet标题
            title = doc.add_heading(f"重要：以下笔记的记录日期【{sheet_name}】", level=2)
            self.set_chinese_font(title)

            # 获取有意义的文本内容
            content_lines = self.extract_meaningful_content(df)

            if not content_lines:
                # 如果没有提取到内容，尝试原始方法
                empty_para = doc.add_paragraph("（此工作表内容为空或格式特殊）")
                self.set_chinese_font(empty_para)
                return

            # 统计信息
            stats_para = doc.add_paragraph(f"📊 提取到 {len(content_lines)} 条有效内容")
            self.set_chinese_font(stats_para)

            # 添加内容，智能设置缩进
            for line in content_lines:
                # 根据内容类型设置缩进级别
                indent_level = 0

                # 如果是编号内容，根据编号级别设置缩进
                if re.match(r'^[一二三四五六七八九十]、', line):
                    indent_level = 0  # 一级标题
                elif re.match(r'^\d+[\.、]', line):
                    # 检查是几级编号
                    match = re.match(r'^(\d+)', line)
                    if match:
                        num = int(match.group(1))
                        if num <= 10:
                            indent_level = 1
                        else:
                            indent_level = 2
                elif re.match(r'^[A-Za-z]\.[\s]', line):
                    indent_level = 2  # 英文编号一般是三级
                elif re.match(r'^\([一二三四五六七八九十]\)', line):
                    indent_level = 3  # 带括号的编号
                elif re.match(r'^###', line) or '###' in line:
                    # 填空题内容，稍微缩进
                    indent_level = 1

                # 创建带缩进的段落
                self.create_indented_paragraph(doc, line, indent_level)

            print(f"    ✓ 提取了 {len(content_lines)} 行内容")

        except Exception as e:
            error_msg = f"处理工作表 {sheet_name} 时出错: {str(e)}"
            print(f"    ✗ {error_msg}")

            error_para = doc.add_paragraph(f"❌ 处理错误: {error_msg}")
            self.set_chinese_font(error_para)

    def convert_with_batch(self, batch_size=10):
        """
        按批次转换Excel文件

        Args:
            batch_size: 每个docx文件包含的sheet数量
        """
        print(f"正在读取Excel文件: {self.excel_path}")

        try:
            # 读取Excel文件信息
            excel_file = pd.ExcelFile(self.excel_path)
            all_sheets = excel_file.sheet_names
            total_sheets = len(all_sheets)

            print(f"找到 {total_sheets} 个工作表")
            print(f"将按每 {batch_size} 个sheet分组生成docx文件")

            # 计算需要多少个批次
            num_batches = math.ceil(total_sheets / batch_size)
            print(f"需要生成 {num_batches} 个docx文件")

            generated_files = []

            # 分批处理
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, total_sheets)
                batch_sheets = all_sheets[start_idx:end_idx]

                # 创建新文档
                doc = Document()

                # 设置文档默认字体
                style = doc.styles['Normal']
                font = style.font
                font.name = '宋体'
                font._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                font.size = Pt(10.5)

                # 添加文档标题
                doc_title = doc.add_heading(f'Excel笔记转换 - 批次 {batch_idx+1}', 0)
                self.set_chinese_font(doc_title)

                # 添加文档信息
                info_para = doc.add_paragraph()
                info_para.add_run(f"源文件: {os.path.basename(self.excel_path)}\n")
                info_para.add_run(f"本批次包含工作表: {start_idx+1}-{end_idx} ({len(batch_sheets)}个)\n")
                info_para.add_run(f"格式: 表格内容已转换为普通段落，带智能缩进")
                self.set_chinese_font(info_para)

                doc.add_page_break()

                print(f"\n{'='*60}")
                print(f"📁 正在处理批次 {batch_idx+1}/{num_batches}")
                print(f"📄 包含工作表: {', '.join(batch_sheets[:3])}" +
                      (f" 等{len(batch_sheets)}个" if len(batch_sheets) > 3 else ""))
                print(f"{'='*60}")

                # 处理本批次中的每个sheet
                for sheet_idx, sheet_name in enumerate(batch_sheets):
                    self.process_sheet(doc, sheet_name, sheet_idx, len(batch_sheets))

                    # 如果不是最后一个sheet，添加分页符
                    if sheet_idx < len(batch_sheets) - 1:
                        doc.add_page_break()

                # 保存文档
                batch_num = batch_idx + 1
                output_filename = f"Excel笔记_批次{batch_num:02d}_({start_idx+1}-{end_idx}).docx"
                output_path = os.path.join(self.output_dir, output_filename)

                doc.save(output_path)
                generated_files.append(output_path)

                file_size = os.path.getsize(output_path) / 1024 / 1024  # MB
                print(f"\n✓ 批次 {batch_idx+1} 完成!")
                print(f"  文件名: {output_filename}")
                print(f"  文件大小: {file_size:.2f} MB")

                # 给个进度提示
                if batch_idx < num_batches - 1:
                    remaining = num_batches - batch_idx - 1
                    print(f"  剩余 {remaining} 个批次\n")

            # 生成汇总报告
            summary_path = self.create_summary_report(all_sheets, generated_files, batch_size)
            if summary_path:
                generated_files.append(summary_path)

            # 打印完成信息
            print(f"\n{'='*60}")
            print("🎉 转换完成！")
            print(f"📁 输出目录: {os.path.abspath(self.output_dir)}")
            print(f"📄 生成文件:")
            for file in generated_files:
                filename = os.path.basename(file)
                file_size = os.path.getsize(file) / 1024  # KB
                if file_size > 1024:
                    file_size_str = f"{file_size/1024:.1f} MB"
                else:
                    file_size_str = f"{file_size:.1f} KB"
                print(f"  • {filename} ({file_size_str})")
            print(f"{'='*60}")

            return generated_files

        except Exception as e:
            print(f"\n❌ 转换过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return []

    def create_summary_report(self, all_sheets, generated_files, batch_size):
        """创建汇总报告"""
        try:
            doc = Document()

            # 标题
            title = doc.add_heading('Excel转docx转换报告', 0)
            self.set_chinese_font(title)

            # 基本信息
            doc.add_paragraph(f"源文件: {os.path.basename(self.excel_path)}")
            doc.add_paragraph(f"总工作表数: {len(all_sheets)}")
            doc.add_paragraph(f"批次大小: 每{batch_size}个sheet一组")
            doc.add_paragraph(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
            doc.add_paragraph(f"生成文件数: {len(generated_files)}")

            doc.add_page_break()

            # 工作表列表
            doc.add_heading('工作表列表', 1)

            table = doc.add_table(rows=len(all_sheets)+1, cols=3)
            table.style = 'Table Grid'

            # 表头
            header_cells = table.rows[0].cells
            header_cells[0].text = "序号"
            header_cells[1].text = "工作表名称"
            header_cells[2].text = "所属批次"

            # 数据行
            for idx, sheet_name in enumerate(all_sheets, 1):
                row_cells = table.rows[idx].cells
                row_cells[0].text = str(idx)
                row_cells[1].text = sheet_name

                # 计算所属批次
                batch_num = ((idx - 1) // batch_size) + 1
                row_cells[2].text = f"批次{batch_num}"

            # 批次详情
            doc.add_page_break()
            doc.add_heading('批次详情', 1)

            for i, file_path in enumerate(generated_files):
                if "批次" in os.path.basename(file_path):
                    filename = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / 1024

                    if file_size > 1024:
                        size_str = f"{file_size/1024:.1f} MB"
                    else:
                        size_str = f"{file_size:.1f} KB"

                    doc.add_paragraph(f"• {filename} - {size_str}")

            # 保存
            summary_path = os.path.join(self.output_dir, "转换汇总报告.docx")
            doc.save(summary_path)

            print(f"\n📋 汇总报告已生成: 转换汇总报告.docx")
            return summary_path

        except Exception as e:
            print(f"创建汇总报告时出错: {e}")
            return None

def main():
    """主函数"""
    print("""
    ═══════════════════════════════════════════════════
        Excel批量转docx工具（智能检测行数版本）
        功能：将Excel每个sheet转换为普通段落
              每10个sheet合并到一个docx文件
              动态检测每个sheet的实际行数
    ═══════════════════════════════════════════════════
    """)

    # 配置参数
    excel_path = input("请输入Excel文件路径: ").strip('"').strip("'")

    if not os.path.exists(excel_path):
        print(f"❌ 文件不存在: {excel_path}")
        return

    # 自动检测文件格式
    if not excel_path.lower().endswith(('.xlsx', '.xls')):
        print("❌ 请提供Excel文件 (.xlsx 或 .xls)")
        return

    # 设置批次大小
    batch_size_input = input("每多少个sheet合并为一个docx文件? (默认10): ").strip()
    batch_size = int(batch_size_input) if batch_size_input.isdigit() else 10

    # 设置输出目录
    file_name = os.path.splitext(os.path.basename(excel_path))[0]
    output_dir = f"{file_name}_每{batch_size}个一组"

    print(f"\n📊 开始处理: {os.path.basename(excel_path)}")
    print(f"📂 输出到: {output_dir}")
    print(f"📦 每个docx包含: {batch_size}个sheet")
    print("-" * 60)

    # 创建转换器并执行
    converter = ExcelToParagraphConverter(excel_path, output_dir)
    converter.convert_with_batch(batch_size)

if __name__ == "__main__":
    try:
        # 检查必要库
        import pandas
        from docx import Document
    except ImportError:
        print("❌ 缺少必要库，正在安装...")
        import subprocess
        import sys

        packages = ["pandas", "openpyxl", "python-docx"]
        for package in packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        print("✅ 安装完成，请重新运行脚本")
        input("按回车键退出...")
        sys.exit()

    main()