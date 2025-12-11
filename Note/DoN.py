"""
笔记知识库API测试与检索脚本（适配单sheet单文件版本）
功能：测试秘塔搜索API，建立真题到笔记的检索系统框架
"""

import json
import logging
import re
import time
from collections import defaultdict
from typing import List, Dict

import pandas as pd
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_search.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# noinspection SpellCheckingInspection
AK = "mk-BEDECEE5985625828541DB38DFE3DD36"
ST_ID = "8687113534114930688"


class NotesKnowledgeBase:
    """笔记知识库API客户端"""

    def __init__(self, api_key: str, search_topic_id: str):
        """
        初始化知识库客户端

        Args:
            api_key: 秘塔搜索API密钥
            search_topic_id: 知识库ID
        """
        self.api_key = api_key
        self.search_topic_id = search_topic_id
        self.base_url = "https://metaso.cn/api/open/search/v2"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive'
        }

        # API调用统计
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'total_time': 0
        }

        # 缓存机制
        self.cache = {}

    def search_notes(self, question: str, max_retries: int = 3) -> Dict:
        """
        向笔记知识库提问

        Args:
            question: 查询问题
            max_retries: 最大重试次数

        Returns:
            API响应结果
        """
        # 检查缓存
        cache_key = question.strip().lower()
        if cache_key in self.cache:
            logger.debug(f"使用缓存: {question[:50]}...")
            return self.cache[cache_key]

        params = {
            'question': question,
            'searchTopicId': self.search_topic_id
        }

        start_time = time.time()
        self.stats['total_queries'] += 1

        for attempt in range(max_retries):
            try:
                logger.debug(f"查询: {question[:100]}... (尝试 {attempt + 1}/{max_retries})")

                response = requests.post(
                    self.base_url,
                    data=json.dumps(params),
                    headers=self.headers,
                    timeout=30
                )

                elapsed = time.time() - start_time
                self.stats['total_time'] += elapsed

                if response.status_code == 200:
                    result = response.json()
                    self.cache[cache_key] = result
                    self.stats['successful_queries'] += 1

                    logger.info(f"✓ 查询成功: {question[:80]}... ({elapsed:.2f}s)")
                    return result
                else:
                    logger.warning(f"查询失败 {response.status_code}: {response.text}")
                    self.stats['failed_queries'] += 1

                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 指数退避
                        logger.debug(f"等待 {wait_time}s 后重试...")
                        time.sleep(wait_time)

            except requests.exceptions.Timeout:
                logger.warning(f"查询超时: {question[:50]}...")
                self.stats['failed_queries'] += 1
                time.sleep(2 ** attempt)

            except Exception as e:
                logger.error(f"查询异常: {e}")
                self.stats['failed_queries'] += 1
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        # 所有重试都失败
        error_result = {
            "error": "查询失败",
            "question": question,
            "retries": max_retries
        }
        self.cache[cache_key] = error_result
        return error_result

    def parse_search_result(self, result: Dict) -> Dict:
        """
        解析秘塔搜索API返回的搜索结果
        """
        parsed = {
            'has_answer': False,
            'answer': '',
            'clean_answer': '',
            'sources': [],
            'confidence': 0.0,
            'references': [],
            'balance': 0,
            'raw_data': result
        }

        try:
            # 1. 检查错误码
            if 'errCode' in result and result['errCode'] != 0:
                parsed['answer'] = f"API错误: {result.get('message', '未知错误')}"
                return parsed

            # 2. 检查data字段
            if 'data' not in result:
                parsed['answer'] = "API返回数据格式异常"
                return parsed

            data = result['data']

            # 3. 提取回答文本
            answer_text = data.get('text', '')
            if answer_text and answer_text.strip():
                parsed['has_answer'] = True
                parsed['answer'] = answer_text.strip()

                # 清理引用标记
                clean_text = re.sub(r'\[\[\d+]]', '', answer_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                parsed['clean_answer'] = clean_text

            # 4. 提取引用信息
            if 'references' in data and isinstance(data['references'], list):
                parsed['references'] = data['references']

                # 构建sources列表
                seen_references = {}
                for ref in data['references']:
                    try:
                        title = ref.get('title', '')
                        page = ref.get('page', 1)
                        key = f"{title}_{page}"

                        if key not in seen_references:
                            source_info = {
                                'title': title, 'page': page, 'total_page': ref.get('total_page', 1),
                                'index': ref.get('index', 0),
                                'refer_id': ref.get('display', {}).get('refer_id', 0),
                                'article_type': ref.get('article_type', ''),
                                'publish_date': ref.get('publish_date', ''),
                                'file_meta': ref.get('file_meta', {}),
                                'score': self.calculate_reference_score(ref),
                                'extracted_date': self.extract_date_from_string(title)
                            }

                            # 提取日期信息（从title中）

                            # 提取内容片段
                            if parsed['answer']:
                                ref_content = self.extract_reference_content(parsed['answer'], ref.get('index', 0))
                                source_info['content'] = ref_content

                            seen_references[key] = source_info

                    except Exception as e:
                        logger.debug(f"处理引用时出错: {e}")
                        continue

                parsed['sources'] = list(seen_references.values())

                # 计算平均置信度
                if parsed['sources']:
                    scores = [s.get('score', 0) for s in parsed['sources']]
                    parsed['confidence'] = sum(scores) / len(scores)
                else:
                    parsed['confidence'] = 0.5 if parsed['has_answer'] else 0.0

            # 5. 提取其他信息
            if 'balance' in data:
                parsed['balance'] = data['balance']

            if 'sessionId' in data:
                parsed['session_id'] = data['sessionId']

            if 'resultId' in data:
                parsed['result_id'] = data['resultId']

        except Exception as e:
            logger.error(f"解析结果失败: {e}")
            parsed['answer'] = f"解析错误: {str(e)}"

        return parsed

    @staticmethod
    def calculate_reference_score(reference: Dict) -> float:
        """计算单个引用的相关性分数"""
        score = 0.5  # 基础分

        try:
            # 1. 根据索引调整分数
            index = reference.get('index', 1)
            if index <= 3:
                score += 0.2
            elif index <= 6:
                score += 0.1

            # 2. 如果提供了具体页面，分数较高
            page = reference.get('page', 1)
            total_page = reference.get('total_page', 1)
            if 0 < page < total_page:
                score += 0.1

            # 3. 根据文章类型调整分数
            article_type = reference.get('article_type', '')
            if article_type == '笔记':
                score += 0.1

            # 确保分数在0-1之间
            score = max(0.0, min(1.0, score))

        except Exception as e:
            logger.debug(f"计算引用分数时出错: {e}")

        return round(score, 3)

    @staticmethod
    def extract_reference_content(answer: str, ref_index: int) -> str:
        """从回答中提取特定引用的相关内容"""
        if not answer or ref_index <= 0:
            return ""

        try:
            ref_marker = f"[[{ref_index}]]"
            start_pos = answer.find(ref_marker)
            if start_pos == -1:
                return ""

            # 查找句子边界
            sentence_start = answer.rfind('.', 0, start_pos)
            if sentence_start == -1:
                sentence_start = 0
            else:
                sentence_start += 1

            sentence_end = answer.find('.', start_pos)
            if sentence_end == -1:
                sentence_end = len(answer)
            else:
                sentence_end += 1

            sentence = answer[sentence_start:sentence_end].strip()
            sentence = sentence.replace(ref_marker, '').strip()

            # 如果句子太短，扩展范围
            if len(sentence) < 20:
                para_start = answer.rfind('\n\n', 0, start_pos)
                if para_start == -1:
                    para_start = 0

                para_end = answer.find('\n\n', start_pos)
                if para_end == -1:
                    para_end = len(answer)

                sentence = answer[para_start:para_end].strip()
                sentence = sentence.replace(ref_marker, '').strip()

            # 截断过长的内容
            if len(sentence) > 200:
                sentence = sentence[:200] + "..."

            return sentence

        except Exception as e:
            logger.debug(f"提取引用内容时出错: {e}")
            return ""

    @staticmethod
    def extract_date_from_string(text: str) -> str:
        """从字符串中提取8位日期"""
        if not text:
            return ""

        import re
        matches = re.findall(r'\b(20\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01]))\b', text)

        if matches:
            for match in matches:
                date_str = match[0]
                if len(date_str) == 8 and date_str.isdigit():
                    return date_str

        return ""

    def extract_dates_from_sources(self, sources: List[Dict]) -> List[str]:
        """
        从源文档元数据中提取日期

        Args:
            sources: parse_search_result返回的sources列表

        Returns:
            日期列表，如 ['20251208', '20251209']
        """
        dates = []

        for source in sources:
            try:
                # 从title中提取日期
                title = source.get('title', '')
                date_from_title = self.extract_date_from_string(title)
                if date_from_title:
                    dates.append(date_from_title)
                    continue

                # 从文件元数据中提取
                file_meta = source.get('file_meta', {})
                if file_meta:
                    file_url = file_meta.get('url', '')
                    if file_url:
                        # 从URL中提取文件名
                        file_name = file_url.split('/')[-1] if '/' in file_url else file_url
                        date_from_file = self.extract_date_from_string(file_name)
                        if date_from_file:
                            dates.append(date_from_file)

            except Exception as e:
                logger.debug(f"从源文档提取日期时出错: {e}")
                continue

        # 去重并排序
        return sorted(list(set(dates)))

    @staticmethod
    def extract_sheet_dates_from_answer(answer: str) -> List[str]:
        """
        从回答中提取工作表日期（备用方法）

        这是备用的日期提取方法，当从源文档中提取不到日期时使用
        """
        dates = []

        try:
            # 方法1：从###框住的区域提取
            hash_pattern = r'###(.*?)###'
            hash_matches = re.findall(hash_pattern, answer, re.DOTALL)

            for hash_content in hash_matches:
                if hash_content:
                    # 从###区域内提取8位数字
                    date_candidates = re.findall(r'\b(20\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01]))\b', hash_content)
                    for match in date_candidates:
                        date_str = match[0]
                        if len(date_str) == 8 and date_str.isdigit():
                            dates.append(date_str)

            # 方法2：如果###中没有找到，从整个回答中提取
            if not dates:
                all_dates = re.findall(r'\b(20\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01]))\b', answer)
                for match in all_dates:
                    date_str = match[0]
                    if len(date_str) == 8 and date_str.isdigit():
                        dates.append(date_str)

            # 去重
            dates = list(set(dates))

        except Exception as e:
            logger.debug(f"从回答中提取日期时出错: {e}")

        return dates

    @staticmethod
    def extract_source_metadata(source: Dict) -> Dict:
        """
        从源文档中提取元数据
        """
        metadata = {
            'title': source.get('title', ''),
            'page': source.get('page', 1),
            'total_page': source.get('total_page', 1),
            'score': source.get('score', 0.0),
            'content': source.get('content', ''),
            'article_type': source.get('article_type', ''),
            'refer_id': source.get('refer_id', 0),
            'publish_date': source.get('publish_date', ''),
            'file_meta': source.get('file_meta', {}),
            'extracted_date': source.get('extracted_date', ''),
            'full_info': source
        }

        # 计算页面比例
        if metadata['total_page'] > 0:
            metadata['page_ratio'] = metadata['page'] / metadata['total_page']
        else:
            metadata['page_ratio'] = 0.0

        return metadata

    # noinspection PyTypeChecker
    def get_statistics(self) -> Dict:
        """获取API使用统计"""
        stats = self.stats.copy()
        if stats['total_queries'] > 0:
            stats['success_rate'] = stats['successful_queries'] / stats['total_queries'] * 100
            stats['avg_time'] = stats['total_time'] / stats['total_queries']
        else:
            stats['success_rate'] = 0.0
            stats['avg_time'] = 0.0

        stats['cache_size'] = len(self.cache)
        return stats


class ExamNotesSearcher:
    """真题笔记检索器（适配单sheet单文件版本）"""

    def __init__(self, knowledge_base: NotesKnowledgeBase):
        self.kb = knowledge_base

        # 考研科目定义
        self.subjects = {
            '政治': self.get_political_exam_points,
            '408': self.get_408_exam_points,
            '数学二': self.get_math_exam_points
        }

        # 检索结果存储
        self.search_results = defaultdict(list)

    @staticmethod
    def get_political_exam_points() -> List[str]:
        """政治真题知识点"""
        return [
            "矛盾的普遍性和特殊性",
            "实践与认识的辩证关系",
            "马克思主义基本原理",
            "社会主义初级阶段理论",
            "习近平新时代中国特色社会主义思想",
            "社会主义核心价值观",
            "新发展理念",
            "中国式现代化",
            "人类命运共同体",
            "一带一路倡议",
            "供给侧结构性改革",
            "共同富裕",
            "国家治理体系和治理能力现代化",
            "全过程人民民主",
            "总体国家安全观",
            "习近平经济思想",
            "生态文明建设",
            "文化自信",
            "人类文明新形态",
            "党的自我革命"
        ]

    @staticmethod
    def get_408_exam_points() -> List[str]:
        """408真题知识点"""
        return [
            "数据结构：二叉树遍历",
            "算法：动态规划",
            "操作系统：进程同步",
            "计算机网络：TCP/IP协议",
            "计算机组成原理：指令系统",
            "数据结构：排序算法",
            "算法：贪心算法",
            "操作系统：内存管理",
            "计算机网络：HTTP协议",
            "计算机组成原理：CPU结构",
            "数据结构：图算法",
            "算法：回溯算法",
            "操作系统：文件系统",
            "计算机网络：DNS解析",
            "计算机组成原理：流水线技术",
            "数据结构：哈希表",
            "算法：分治算法",
            "操作系统：死锁避免",
            "计算机网络：网络安全",
            "计算机组成原理：缓存机制"
        ]

    @staticmethod
    def get_math_exam_points() -> List[str]:
        """数学二真题知识点"""
        return [
            "极限计算：洛必达法则",
            "导数应用：单调性与极值",
            "不定积分计算",
            "定积分应用",
            "微分方程求解",
            "多元函数微分",
            "二重积分计算",
            "矩阵运算与性质",
            "向量空间与线性变换",
            "特征值与特征向量",
            "二次型标准化",
            "曲线积分",
            "曲面积分",
            "无穷级数收敛性",
            "偏导数计算",
            "方向导数与梯度",
            "拉格朗日乘数法",
            "傅里叶级数",
            "常微分方程初值问题",
            "线性方程组求解"
        ]

    @staticmethod
    def build_search_queries(exam_point: str, subject: str) -> List[str]:
        """
        为知识点构建查询问题 - 优化版（适用于单个sheet一个docx的情况）

        现在每个文档的文件名就是日期，知识库应该能直接返回文档名称
        """

        # 直接明确的查询模板
        base_queries = [
            # 直接要求返回文档名称（日期）
            f"在我的笔记文档中查找关于'{exam_point}'的内容。"
            f"请直接告诉我哪些文档（文档名称/日期）包含了这个知识点。"
            f"文档名称格式为'YYYYMMDD.docx'。请列出所有相关文档的日期。",

            # 强调文档名就是日期
            f"搜索'{exam_point}'相关内容。每个笔记文档的文件名就是记录日期，格式如20251208.docx。"
            f"请找出所有包含该知识点的文档，并列出它们的文件名（只需要日期部分）。",

            # 结合科目特点
            f"查找考研{subject}知识点'{exam_point}'的相关笔记。"
            f"每个笔记文件以日期命名（如20251208.docx）。请返回所有包含该知识点的文档日期。",

            # 简化版
            f"哪些日期的笔记中提到了'{exam_point}'？请直接给出日期列表（格式如：20251208, 20251209）。"
        ]

        # 科目特定的查询
        subject_specific = {
            '政治': [
                f"政治理论'{exam_point}'在哪些日期的笔记中有记录？每个笔记文件以日期命名。请列出日期。",
                f"查找关于'{exam_point}'的政治学习笔记。文档以日期命名，如20251208.docx。请返回相关日期。"
            ],
            '408': [
                f"计算机408知识点'{exam_point}'在哪些日期的笔记中？文档文件名就是日期。请给出日期列表。",
                f"搜索'{exam_point}'的计算机笔记。每个文档代表一天的笔记，文件名是日期。请列出相关日期。"
            ],
            '数学二': [
                f"数学二考点'{exam_point}'在哪些日期的笔记中记录？文档以日期命名。请提供日期。",
                f"查找'{exam_point}'的数学学习笔记。每个文档对应一天的笔记，文件名是日期。请返回日期。"
            ]
        }

        # 合并查询
        all_queries = base_queries + subject_specific.get(subject, [])

        # 添加强调格式的查询
        format_queries = [
            f"请搜索'{exam_point}'并返回包含该知识点的笔记文档日期。"
            f"要求：直接给出日期列表，每个日期格式为8位数字（如20251208），多个日期用逗号分隔。"
            f"例如：20251208, 20251209",

            f"查找'{exam_point}'。"
            f"每个笔记文档的文件名就是它的记录日期（如20251208.docx）。"
            f"请列出所有相关文档的日期（只需8位数字）。",

            f"在我的笔记库中搜索'{exam_point}'。"
            f"每个文件代表一天的笔记，文件名是日期（YYYYMMDD.docx）。"
            f"请直接返回日期列表，如：20251208, 20251210"
        ]

        return base_queries + format_queries

    def search_for_exam_point(self, exam_point: str, subject: str, max_queries: int = 3) -> List[Dict]:
        """
        搜索单个真题知识点的相关笔记 - 优化版

        现在从源文档的元数据中直接提取日期，而不是从回答文本中提取
        """
        results = []

        # 构建查询问题
        queries = self.build_search_queries(exam_point, subject)
        queries = queries[:max_queries]  # 限制查询数量

        logger.info(f"搜索'{exam_point}' ({subject}) - {len(queries)}个查询")

        for query in queries:
            try:
                # 调用API
                raw_result = self.kb.search_notes(query)

                # 解析结果
                parsed_result = self.kb.parse_search_result(raw_result)

                if parsed_result['has_answer']:
                    # 提取源文档信息
                    sources_info = []
                    for source in parsed_result['sources']:
                        source_meta = self.kb.extract_source_metadata(source)
                        sources_info.append(source_meta)

                    # 直接从源文档中提取日期
                    sheet_dates = self.kb.extract_dates_from_sources(parsed_result['sources'])

                    # 如果源文档中没有提取到日期，尝试从回答中提取
                    if not sheet_dates:
                        dates_from_answer = self.kb.extract_sheet_dates_from_answer(parsed_result['answer'])
                        sheet_dates = dates_from_answer

                    result_entry = {
                        'exam_point': exam_point,
                        'subject': subject,
                        'query': query,
                        'answer': parsed_result['answer'][:500],
                        'clean_answer': parsed_result.get('clean_answer', '')[:500],
                        'confidence': parsed_result['confidence'],
                        'sources': sources_info,
                        'full_answer': parsed_result['answer'],
                        'sheet_dates': sheet_dates,
                        'date_count': len(sheet_dates),
                        'date_extraction_method': 'from_sources' if sheet_dates else 'from_answer'
                    }

                    results.append(result_entry)

                    # 日志中显示日期信息
                    if sheet_dates:
                        logger.debug(f"  找到 {len(sheet_dates)} 个相关文档日期: {', '.join(sheet_dates)}")
                    else:
                        logger.debug(f"  未提取到文档日期信息")

                else:
                    logger.debug(f"  未找到相关信息")

                # 避免过快调用API
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"查询'{query}'时出错: {e}")
                continue

        return results

    def batch_search(self, subject: str, max_points: int = 5) -> Dict:
        """
        批量搜索某个科目的多个知识点

        Returns:
            搜索结果字典: {exam_point: [search_results]}
        """
        logger.info(f"\n开始批量搜索 {subject} 科目")

        # 获取该科目的知识点
        if subject in self.subjects:
            exam_points = self.subjects[subject]()
            exam_points = exam_points[:max_points]  # 限制数量进行测试
        else:
            logger.error(f"未知科目: {subject}")
            return {}

        all_results = {}

        for i, exam_point in enumerate(exam_points):
            logger.info(f"进度: {i + 1}/{len(exam_points)} - {exam_point}")

            results = self.search_for_exam_point(exam_point, subject)
            all_results[exam_point] = results

            # 进度间隔
            if i < len(exam_points) - 1:
                time.sleep(1)  # 避免API限制

        return all_results

    @staticmethod
    def analyze_results(search_results: Dict) -> pd.DataFrame:
        """
        分析检索结果，生成统计表格 - 增加日期统计

        Returns:
            DataFrame包含以下列:
            - exam_point: 真题知识点
            - subject: 科目
            - found_count: 找到的相关文档数
            - avg_confidence: 平均置信度
            - date_count: 提取到的工作表日期数量
            - date_list: 工作表日期列表
            - source_titles: 源文档标题列表
        """
        analysis_data = []

        for exam_point, results in search_results.items():
            if not results:
                continue

            # 提取所有源文档
            all_sources = []
            all_dates = []

            for result in results:
                all_sources.extend(result['sources'])
                # 收集所有日期
                dates = result.get('sheet_dates', [])
                all_dates.extend(dates)

            # 去重源文档（基于标题）
            unique_sources = {}
            for source in all_sources:
                title = source.get('title', '')
                if title and title not in unique_sources:
                    unique_sources[title] = source

            # 去重日期
            unique_dates = sorted(list(set(all_dates)))

            # 计算置信度
            confidences = [r['confidence'] for r in results if r['confidence'] > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            # 提取科目（假设所有结果科目相同）
            subject = results[0]['subject'] if results else '未知'

            analysis_data.append({
                'exam_point': exam_point,
                'subject': subject,
                'found_count': len(unique_sources),
                'avg_confidence': round(avg_confidence, 3),
                'date_count': len(unique_dates),
                'date_list': ', '.join(unique_dates),
                'source_titles': list(unique_sources.keys()),
                'total_searches': len(results)
            })

        return pd.DataFrame(analysis_data)

    def export_results(self, search_results: Dict, output_file: str = "exam_notes_search.xlsx"):
        """
        导出检索结果到Excel

        Args:
            search_results: 检索结果字典
            output_file: 输出文件路径
        """
        try:
            # 准备数据
            all_data = []

            for exam_point, results in search_results.items():
                for result in results:
                    # 基本信息
                    row = {
                        '真题知识点': exam_point,
                        '科目': result['subject'],
                        '查询问题': result['query'],
                        '回答摘要': result['answer'],
                        '置信度': result['confidence'],
                        '找到日期数': result['date_count'],
                        '日期列表': ', '.join(result['sheet_dates']) if result['sheet_dates'] else '无',
                        '日期提取方式': result.get('date_extraction_method', '未知')
                    }

                    # 源文档信息
                    for i, source in enumerate(result['sources'][:3]):  # 最多3个源
                        row[f'源文档{i + 1}_标题'] = source.get('title', '')
                        row[f'源文档{i + 1}_分数'] = source.get('score', 0)
                        row[f'源文档{i + 1}_提取日期'] = source.get('extracted_date', '无')
                        row[f'源文档{i + 1}_内容'] = source.get('content', '')[:100]  # 截断

                    all_data.append(row)

            # 创建DataFrame
            df = pd.DataFrame(all_data)

            # 排序
            if not df.empty:
                df = df.sort_values(['科目', '置信度'], ascending=[True, False])

            # 保存到Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='详细结果', index=False)

                # 添加汇总表
                summary_df = self.analyze_results(search_results)
                if not summary_df.empty:
                    summary_df.to_excel(writer, sheet_name='知识点汇总', index=False)

                # 添加API统计
                stats = self.kb.get_statistics()
                stats_df = pd.DataFrame([stats])
                stats_df.to_excel(writer, sheet_name='API统计', index=False)

            logger.info(f"结果已导出到: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"导出结果失败: {e}")
            return None


def check_api_connection():
    """测试API连接"""
    print("🧪 测试API连接...")

    # 使用提供的API信息
    api_key = AK
    search_topic_id = ST_ID

    # 创建知识库客户端
    kb = NotesKnowledgeBase(api_key, search_topic_id)

    # 简单测试查询
    test_queries = [
        "矛盾的普遍性和特殊性",
        "二叉树遍历算法",
        "极限计算洛必达法则"
    ]

    for query in test_queries:
        print(f"\n查询: '{query}'")
        result = kb.search_notes(query)

        # 解析结果
        parsed = kb.parse_search_result(result)

        if parsed['has_answer']:
            print(f"✓ 成功获取回答 ({parsed['confidence']:.2%})")
            print(f"回答摘要: {parsed['answer'][:200]}...")

            if parsed['sources']:
                print(f"找到 {len(parsed['sources'])} 个源文档")
                for i, source in enumerate(parsed['sources'][:2]):  # 显示前2个
                    meta = kb.extract_source_metadata(source)
                    print(f"  源{i + 1}: {meta['title']} (分数: {meta['score']:.2f})")

                    # 显示提取的日期
                    if meta['extracted_date']:
                        print(f"     提取日期: {meta['extracted_date']}")
        else:
            print(f"✗ 未找到相关信息")
            print(f"错误信息: {parsed['answer']}")

    # 显示统计信息
    stats = kb.get_statistics()
    print(f"\n📊 API使用统计:")
    print(f"  总查询数: {stats['total_queries']}")
    print(f"  成功数: {stats['successful_queries']}")
    print(f"  成功率: {stats['success_rate']:.1f}%")
    print(f"  平均耗时: {stats['avg_time']:.2f}s")

    return kb


def run_comprehensive_test():
    """运行综合测试"""
    print("\n" + "=" * 60)
    print("🧪 笔记知识库综合测试（单sheet单文件版本）")
    print("=" * 60)

    # 1. 初始化
    api_key = AK
    search_topic_id = ST_ID

    kb = NotesKnowledgeBase(api_key, search_topic_id)
    searcher = ExamNotesSearcher(kb)

    # 2. 测试单个科目（政治）
    print("\n📚 测试政治科目搜索...")
    political_results = searcher.batch_search('政治', max_points=3)

    # 3. 分析结果
    if political_results:
        analysis_df = searcher.analyze_results(political_results)

        print("\n📊 政治科目搜索结果分析:")
        print(analysis_df[['exam_point', 'found_count', 'date_count', 'date_list']].to_string(index=False))

        # 4. 导出结果
        output_file = searcher.export_results(political_results, "政治科目测试结果.xlsx")
        print(f"\n💾 结果已保存到: {output_file}")

    # 5. 显示API统计
    stats = kb.get_statistics()
    print(f"\n📈 最终API统计:")
    print(f"  总查询数: {stats['total_queries']}")
    print(f"  缓存命中: {stats['cache_size']}")
    print(f"  总耗时: {stats['total_time']:.1f}s")

    return searcher


def quick_test():
    """快速测试"""
    print("🚀 快速测试模式（单sheet单文件版本）")

    # 初始化
    api_key = AK
    search_topic_id = ST_ID

    kb = NotesKnowledgeBase(api_key, search_topic_id)

    # 测试几个关键查询
    test_cases = [
        ("矛盾的普遍性和特殊性在考研政治中如何考察？", "政治"),
        ("二叉树的前序、中序、后序遍历有什么区别？", "408"),
        ("如何使用洛必达法则计算极限？", "数学二"),
        ("请列出关于新质生产力的相关内容", "政治"),
        ("TCP三次握手的过程是怎样的？", "408")
    ]

    results = []

    for query, expected_subject in test_cases:
        print(f"\n🔍 查询: {query}")

        raw_result = kb.search_notes(query)
        parsed = kb.parse_search_result(raw_result)

        if parsed['has_answer']:
            print(f"✓ 找到相关信息")
            print(f"  回答摘要: {parsed['answer'][:150]}...")

            # 提取源信息
            sources = []
            for source in parsed['sources'][:2]:  # 前2个源
                meta = kb.extract_source_metadata(source)
                source_info = f"{meta['title']}({meta['score']:.2f})"
                if meta['extracted_date']:
                    source_info += f" [日期:{meta['extracted_date']}]"
                sources.append(source_info)

            if sources:
                print(f"  相关源文档: {', '.join(sources)}")

            # 从源文档中提取日期
            dates = kb.extract_dates_from_sources(parsed['sources'])
            if dates:
                print(f"  提取到的日期: {', '.join(dates)}")
        else:
            print(f"✗ 未找到相关信息")

        results.append({
            'query': query,
            'subject': expected_subject,
            'has_answer': parsed['has_answer'],
            'confidence': parsed['confidence']
        })

    # 统计
    total = len(results)
    success = sum(1 for r in results if r['has_answer'])

    print(f"\n📊 测试总结:")
    print(f"  总测试数: {total}")
    print(f"  成功数: {success}")
    print(f"  成功率: {success / total * 100:.1f}%")

    return kb


def check_date_extraction():
    """测试日期提取功能"""
    print("📅 测试日期提取功能（单sheet单文件版本）")
    print("=" * 60)

    # 初始化
    api_key = AK
    search_topic_id = ST_ID

    kb = NotesKnowledgeBase(api_key, search_topic_id)
    searcher = ExamNotesSearcher(kb)

    # 测试几个重点知识点
    test_cases = [
        ("矛盾的普遍性和特殊性", "政治"),
        ("二叉树遍历", "408"),
        ("定积分计算", "数学二"),
        ("新质生产力", "政治")
    ]

    for exam_point, subject in test_cases:
        print(f"\n🔍 测试: {exam_point} ({subject})")

        # 搜索
        results = searcher.search_for_exam_point(exam_point, subject, max_queries=2)

        if results:
            for result in results:
                print(f"  查询: {result['query'][:50]}...")
                print(f"  置信度: {result['confidence']:.3f}")

                if result['sheet_dates']:
                    print(f"  提取到的工作表日期: {', '.join(result['sheet_dates'])}")
                    print(f"  提取方式: {result['date_extraction_method']}")
                else:
                    print(f"  ⚠️ 未提取到工作表日期")

                # 显示源文档信息
                if result['sources']:
                    print(f"  相关源文档数: {len(result['sources'])}")
                    for i, source in enumerate(result['sources'][:2]):
                        print(f"    源{i + 1}: {source.get('title', '无标题')}")
                        if source.get('extracted_date'):
                            print(f"      提取日期: {source.get('extracted_date')}")

        time.sleep(1)  # 避免API限流

    print(f"\n{'=' * 60}")
    print("📊 总结：")
    print("现在每个Excel sheet单独保存为docx文件，文件名就是日期")
    print("查询时会明确要求知识库返回文档名称（日期）")
    print("日期提取优先级：1.从源文档标题中提取 2.从回答文本中提取")


def custom_search_test():
    """自定义搜索测试"""
    print("🎯 自定义搜索测试（单sheet单文件版本）")

    api_key = AK
    search_topic_id = ST_ID

    kb = NotesKnowledgeBase(api_key, search_topic_id)
    searcher = ExamNotesSearcher(kb)

    while True:
        print("\n" + "-" * 60)
        exam_point = input("请输入要搜索的知识点（输入 'quit' 退出）: ").strip()

        if exam_point.lower() in ['quit', 'exit', 'q']:
            break

        if exam_point:
            subject = input("请输入所属科目（政治/408/数学二）: ").strip()

            if subject not in ['政治', '408', '数学二']:
                print("⚠️ 科目无效，使用默认科目：政治")
                subject = '政治'

            print(f"\n搜索: {exam_point} ({subject})")
            results = searcher.search_for_exam_point(exam_point, subject, max_queries=2)

            if results:
                print(f"找到 {len(results)} 个查询结果")

                for i, result in enumerate(results):
                    print(f"\n结果 {i + 1}:")
                    print(f"  查询问题: {result['query'][:80]}...")
                    print(f"  置信度: {result['confidence']:.3f}")

                    if result['sheet_dates']:
                        print(f"  找到日期: {', '.join(result['sheet_dates'])}")
                        print(f"  提取方式: {result['date_extraction_method']}")
                    else:
                        print(f"  ⚠️ 未找到相关日期")

                    # 显示部分回答内容
                    if result['clean_answer']:
                        print(f"  回答摘要: {result['clean_answer'][:200]}...")
            else:
                print("未找到相关信息")


def main():
    """主函数"""
    print("""
    ════════════════════════════════════════════════════
        考研笔记知识库检索测试系统 (单sheet单文件版本)
        版本: 2.0
        功能: 测试秘塔搜索API，提取相关笔记的工作表日期
        说明: 每个Excel sheet单独保存为docx文件，文件名就是日期
    ════════════════════════════════════════════════════
    """)

    print("请选择测试模式:")
    print("1. 🔌 API连接测试")
    print("2. 🚀 快速功能测试")
    print("3. 📚 综合科目测试")
    print("4. 🎯 自定义查询测试")
    print("5. 📅 测试日期提取功能 (新版本)")
    print("6. 🔍 自定义知识点搜索")

    choice = input("\n请输入选项 (1-6): ").strip()

    if choice == '1':
        check_api_connection()

    elif choice == '2':
        quick_test()

    elif choice == '3':
        run_comprehensive_test()

    elif choice == '4':
        api_key = AK
        search_topic_id = ST_ID

        kb = NotesKnowledgeBase(api_key, search_topic_id)

        while True:
            query = input("\n请输入查询问题 (输入 'quit' 退出): ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                break

            if query:
                raw_result = kb.search_notes(query)
                parsed = kb.parse_search_result(raw_result)

                print(f"\n🔍 查询: {query}")
                if parsed['has_answer']:
                    print(f"✓ 找到相关信息:")
                    print(f"  回答: {parsed['answer'][:300]}...")

                    if parsed['sources']:
                        print(f"\n  相关源文档:")
                        for i, source in enumerate(parsed['sources'][:3]):
                            meta = kb.extract_source_metadata(source)
                            source_desc = f"  {i + 1}. {meta['title']} (相关性: {meta['score']:.2f})"
                            if meta['extracted_date']:
                                source_desc += f" [日期: {meta['extracted_date']}]"
                            print(source_desc)

                            if meta['content']:
                                print(f"     内容: {meta['content'][:100]}...")

                        # 提取日期
                        dates = kb.extract_dates_from_sources(parsed['sources'])
                        if dates:
                            print(f"\n  提取到的日期: {', '.join(dates)}")
                else:
                    print(f"✗ {parsed['answer']}")

        # 显示统计
        stats = kb.get_statistics()
        print(f"\n📊 本次会话统计:")
        print(f"  总查询数: {stats['total_queries']}")
        print(f"  成功数: {stats['successful_queries']}")
        print(f"  成功率: {stats['success_rate']:.1f}%")

    elif choice == '5':
        check_date_extraction()

    elif choice == '6':
        custom_search_test()

    else:
        print("无效选项")


if __name__ == "__main__":
    main()
