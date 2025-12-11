"""
笔记知识库API测试与检索脚本
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

        根据实际API返回结构：
        {
            'errCode': 0,
            'data': {
                'resultId': '...',
                'references': [
                    {
                        'link': '',
                        'title': 'Excel 笔记转换 - 批次 22',
                        'author': '',
                        'article_type': '笔记',
                        'index': 1,
                        'page': 59,
                        'total_page': 59,
                        'publish_date': '2025-12-10',
                        'display': {'refer_id': 1},
                        'file_meta': {'type': 'docx', 'url': '...'}
                    },
                    ...
                ],
                'balance': 5771,
                'sessionId': 8687123735392067584,
                'text': '回答内容...'  # 这里包含[[1]]这样的引用标记
            }
        }
        """
        parsed = {
            'has_answer': False,
            'answer': '',
            'clean_answer': '',  # 清理后的答案（不含引用标记）
            'sources': [],
            'confidence': 0.0,
            'references': [],  # 原始references
            'balance': 0,  # API余额
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

                # 清理引用标记，如[[1]]、[[2]]
                clean_text = re.sub(r'\[\[\d+]]', '', answer_text)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                parsed['clean_answer'] = clean_text

            # 4. 提取引用信息
            if 'references' in data and isinstance(data['references'], list):
                parsed['references'] = data['references']

                # 构建sources列表（去重并增强）
                seen_references = {}
                for ref in data['references']:
                    try:
                        # 使用(title, page)作为唯一标识
                        title = ref.get('title', '')
                        page = ref.get('page', 1)
                        key = f"{title}_{page}"

                        if key not in seen_references:
                            # 提取更详细的信息
                            source_info = {
                                'title': title,
                                'page': page,
                                'total_page': ref.get('total_page', 1),
                                'index': ref.get('index', 0),
                                'refer_id': ref.get('display', {}).get('refer_id', 0),
                                'article_type': ref.get('article_type', ''),
                                'publish_date': ref.get('publish_date', ''),
                                'file_type': ref.get('file_meta', {}).get('type', ''),
                                'file_url': ref.get('file_meta', {}).get('url', ''),
                                'score': self.calculate_reference_score(ref)  # 计算相关性分数
                            }

                            # 提取内容片段（从answer中提取引用此来源的部分）
                            if parsed['answer']:
                                # 查找[[index]]标记的内容
                                ref_content = self.extract_reference_content(parsed['answer'], ref.get('index', 0))
                                source_info['content'] = ref_content

                            # 判断是否是sheet（基于标题格式）
                            title_lower = title.lower()
                            is_sheet = (
                                    'excel' in title_lower or
                                    '笔记转换' in title_lower or
                                    '批次' in title_lower or
                                    re.search(r'batch\d+', title_lower) or
                                    re.search(r'第.*[章节页]', title)
                            )
                            source_info['is_sheet'] = is_sheet

                            # 计算批次信息
                            source_info['batch_info'] = self.extract_batch_info(title)

                            seen_references[key] = source_info

                    except Exception as e:
                        logger.debug(f"处理引用时出错: {e}")
                        continue

                parsed['sources'] = list(seen_references.values())

                # 如果有引用，计算平均置信度
                if parsed['sources']:
                    sources: list = parsed['sources']
                    scores = [s.get('score', 0) for s in sources]
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
        """
        计算单个引用的相关性分数

        基于以下因素：
        1. 页面信息：如果引用的是特定页面，分数较高
        2. 标题相关性：如果标题包含关键词，分数较高
        3. 引用索引：前面的引用通常更相关

        Returns:
            0.0 到 1.0 之间的分数
        """
        score = 0.5  # 基础分

        try:
            # 1. 根据索引调整分数（前面的引用更重要）
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
            elif article_type == '技术文档':
                score += 0.05

            # 4. 如果标题包含重要关键词
            title = reference.get('title', '').lower()
            important_keywords = ['excel', '笔记', '考研', '政治', '408', '数学', '算法', '数据结构']
            if any(keyword in title for keyword in important_keywords):
                score += 0.05

            # 确保分数在0-1之间
            score = max(0.0, min(1.0, score))

        except Exception as e:
            logger.debug(f"计算引用分数时出错: {e}")

        return round(score, 3)

    @staticmethod
    def extract_reference_content(answer: str, ref_index: int) -> str:
        """
        从回答中提取特定引用的相关内容

        查找包含[[ref_index]]标记的句子或段落

        Args:
            answer: 完整回答文本
            ref_index: 引用索引（从1开始）

        Returns:
            提取的内容片段
        """
        if not answer or ref_index <= 0:
            return ""

        try:
            # 查找引用标记
            ref_marker = f"[[{ref_index}]]"

            # 查找引用标记前后的内容
            start_pos = answer.find(ref_marker)
            if start_pos == -1:
                return ""

            # 向前找句子开始
            sentence_start = answer.rfind('.', 0, start_pos)
            if sentence_start == -1:
                sentence_start = 0
            else:
                sentence_start += 1  # 跳过句点

            # 向后找句子结束
            sentence_end = answer.find('.', start_pos)
            if sentence_end == -1:
                sentence_end = len(answer)
            else:
                sentence_end += 1  # 包含句点

            # 提取句子
            sentence = answer[sentence_start:sentence_end].strip()

            # 移除引用标记
            sentence = sentence.replace(ref_marker, '').strip()

            # 如果句子太短，扩展范围
            if len(sentence) < 20:
                # 向前扩展一段
                para_start = answer.rfind('\n\n', 0, start_pos)
                if para_start == -1:
                    para_start = 0

                # 向后扩展一段
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
    def extract_batch_info(title: str) -> Dict:
        """
        从标题中提取批次信息

        示例标题: "Excel 笔记转换 - 批次 22"

        Returns:
            {'batch_num': 22, 'has_excel': True, 'is_note_conversion': True}
        """
        batch_info = {
            'batch_num': 0,
            'has_excel': False,
            'is_note_conversion': False,
            'original_title': title
        }

        try:
            title_lower = title.lower()

            # 检查是否包含Excel和笔记转换
            batch_info['has_excel'] = 'excel' in title_lower
            batch_info['is_note_conversion'] = '笔记转换' in title

            # 提取批次号
            batch_match = re.search(r'批次\s*(\d+)', title)
            if batch_match:
                batch_info['batch_num'] = int(batch_match.group(1))
            else:
                # 尝试其他格式
                batch_match = re.search(r'batch\s*(\d+)', title_lower)
                if batch_match:
                    batch_info['batch_num'] = int(batch_match.group(1))

            # 提取页码范围（如果有）
            page_match = re.search(r'\((\d+)-(\d+)\)', title)
            if page_match:
                batch_info['start_page'] = int(page_match.group(1))
                batch_info['end_page'] = int(page_match.group(2))

        except Exception as e:
            logger.debug(f"提取批次信息时出错: {e}")

        return batch_info

    @staticmethod
    def extract_source_metadata(source: Dict) -> Dict:
        """
        从源文档中提取元数据（适配新格式）

        Args:
            source: 解析后的source字典（来自parse_search_result）

        Returns:
            元数据: {
                'title': str,           # 文档标题
                'page': int,            # 页码
                'total_page': int,      # 总页数
                'score': float,         # 相关性分数
                'content': str,         # 内容片段
                'is_sheet': bool,       # 是否是sheet
                'batch_num': int,       # 批次号
                'article_type': str,    # 文章类型
                'refer_id': int,        # 引用ID
                'publish_date': str,    # 发布日期
                'file_type': str        # 文件类型
            }
        """
        metadata = {
            'title': source.get('title', ''),
            'page': source.get('page', 1),
            'total_page': source.get('total_page', 1),
            'score': source.get('score', 0.0),
            'content': source.get('content', ''),
            'is_sheet': source.get('is_sheet', False),
            'batch_num': source.get('batch_info', {}).get('batch_num', 0),
            'article_type': source.get('article_type', ''),
            'refer_id': source.get('refer_id', 0),
            'publish_date': source.get('publish_date', ''),
            'file_type': source.get('file_type', ''),
            'full_info': source  # 保留完整信息
        }

        # 计算页面比例（用于排序）
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

    @staticmethod
    def extract_sheet_dates_from_answer(answer: str) -> List[str]:
        """
        从回答中提取工作表日期（Excel sheet名称）

        新的查找逻辑：
        1. 先找###框住的区域，找到的情况下，在###框住区域内部进行匹配
        2. 如果没找到，从回答文本的最后往前找，第一个匹配的日期作为唯一的结果

        Returns:
            日期字符串列表，如 ['20251208', '20251209']
        """
        dates = []

        try:
            # 首先，尝试从###框住的区域提取
            hash_pattern = r'###(.*?)###'
            hash_matches = re.findall(hash_pattern, answer, re.DOTALL)

            if hash_matches:
                # 获取最后一个###框住的区域（通常是最新的结论）
                last_hash_block = hash_matches[-1].strip() if hash_matches else ""

                if last_hash_block:
                    logger.debug(f"找到###框住区域: {last_hash_block[:100]}...")

                    # 从###区域内提取所有可能的日期
                    date_candidates = []

                    # 模式1：直接查找8位数字日期（YYYYMMDD）
                    date_patterns = [
                        r'\b(\d{4})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\b',  # YYYYMMDD
                        r'\b(\d{4})年(\d{1,2})月(\d{1,2})日\b',  # YYYY年MM月DD日
                        r'(\d{8})',  # 直接8位数字
                        r'[\(（](\d{8})[\)）]',  # (20251208)或（20251208）
                    ]

                    for pattern in date_patterns:
                        matches = re.findall(pattern, last_hash_block)
                        for match in matches:
                            if isinstance(match, tuple):
                                # 如果是分组匹配，拼接成完整日期
                                date_str = ''.join(str(num) for num in match)
                            else:
                                date_str = match

                            # 验证是否为有效日期
                            if len(date_str) == 8 and date_str.isdigit():
                                year = int(date_str[:4])
                                month = int(date_str[4:6])
                                day = int(date_str[6:8])

                                # 基本验证（2024-2025年，月份1-12，日期1-31）
                                if (2024 <= year <= 2025 and
                                        1 <= month <= 12 and
                                        1 <= day <= 31):
                                    date_candidates.append(date_str)

                    # 去重
                    if date_candidates:
                        dates = sorted(list(set(date_candidates)))
                        logger.debug(f"从###区域提取到日期: {dates}")
                        return dates

            # 如果没有从###区域提取到日期，从整个回答文本中提取
            if not dates:
                # 先查找所有可能的日期模式
                all_date_patterns = [
                    r'\b(\d{4})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\b',  # YYYYMMDD
                    r'\b(\d{4})年(\d{1,2})月(\d{1,2})日\b',  # YYYY年MM月DD日
                    r'工作表[：:]\s*(\d{8})',  # 工作表：20251208
                    r'日期[：:]\s*(\d{8})',  # 日期：20251208
                    r'(\d{8})\s*工作表',  # 20251208工作表
                    r'[\(（](\d{8})[\)）]',  # (20251208)或（20251208）
                    r'###.*?(\d{8}).*?###',  # ###包含的日期
                ]

                all_dates = []

                for pattern in all_date_patterns:
                    matches = re.findall(pattern, answer)
                    for match in matches:
                        if isinstance(match, tuple):
                            # 如果是分组匹配，拼接成完整日期
                            date_str = ''.join(str(num) for num in match)
                        else:
                            date_str = match

                        # 验证是否为有效日期
                        if len(date_str) == 8 and date_str.isdigit():
                            year = int(date_str[:4])
                            month = int(date_str[4:6])
                            day = int(date_str[6:8])

                            # 基本验证（2024-2025年，月份1-12，日期1-31）
                            if (2024 <= year <= 2025 and
                                    1 <= month <= 12 and
                                    1 <= day <= 31):
                                all_dates.append({
                                    'date': date_str,
                                    'pattern': pattern
                                })

                if all_dates:
                    # 从后往前找第一个匹配的日期
                    # 方法：记录每个日期在原文中的位置，取位置最靠后的那个

                    # 先收集所有匹配的位置
                    date_positions = []
                    for date_info in all_dates:
                        date_str = date_info['date']
                        # 查找该日期在原文中的位置（取最后一个出现的位置）
                        pos = answer.rfind(date_str)
                        if pos != -1:
                            date_positions.append({
                                'date': date_str,
                                'position': pos
                            })

                    # 按位置从后往前排序（位置值越大，说明越靠后）
                    if date_positions:
                        date_positions.sort(key=lambda x: x['position'], reverse=True)
                        # 取位置最靠后的（第一个）
                        most_recent_date = date_positions[0]['date']
                        dates = [most_recent_date]
                        logger.debug(f"从文本末尾找到最近日期: {most_recent_date}")

        except Exception as e:
            logger.debug(f"提取日期时出错: {e}")

        return dates


class ExamNotesSearcher:
    """真题笔记检索器"""

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
        为知识点构建多个查询问题 - 优化版

        优化要点：
        1. 不限制首次出现，任何相关日期都返回
        2. 只提及包含笔记的日期，不提及不符合的日期
        3. 在回答最后用###框出所有符合的日期
        """

        # 基础指令 - 强调日期收集和格式化要求
        core_instruction = (
            "请查找所有包含该知识点的笔记日期，并遵守以下要求：\n"
            "1. 不限于首次出现，任何相关日期都收集\n"
            "2. 只返回包含笔记的日期，不提及不符合的日期\n"
            "3. 在回答最后用###号框出所有符合的日期\n\n"
            "日期定位方法：找到相关内容后，向上查找包含'重要：以下笔记的记录日期【'的行，提取【】内的8位数字。"
        )

        # 格式要求模板
        format_requirement = (
            "请按以下格式组织回答：\n"
            "1. 先分析内容\n"
            "2. 然后总结所有相关日期\n"
            "3. 最后用###号框出日期，例如：###20240501、20240627###\n\n"
            "注意：只列出确实包含该知识点的日期，不要列出没有相关内容的日期。"
        )

        # 合并指令
        combined_instruction = f"{core_instruction}\n\n{format_requirement}"

        base_queries = [
            # 方案1：全面收集日期，强调格式
            f"关于'{exam_point}'的笔记内容。{combined_instruction}请分析并返回所有包含该知识点的日期。",

            # 方案2：强调不限于首次出现
            f"查找'{exam_point}'相关的所有笔记。要求：不限于首次出现，所有包含该知识点的日期都要收集。"
            f"每个工作表的标题行为'重要：以下笔记的记录日期【YYYYMMDD】'。请在回答最后用###号框出所有日期。",

            # 方案3：明确排除不符合的日期
            f"搜索'{exam_point}'的知识点。重要要求："
            f"1. 收集所有相关日期，不限出现顺序\n"
            f"2. 只列出包含该知识点的日期，不列出没有相关内容的日期\n"
            f"3. 在结论中用###号框出所有日期，格式如###20240501、20240627###",

            # 方案4：结合科目特点，强调完整性
            f"考研{subject}知识点'{exam_point}'在哪些日期的工作表中有记录？"
            f"请收集所有相关日期（不限于首次出现），"
            f"在回答中只提及包含该知识点的日期，并在最后用###号框出这些日期。",
        ]

        # 针对不同科目的特定查询
        if subject == '政治':
            base_queries.extend([
                f"政治理论'{exam_point}'在哪些工作表中出现？请收集所有相关日期（包括多次出现的日期），"
                f"只返回确实包含该理论的工作表日期，并在回答末尾用###号框出所有日期，例如###20240501、20240627###。",

                f"查找关于'{exam_point}'的政治笔记。要求："
                f"1. 找出所有包含该知识点的日期\n"
                f"2. 不提及没有该知识点的日期\n"
                f"3. 在结论中明确用###框出所有日期\n"
                f"日期定位：标题行为'重要：以下笔记的记录日期【YYYYMMDD】'",
            ])

        elif subject == '408':
            base_queries.extend([
                f"计算机408知识点'{exam_point}'在哪些工作表中？请完整收集所有相关日期，"
                f"不限出现次数。在回答中只列出包含该知识点的日期，最后用###号框出所有日期。",

                f"搜索'{exam_point}'的算法/数据结构笔记。要求："
                f"收集所有日期，不限于首次出现；"
                f"只返回包含该知识点的日期；"
                f"在回答末尾用###框出所有日期，格式为###日期1、日期2、日期3###。",
            ])

        elif subject == '数学二':
            base_queries.extend([
                f"数学二考点'{exam_point}'在哪些日期的工作表中出现？"
                f"请收集所有相关日期（包括多次出现的），"
                f"在回答中只提及包含该考点的日期，并在最后用###号框出所有日期。",

                f"查找'{exam_point}'的数学笔记。要求："
                f"1. 找出所有相关日期，不限制出现次数\n"
                f"2. 只列出包含该知识点的日期\n"
                f"3. 在结论部分用###号框出所有日期\n"
                f"日期格式为8位数字，位于'重要：以下笔记的记录日期【'之后。",
            ])

        # 强化格式要求的查询
        enhanced_queries = [
            # 强调日期完整性
            f"请查找'{exam_point}'相关内容，并严格遵守以下要求："
            f"1. 收集所有相关日期，不限于首次出现\n"
            f"2. 只提及包含该知识点的日期，不提及不符合的日期\n"
            f"3. 在回答最后用###号框出所有日期，格式为###YYYYMMDD、YYYYMMDD、YYYYMMDD###\n\n"
            f"日期定位：向上查找'重要：以下笔记的记录日期【'，提取【】内的8位数字。",

            # 强调排除不符合的日期
            f"搜索'{exam_point}'。重要规则："
            f"1. 返回所有包含该知识点的日期\n"
            f"2. 不返回或提及没有该知识点的日期\n"
            f"3. 在回答末尾必须用###号框出所有日期\n\n"
            f"笔记格式：标题行为'重要：以下笔记的记录日期【20251208】'。",

            # 强调格式和完整性
            f"查找'{exam_point}'并提取所有相关的工作表日期。要求："
            f"1. 不限制首次出现，收集所有日期\n"
            f"2. 只列出确实包含该知识点的日期\n"
            f"3. 在结论中明确用###框出所有日期\n\n"
            f"日期提取规则：查找包含'重要：以下笔记的记录日期【'的行，提取【】内的8位数字。",

            # 提供示例格式
            f"查找'{exam_point}'相关笔记，提取工作表日期。要求："
            f"1. 收集所有相关日期，不限出现顺序\n"
            f"2. 只返回包含该知识点的日期\n"
            f"3. 在回答最后必须包含以下格式：'综上所述，符合关键词笔记的日期为###日期1、日期2、日期3###'\n\n"
            f"日期位于标题行中，格式为'重要：以下笔记的记录日期【20251208】'。",
        ]

        # 提供更明确的格式模板
        template_queries = [
            # 模板1：明确的格式要求
            f"搜索'{exam_point}'。请按以下模板回答：\n"
            f"[内容分析...]\n"
            f"综上所述，符合关键词笔记的日期为###20240501、20240627###\n\n"
            f"要求：1. 收集所有相关日期 2. 只提及包含的日期 3. 必须使用###框出日期",

            # 模板2：强调排除
            f"查找'{exam_point}'。要求：\n"
            f"1. 找出所有包含该知识点的日期（不限首次）\n"
            f"2. 在回答中绝对不提及没有该知识点的日期\n"
            f"3. 在结尾必须包含：'###日期1、日期2###'格式\n\n"
            f"日期定位：标题行包含'重要：以下笔记的记录日期【'",

            # 模板3：简化的指令
            f"找到'{exam_point}'的所有出现日期。\n"
            f"要求：所有日期都收集，只列包含的，最后用###框起来。\n"
            f"例如：###20240501、20240627###",
        ]

        # 合并所有查询
        all_queries = base_queries + enhanced_queries + template_queries

        return all_queries

    def search_for_exam_point(self, exam_point: str, subject: str, max_queries: int = 3) -> List[Dict]:
        """
        搜索单个真题知识点的相关笔记 - 增加日期提取

        Returns:
            搜索结果列表: [{
                'exam_point': 真题知识点,
                'subject': 科目,
                'query': 查询问题,
                'answer': API回答,
                'confidence': 置信度,
                'sources': 源文档列表,
                'sheet_dates': [],  # 新增：提取到的工作表日期
                'date_extraction_method': str  # 新增：日期提取方式
            }]
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

                    # 提取工作表日期
                    sheet_dates = []
                    date_extraction_method = "unknown"

                    # 方法1：从回答文本中提取
                    dates_from_answer = self.kb.extract_sheet_dates_from_answer(parsed_result['answer'])
                    if dates_from_answer:
                        sheet_dates.extend(dates_from_answer)
                        date_extraction_method = "from_answer"

                    # 去重和排序
                    sheet_dates = sorted(list(set(sheet_dates)))

                    result_entry = {
                        'exam_point': exam_point,
                        'subject': subject,
                        'query': query,
                        'answer': parsed_result['answer'][:500],  # 截断
                        'clean_answer': parsed_result.get('clean_answer', '')[:500],
                        'confidence': parsed_result['confidence'],
                        'sources': sources_info,
                        'full_answer': parsed_result['answer'],
                        'sheet_dates': sheet_dates,  # 新增：工作表日期
                        'date_extraction_method': date_extraction_method,  # 新增：提取方式
                        'date_count': len(sheet_dates)  # 新增：日期数量
                    }

                    results.append(result_entry)

                    # 日志中显示日期信息
                    if sheet_dates:
                        logger.debug(f"  找到 {len(sheet_dates)} 个相关工作表日期: {', '.join(sheet_dates)}")
                    else:
                        logger.debug(f"  未提取到工作表日期信息")

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
                        '置信度': result['confidence']
                    }

                    # 源文档信息
                    for i, source in enumerate(result['sources'][:3]):  # 最多3个源
                        row[f'源文档{i + 1}_标题'] = source.get('title', '')
                        row[f'源文档{i + 1}_分数'] = source.get('score', 0)
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
    print("🧪 笔记知识库综合测试")
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
        print(analysis_df[['exam_point', 'found_count', 'avg_confidence']].to_string(index=False))

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
    print("🚀 快速测试模式")

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
                if meta['title']:
                    sources.append(f"{meta['title']}({meta['score']:.2f})")

            if sources:
                print(f"  相关源文档: {', '.join(sources)}")
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
    print("📅 测试日期提取功能")
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
        ("定积分计算", "数学二")
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

                # 显示回答中的日期线索
                if result['answer']:
                    # 查找可能的日期模式
                    date_patterns = re.findall(r'\d{8}', result['answer'][:300])
                    if date_patterns:
                        print(f"  回答中的数字模式: {', '.join(date_patterns)}")

        time.sleep(1)  # 避免API限流

    print(f"\n{'=' * 60}")
    print("📊 总结：")
    print("修改后的查询会明确要求知识库提供工作表日期信息")
    print("如果知识库按格式提供，我们就可以直接定位到具体的sheet")


def main():
    """主函数"""
    print("""
    ════════════════════════════════════════════════════
        考研笔记知识库检索测试系统 (日期增强版)
        版本: 1.1
        功能: 测试秘塔搜索API，提取相关笔记的工作表日期
    ════════════════════════════════════════════════════
    """)

    print("请选择测试模式:")
    print("1. 🔌 API连接测试")
    print("2. 🚀 快速功能测试")
    print("3. 📚 综合科目测试")
    print("4. 🎯 自定义查询测试")
    print("5. 📅 测试日期提取功能 (新增)")

    choice = input("\n请输入选项 (1-5): ").strip()

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
                            print(f"  {i + 1}. {meta['title']} (相关性: {meta['score']:.2f})")
                            if meta['content']:
                                print(f"     内容: {meta['content'][:100]}...")
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
    else:
        print("无效选项")


if __name__ == "__main__":
    main()
