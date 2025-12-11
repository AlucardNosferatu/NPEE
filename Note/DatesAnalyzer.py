import heapq
import json
import math
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional

import pandas as pd


class IncrementalDateAnalyzer:
    """
    增量日期分析器 - 逐个处理RAG结果，逐步更新统计
    适合处理大量数据，避免一次性内存占用过高
    """

    def __init__(self,
                 top_k: int = 100,
                 memory_limit: Optional[int] = None,
                 save_path: Optional[str] = None):
        """
        初始化增量分析器

        Args:
            top_k: 保留排名前K的日期
            memory_limit: 内存限制，超过时触发压缩
            save_path: 定期保存路径
        """
        # 核心数据结构
        self.date_stats = defaultdict(lambda: {
            'frequency': 0,  # 总出现次数
            'question_ids': set(),  # 涉及的问题ID
            'keywords': set(),  # 涉及的关键词
            'subjects': set(),  # 涉及的科目
            'confidence_sum': 0.0,  # 置信度总和
            'confidence_count': 0,  # 置信度计数
            'keyword_details': defaultdict(int),  # 关键词出现次数
            'last_updated': '',  # 最后更新时间
        })

        # 全局统计
        self.global_stats = {
            'total_questions': 0,
            'total_keywords': 0,
            'total_dates_found': 0,
            'processed_questions': 0,
            'failed_keywords': 0,
            'subjects_distribution': Counter(),
            'top_keywords': Counter(),
        }

        # 配置参数
        self.top_k = top_k
        self.memory_limit = memory_limit
        self.save_path = save_path

        # 缓存结构，用于快速排序
        self._score_cache = {}  # date -> 计算过的得分
        self._sorted_dates = []  # 缓存的排序结果

        # 历史记录
        self.history = []

    def update(self, rag_item: Dict) -> None:
        """
        处理单个RAG返回结果，更新内部统计

        Args:
            rag_item: 单个问题的RAG结果
        """
        # 记录更新历史
        update_id = f"update_{len(self.history)}_{rag_item.get('timestamp', 'unknown')}"
        self.history.append({
            'update_id': update_id,
            'question_info': rag_item.get('question_info'),
            'timestamp': rag_item.get('timestamp')
        })

        # 提取问题信息
        question_info = rag_item.get('question_info', {})
        question_id = self._generate_question_id(question_info)

        # 更新全局统计
        self.global_stats['total_questions'] += 1
        self.global_stats['processed_questions'] += 1
        self.global_stats['subjects_distribution'][question_info.get('subject', 'unknown')] += 1

        # 处理关键词结果
        for keyword_result in rag_item.get('keywords_results', []):
            keyword = keyword_result.get('keyword', '')
            status = keyword_result.get('status', '')

            # 更新全局关键词统计
            if status == 'success':
                self.global_stats['total_keywords'] += 1
                self.global_stats['top_keywords'][keyword] += 1
            else:
                self.global_stats['failed_keywords'] += 1
                continue  # 跳过失败的关键词

            # 处理该关键词找到的所有日期
            for date in keyword_result.get('dates_found', []):
                self._update_date_stat(
                    date=date,
                    question_id=question_id,
                    keyword=keyword,
                    confidence=keyword_result.get('confidence', 0.5),
                    subject=question_info.get('subject', 'unknown')
                )
                self.global_stats['total_dates_found'] += 1

        # 触发可能的优化
        self._maybe_optimize()

    def _update_date_stat(self, date: str, question_id: str,
                          keyword: str, confidence: float, subject: str) -> None:
        """更新单个日期的统计信息"""
        stats = self.date_stats[date]

        # 更新频率
        stats['frequency'] += 1

        # 更新问题集合
        stats['question_ids'].add(question_id)

        # 更新关键词集合
        stats['keywords'].add(keyword)
        stats['keyword_details'][keyword] += 1

        # 更新科目集合
        stats['subjects'].add(subject)

        # 更新置信度统计
        stats['confidence_sum'] += confidence
        stats['confidence_count'] += 1

        # 更新时间戳
        stats['last_updated'] = pd.Timestamp.now().isoformat()

        # 清除该日期的缓存得分
        if date in self._score_cache:
            del self._score_cache[date]

    @staticmethod
    def _generate_question_id(question_info: Dict) -> str:
        """生成唯一问题ID"""
        subject = question_info.get('subject', 'unknown')
        qid = question_info.get('qid', 'unknown')
        year = question_info.get('year', 'unknown')
        return f"{year}_{subject}_{qid}"

    def _maybe_optimize(self) -> None:
        """根据条件触发优化"""
        # 检查内存限制
        if self.memory_limit and len(self.date_stats) > self.memory_limit:
            self._compress_stats()

        # 每处理100个问题重新计算排序
        if self.global_stats['processed_questions'] % 100 == 0:
            self._recalculate_scores()

            # 定期保存
            if self.save_path:
                self.save_state(f"{self.save_path}_checkpoint_{self.global_stats['processed_questions']}.json")

    def _compress_stats(self) -> None:
        """压缩统计信息，移除低频日期"""
        if len(self.date_stats) <= self.top_k * 2:
            return

        # 计算所有日期的分数
        scores = {}
        for date, stats in self.date_stats.items():
            scores[date] = self._calculate_date_score(date, stats, update_cache=False)

        # 保留前N个
        top_dates = heapq.nlargest(self.top_k * 2, scores.items(), key=lambda x: x[1])
        top_dates_set = {date for date, _ in top_dates}

        # 移除低频日期
        dates_to_remove = [date for date in self.date_stats.keys() if date not in top_dates_set]
        for date in dates_to_remove:
            del self.date_stats[date]
            if date in self._score_cache:
                del self._score_cache[date]

        print(f"压缩完成: 从{len(dates_to_remove) + len(top_dates_set)}个日期压缩到{len(top_dates_set)}个")

    def _recalculate_scores(self) -> None:
        """重新计算所有日期的得分并排序"""
        self._score_cache.clear()
        self._sorted_dates = self.get_sorted_dates(force_recalculate=True)

    def _calculate_date_score(self, date: str, stats: Dict, update_cache: bool = True) -> float:
        """
        计算单个日期的综合得分

        得分 = 频率得分 × 问题覆盖率得分 × 关键词广度得分 × 置信度得分
        """
        # 检查缓存
        if date in self._score_cache and update_cache:
            return self._score_cache[date]

        # 频率得分 (0-1)
        freq_score = min(1.0, stats['frequency'] / 50)  # 假设最大频率50

        # 问题覆盖率得分
        question_coverage = len(stats['question_ids']) / max(1, self.global_stats['total_questions'])

        # 关键词广度得分
        keyword_breadth = min(1.0, len(stats['keywords']) / 20)  # 假设最大关键词20

        # 平均置信度
        avg_confidence = (stats['confidence_sum'] / stats['confidence_count']) if stats['confidence_count'] > 0 else 0.5

        # 科目多样性加分
        subject_diversity = min(1.0, len(stats['subjects']) / 3)  # 涉及多个科目加分

        # 综合得分计算（加权几何平均）
        weights = {
            'frequency': 0.35,
            'question_coverage': 0.25,
            'keyword_breadth': 0.20,
            'confidence': 0.15,
            'subject_diversity': 0.05
        }

        # 避免零值
        freq_score = max(freq_score, 0.01)
        question_coverage = max(question_coverage, 0.01)
        keyword_breadth = max(keyword_breadth, 0.01)
        avg_confidence = max(avg_confidence, 0.01)
        subject_diversity = max(subject_diversity, 0.01)

        # 计算加权几何平均
        log_score = (
                weights['frequency'] * math.log(freq_score) +
                weights['question_coverage'] * math.log(question_coverage) +
                weights['keyword_breadth'] * math.log(keyword_breadth) +
                weights['confidence'] * math.log(avg_confidence) +
                weights['subject_diversity'] * math.log(subject_diversity)
        )

        score = math.exp(log_score)

        # 应用非线性变换增强区分度
        score = self._apply_nonlinear_transform(score)

        if update_cache:
            self._score_cache[date] = score

        return score

    @staticmethod
    def _apply_nonlinear_transform(score: float) -> float:
        """应用非线性变换增强得分区分度"""
        # Sigmoid-like transformation centered at 0.5
        return 1 / (1 + math.exp(-10 * (score - 0.5)))

    def get_sorted_dates(self, force_recalculate: bool = False, top_n: Optional[int] = None) -> List[Tuple[str, Dict]]:
        """
        获取排序后的日期列表

        Args:
            force_recalculate: 强制重新计算
            top_n: 只返回前N个

        Returns:
            排序后的(日期, 统计信息)列表
        """
        if force_recalculate or not self._sorted_dates:
            # 计算所有日期的得分
            scored_dates = []
            for date, stats in self.date_stats.items():
                score = self._calculate_date_score(date, stats)
                scored_dates.append((date, stats, score))

            # 按得分排序
            scored_dates.sort(key=lambda x: x[2], reverse=True)
            self._sorted_dates = scored_dates

        # 截取前N个
        result = self._sorted_dates
        if top_n is not None:
            result = result[:top_n]

        # 转换为更友好的格式
        return [(date, {
            'score': score,
            'frequency': stats['frequency'],
            'question_count': len(stats['question_ids']),
            'keyword_count': len(stats['keywords']),
            'subject_count': len(stats['subjects']),
            'avg_confidence': stats['confidence_sum'] / max(1, stats['confidence_count']),
            'subjects': list(stats['subjects']),
            'top_keywords': self._get_top_keywords(stats['keyword_details'], 5),
            'last_updated': stats['last_updated']
        }) for date, stats, score in result]

    @staticmethod
    def _get_top_keywords(keyword_details: Dict[str, int], top_n: int):
        """获取前N个关键词"""
        return sorted(keyword_details.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_top_dates_df(self, top_n: Optional[int] = None) -> pd.DataFrame:
        """获取前N个日期的DataFrame"""
        if top_n is None:
            top_n = self.top_k

        sorted_dates = self.get_sorted_dates(top_n=top_n)

        data = []
        for rank, (date, stats) in enumerate(sorted_dates, 1):
            data.append({
                '排名': rank,
                '日期': date,
                '综合得分': round(stats['score'], 4),
                '总出现次数': stats['frequency'],
                '涉及问题数': stats['question_count'],
                '涉及关键词数': stats['keyword_count'],
                '涉及科目数': stats['subject_count'],
                '平均置信度': round(stats['avg_confidence'], 3),
                '科目': ', '.join(stats['subjects']),
                '高频关键词': ', '.join([f"{kw}({cnt})" for kw, cnt in stats['top_keywords']]),
                '最后更新': stats['last_updated']
            })

        return pd.DataFrame(data)

    def get_importance_levels(self) -> Dict[str, List[str]]:
        """按重要性等级分组日期"""
        sorted_dates = self.get_sorted_dates()
        if not sorted_dates:
            return {}

        # 确定分位数
        total = len(sorted_dates)
        top_10 = int(total * 0.1)
        top_30 = int(total * 0.3)
        top_60 = int(total * 0.6)

        return {
            '极高重要性': [date for date, _, _ in sorted_dates[:top_10]],
            '高重要性': [date for date, _, _ in sorted_dates[top_10:top_30]],
            '中等重要性': [date for date, _, _ in sorted_dates[top_30:top_60]],
            '低重要性': [date for date, _, _ in sorted_dates[top_60:]]
        }

    def calculate_coverage(self, selected_dates: List[str]) -> Dict[str, float]:
        """
        计算选定日期的覆盖率

        Returns:
            各种覆盖率指标
        """
        # 收集所有问题和关键词
        all_questions = set()
        all_keywords = set()

        for stats in self.date_stats.values():
            all_questions.update(stats['question_ids'])
            all_keywords.update(stats['keywords'])

        # 计算覆盖情况
        covered_questions = set()
        covered_keywords = set()

        for date in selected_dates:
            if date in self.date_stats:
                stats = self.date_stats[date]
                covered_questions.update(stats['question_ids'])
                covered_keywords.update(stats['keywords'])

        total_questions = len(all_questions)
        total_keywords = len(all_keywords)

        return {
            '问题覆盖率': len(covered_questions) / total_questions if total_questions > 0 else 0,
            '关键词覆盖率': len(covered_keywords) / total_keywords if total_keywords > 0 else 0,
            '覆盖问题数': len(covered_questions),
            '覆盖关键词数': len(covered_keywords),
            '总问题数': total_questions,
            '总关键词数': total_keywords
        }

    def save_state(self, filepath: str) -> None:
        """保存当前状态到文件"""
        state = {
            'date_stats': {
                date: {
                    'frequency': stats['frequency'],
                    'question_ids': list(stats['question_ids']),
                    'keywords': list(stats['keywords']),
                    'subjects': list(stats['subjects']),
                    'confidence_sum': stats['confidence_sum'],
                    'confidence_count': stats['confidence_count'],
                    'keyword_details': dict(stats['keyword_details']),
                    'last_updated': stats['last_updated']
                }
                for date, stats in self.date_stats.items()
            },
            'global_stats': dict(self.global_stats),
            'history': self.history,
            'config': {
                'top_k': self.top_k,
                'memory_limit': self.memory_limit,
                'processed_count': self.global_stats['processed_questions']
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        print(f"状态已保存到: {filepath}")

    def load_state(self, filepath: str) -> None:
        """从文件加载状态"""
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)

        # 恢复date_stats
        self.date_stats.clear()
        for date, stats_dict in state['date_stats'].items():
            self.date_stats[date] = {
                'frequency': stats_dict['frequency'],
                'question_ids': set(stats_dict['question_ids']),
                'keywords': set(stats_dict['keywords']),
                'subjects': set(stats_dict['subjects']),
                'confidence_sum': stats_dict['confidence_sum'],
                'confidence_count': stats_dict['confidence_count'],
                'keyword_details': defaultdict(int, stats_dict['keyword_details']),
                'last_updated': stats_dict['last_updated']
            }

        # 恢复全局统计
        self.global_stats.update(state['global_stats'])

        # 恢复历史
        self.history = state['history']

        # 清除缓存
        self._score_cache.clear()
        self._sorted_dates = []

        print(f"状态已从 {filepath} 加载，已处理 {self.global_stats['processed_questions']} 个问题")

    def get_stats_summary(self) -> Dict:
        """获取统计摘要"""
        importance_levels = self.get_importance_levels()
        coverage_stats = self.calculate_coverage([])

        return {
            '处理统计': {
                '已处理问题数': self.global_stats['processed_questions'],
                '发现的日期数': len(self.date_stats),
                '总关键词数': self.global_stats['total_keywords'],
                '失败关键词数': self.global_stats['failed_keywords'],
                '科目分布': dict(self.global_stats['subjects_distribution'])
            },
            '重要性分布': {
                level: len(dates) for level, dates in importance_levels.items()
            },
            '覆盖率统计': coverage_stats,
            '高频关键词': self.global_stats['top_keywords'].most_common(10)
        }
