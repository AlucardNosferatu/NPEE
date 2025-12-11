"""
考点日期定位接口函数
功能：为真题检索引擎提供考点对应笔记日期的定位服务
"""
import datetime
import glob
import json
import os
import time
from collections import defaultdict, Counter
from typing import Dict, List

from DoN import ExamNotesSearcher, ST_ID, AK, NotesKnowledgeBase, logger

"""
考点日期定位接口函数
功能：为真题检索引擎提供考点对应笔记日期的定位服务
"""


def locate_exam_point_dates(
        exam_point: str,
        subject: str,
        knowledge_base: NotesKnowledgeBase = None,
        searcher: ExamNotesSearcher = None,
        max_queries: int = 2,
        return_objects: bool = True
) -> Dict:
    """
    定位考点对应的笔记日期 - 核心接口函数

    Args:
        exam_point: 真题考点（如"矛盾的普遍性和特殊性"）
        subject: 科目（"政治"/"408"/"数学二"）
        knowledge_base: 可选，已初始化的知识库对象。如果为None，则新建
        searcher: 可选，已初始化的检索器对象。如果为None，则新建
        max_queries: 最大查询数（默认2，平衡准确性和效率）
        return_objects: 是否返回使用的对象以便复用（默认True）

    Returns:
        字典格式的结果:
        {
            "status": "success"/"partial"/"error",
            "exam_point": "考点名称",
            "subject": "科目",
            "dates_found": ["20251208", "20251209", ...],
            "date_count": 3,
            "confidence": 0.85,  # 整体置信度（0-1）
            "details": [  # 详细信息
                {
                    "query": "查询问题",
                    "answer_snippet": "回答摘要...",
                    "confidence": 0.9,
                    "sources_count": 2,
                    "dates": ["20251208"]
                }
            ],
            "statistics": {
                "total_queries": 2,
                "successful_queries": 2,
                "response_time": 2.5
            },
            "timestamp": "2024-01-15 10:30:00",
            "knowledge_base": <NotesKnowledgeBase object>,  # 可选
            "searcher": <ExamNotesSearcher object>          # 可选
        }
    """

    start_time = time.time()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 初始化对象（如果未提供）
    if knowledge_base is None:
        knowledge_base = NotesKnowledgeBase(api_key=AK, search_topic_id=ST_ID)

    if searcher is None:
        searcher = ExamNotesSearcher(knowledge_base=knowledge_base)

    try:
        # 执行搜索
        logger.info(f"📅 开始定位考点日期: {exam_point} ({subject})")
        search_results = searcher.search_for_exam_point(
            exam_point=exam_point,
            subject=subject,
            max_queries=max_queries
        )

        response_time = round(time.time() - start_time, 2)

        # 分析结果
        if not search_results:
            return {
                "status": "error",
                "exam_point": exam_point,
                "subject": subject,
                "message": "未找到相关笔记",
                "dates_found": [],
                "date_count": 0,
                "confidence": 0.0,
                "details": [],
                "statistics": {
                    "total_queries": 0,
                    "successful_queries": 0,
                    "response_time": response_time
                },
                "timestamp": timestamp,
                **({"knowledge_base": knowledge_base, "searcher": searcher} if return_objects else {})
            }

        # 提取并合并所有日期
        all_dates = []
        details = []
        total_confidence = 0

        for result in search_results:
            dates = result.get('sheet_dates', [])
            all_dates.extend(dates)

            detail_entry = {
                "query": result['query'][:100] + "..." if len(result['query']) > 100 else result['query'],
                "answer_snippet": result.get('clean_answer', result['answer'][:200])[:200] + "..."
                if len(result.get('clean_answer', result['answer'])) > 200
                else result.get('clean_answer', result['answer'][:200]),
                "confidence": round(result['confidence'], 3),
                "sources_count": len(result['sources']),
                "dates": dates,
                "date_extraction_method": result.get('date_extraction_method', 'unknown')
            }
            details.append(detail_entry)

            total_confidence += result['confidence']

        # 去重和排序日期
        unique_dates = sorted(list(set(all_dates)))

        # 计算整体置信度
        avg_confidence = round(total_confidence / len(search_results), 3) if search_results else 0

        # 确定状态
        if unique_dates:
            status = "success" if avg_confidence > 0.6 else "partial"
        else:
            status = "partial" if search_results else "error"

        result_data = {
            "status": status,
            "exam_point": exam_point,
            "subject": subject,
            "dates_found": unique_dates,
            "date_count": len(unique_dates),
            "confidence": avg_confidence,
            "details": details,
            "statistics": {
                "total_queries": len(search_results),
                "successful_queries": len([r for r in search_results if r.get('confidence', 0) > 0]),
                "response_time": response_time
            },
            "timestamp": timestamp,
            **({"knowledge_base": knowledge_base, "searcher": searcher} if return_objects else {})
        }

        logger.info(f"✅ 定位完成: 找到 {len(unique_dates)} 个日期，置信度 {avg_confidence}")
        return result_data

    except Exception as e:
        logger.error(f"定位考点日期失败: {e}")
        return {
            "status": "error",
            "exam_point": exam_point,
            "subject": subject,
            "message": f"定位失败: {str(e)}",
            "dates_found": [],
            "date_count": 0,
            "confidence": 0.0,
            "details": [],
            "statistics": {
                "total_queries": 0,
                "successful_queries": 0,
                "response_time": round(time.time() - start_time, 2)
            },
            "timestamp": timestamp,
            **({"knowledge_base": knowledge_base, "searcher": searcher} if return_objects else {})
        }


def batch_locate_dates(
        exam_points: List[Dict],
        knowledge_base: NotesKnowledgeBase = None,
        searcher: ExamNotesSearcher = None,
        max_queries_per_point: int = 2,
        return_objects: bool = True
) -> Dict:
    """
    批量定位多个考点的笔记日期

    Args:
        exam_points: 考点列表，格式: [{"exam_point": "考点", "subject": "科目"}, ...]
        knowledge_base: 可选，已初始化的知识库对象
        searcher: 可选，已初始化的检索器对象
        max_queries_per_point: 每个考点的最大查询数
        return_objects: 是否返回使用的对象

    Returns:
        批量定位结果:
        {
            "status": "complete"/"partial",
            "total_points": 10,
            "successful_points": 8,
            "failed_points": 2,
            "results": [
                {每个考点的定位结果...},
                ...
            ],
            "summary": {
                "total_dates_found": 25,
                "avg_confidence": 0.78,
                "date_distribution": {"政治": 10, "408": 8, "数学二": 7}
            },
            "knowledge_base": <对象>,  # 可选
            "searcher": <对象>         # 可选
        }
    """

    # 初始化对象（如果未提供）
    if knowledge_base is None:
        knowledge_base = NotesKnowledgeBase(api_key=AK, search_topic_id=ST_ID)

    if searcher is None:
        searcher = ExamNotesSearcher(knowledge_base=knowledge_base)

    start_time = time.time()
    results = []
    successful_count = 0
    failed_count = 0
    all_dates = []
    total_confidence = 0
    date_distribution = defaultdict(int)

    logger.info(f"🚀 开始批量定位 {len(exam_points)} 个考点")

    for i, point in enumerate(exam_points):
        exam_point = point.get('exam_point', '')
        subject = point.get('subject', '')

        if not exam_point or not subject:
            logger.warning(f"跳过无效考点数据: {point}")
            continue

        logger.info(f"进度 [{i + 1}/{len(exam_points)}]: {exam_point} ({subject})")

        # 定位单个考点
        result = locate_exam_point_dates(
            exam_point=exam_point,
            subject=subject,
            knowledge_base=knowledge_base,
            searcher=searcher,
            max_queries=max_queries_per_point,
            return_objects=False  # 不重复返回对象
        )

        results.append(result)

        # 统计
        if result['status'] in ['success', 'partial'] and result['date_count'] > 0:
            successful_count += 1
            all_dates.extend(result['dates_found'])
            total_confidence += result['confidence']

            # 统计科目分布
            date_distribution[subject] += result['date_count']
        else:
            failed_count += 1

        # 避免API限制
        if i < len(exam_points) - 1:
            time.sleep(0.5)

    # 生成汇总信息
    total_time = round(time.time() - start_time, 2)

    summary_data = {
        "status": "complete" if successful_count > 0 else "error",
        "total_points": len(exam_points),
        "successful_points": successful_count,
        "failed_points": failed_count,
        "results": results,
        "summary": {
            "total_dates_found": len(set(all_dates)),
            "avg_confidence": round(total_confidence / successful_count, 3) if successful_count > 0 else 0,
            "date_distribution": dict(date_distribution),
            "total_time_seconds": total_time,
            "avg_time_per_point": round(total_time / len(exam_points), 2) if exam_points else 0
        },
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **({"knowledge_base": knowledge_base, "searcher": searcher} if return_objects else {})
    }

    logger.info(f"🎉 批量定位完成: 成功 {successful_count}/{len(exam_points)}，找到 {len(set(all_dates))} 个日期")
    return summary_data


"""
关键词日期定位接口
功能：处理真题分析模块的JSON格式，定位关键词对应的笔记日期
"""


def locate_dates_by_keywords(
        question_data: Dict,
        knowledge_base: NotesKnowledgeBase = None,
        searcher: ExamNotesSearcher = None,
        max_queries_per_keyword: int = 2,
        return_objects: bool = True
) -> Dict:
    """
    基于关键词列表定位笔记日期

    Args:
        question_data: 真题分析模块的JSON数据，格式:
            {
                "year": 2024,
                "subject": "数学二",
                "qid": 16,
                "keywords": ["向量组", "线性相关", "线性无关", ...]
            }
        knowledge_base: 可选，已初始化的知识库对象
        searcher: 可选，已初始化的检索器对象
        max_queries_per_keyword: 每个关键词的最大查询数
        return_objects: 是否返回使用的对象以便复用

    Returns:
        字典格式的结果:
        {
            "question_info": {
                "year": 2024,
                "subject": "数学二",
                "qid": 16,
                "total_keywords": 8
            },
            "status": "success"/"partial"/"error",
            "keywords_results": [
                {
                    "keyword": "向量组",
                    "status": "success",
                    "dates_found": ["20251208", "20251209"],
                    "date_count": 2,
                    "confidence": 0.85,
                    "primary_date": "20251208"  # 置信度最高的日期
                },
                ...
            ],
            "summary": {
                "total_dates_found": 15,
                "unique_dates": ["20251208", "20251209", ...],
                "unique_date_count": 5,
                "avg_confidence": 0.78,
                "date_frequency": {
                    "20251208": 4,  # 日期: 出现次数
                    "20251209": 3,
                    ...
                },
                "most_frequent_dates": [
                    {"date": "20251208", "frequency": 4, "keywords": ["向量组", "线性相关", ...]},
                    ...
                ],
                "best_keywords": [
                    {"keyword": "向量组", "date_count": 3, "confidence": 0.9},
                    ...
                ]
            },
            "recommendations": {
                "primary_review_date": "20251208",  # 主要复习日期
                "supporting_dates": ["20251209", "20251210"],  # 补充复习日期
                "focus_keywords": ["向量组", "线性相关"],  # 重点关注的关键词
                "review_priority": "high"  # 复习优先级: high/medium/low
            },
            "statistics": {
                "total_queries": 16,
                "successful_queries": 14,
                "response_time": 8.5
            },
            "timestamp": "2024-01-15 10:30:00",
            "knowledge_base": <对象>,  # 可选
            "searcher": <对象>         # 可选
        }
    """

    start_time = time.time()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 提取问题信息
    year = question_data.get("year", 0)
    subject = question_data.get("subject", "")
    qid = question_data.get("qid", 0)
    keywords = question_data.get("keywords", [])

    if not subject or not keywords:
        return {
            "question_info": {
                "year": year,
                "subject": subject,
                "qid": qid,
                "total_keywords": len(keywords)
            },
            "status": "error",
            "message": "缺少科目或关键词信息",
            "keywords_results": [],
            "summary": {},
            "recommendations": {},
            "statistics": {
                "total_queries": 0,
                "successful_queries": 0,
                "response_time": 0
            },
            "timestamp": timestamp
        }

    # 初始化对象（如果未提供）
    if knowledge_base is None:
        knowledge_base = NotesKnowledgeBase(api_key=AK, search_topic_id=ST_ID)

    if searcher is None:
        searcher = ExamNotesSearcher(knowledge_base=knowledge_base)

    logger.info(f"🔍 开始处理真题 {year}-{subject}-{qid}: {len(keywords)} 个关键词")

    # 准备批量处理的考点数据
    exam_points = []
    for keyword in keywords:
        exam_points.append({
            "exam_point": keyword,
            "subject": subject
        })

    # 执行批量定位
    try:
        batch_result = batch_locate_dates(
            exam_points=exam_points,
            knowledge_base=knowledge_base,
            searcher=searcher,
            max_queries_per_point=max_queries_per_keyword,
            return_objects=False  # 不在每个结果中返回对象
        )

        response_time = round(time.time() - start_time, 2)

        # 处理每个关键词的结果
        keywords_results = []
        all_dates = []
        date_keyword_map = defaultdict(list)  # 日期 -> 关键词列表
        keyword_date_map = defaultdict(list)  # 关键词 -> 日期列表

        for i, keyword in enumerate(keywords):
            if i < len(batch_result["results"]):
                result = batch_result["results"][i]
            else:
                result = {
                    "status": "error",
                    "exam_point": keyword,
                    "subject": subject,
                    "dates_found": [],
                    "date_count": 0,
                    "confidence": 0.0,
                    "details": []
                }

            keyword_result = {
                "keyword": keyword,
                "status": result["status"],
                "dates_found": result["dates_found"],
                "date_count": result["date_count"],
                "confidence": result["confidence"],
                "details_count": len(result.get("details", []))
            }

            # 如果有找到日期，计算主要日期（置信度最高的）
            if result["dates_found"] and result["confidence"] > 0:
                # 如果有多个日期，取第一个（通常是最相关的）
                keyword_result["primary_date"] = result["dates_found"][0]

                # 更新映射关系
                for date in result["dates_found"]:
                    all_dates.append(date)
                    date_keyword_map[date].append({
                        "keyword": keyword,
                        "confidence": result["confidence"]
                    })
                    keyword_date_map[keyword].append(date)
            else:
                keyword_result["primary_date"] = None

            keywords_results.append(keyword_result)

        # 统计汇总信息
        unique_dates = sorted(list(set(all_dates)))
        date_frequency = Counter(all_dates)

        # 计算平均置信度（仅统计有结果的关键词）
        confidences = [r["confidence"] for r in keywords_results if r["confidence"] > 0]
        avg_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0

        # 找到最高频的日期
        most_frequent_dates = []
        for date, freq in date_frequency.most_common(5):  # 取前5个最高频日期
            keywords_for_date = [item["keyword"] for item in date_keyword_map[date]]
            most_frequent_dates.append({
                "date": date,
                "frequency": freq,
                "keywords": keywords_for_date[:5]  # 最多显示5个关键词
            })

        # 找到最佳关键词（找到日期最多且置信度高的）
        best_keywords = []
        for result in keywords_results:
            if result["date_count"] > 0:
                best_keywords.append({
                    "keyword": result["keyword"],
                    "date_count": result["date_count"],
                    "confidence": result["confidence"]
                })

        # 按日期数量和置信度排序
        best_keywords.sort(key=lambda x: (x["date_count"], x["confidence"]), reverse=True)
        best_keywords = best_keywords[:5]  # 取前5个最佳关键词

        # 生成复习建议
        recommendations = generate_review_recommendations(
            most_frequent_dates,
            best_keywords,
            avg_confidence
        )

        # 构建最终结果
        final_result = {
            "question_info": {
                "year": year,
                "subject": subject,
                "qid": qid,
                "total_keywords": len(keywords),
                "keywords_list": keywords
            },
            "status": batch_result["status"],
            "keywords_results": keywords_results,
            "summary": {
                "total_dates_found": len(all_dates),
                "unique_dates": unique_dates,
                "unique_date_count": len(unique_dates),
                "avg_confidence": avg_confidence,
                "date_frequency": dict(date_frequency),
                "most_frequent_dates": most_frequent_dates,
                "best_keywords": best_keywords,
                "success_rate": batch_result["successful_points"] / batch_result["total_points"]
                if batch_result["total_points"] > 0 else 0
            },
            "recommendations": recommendations,
            "statistics": {
                "total_queries": batch_result["summary"].get("total_queries", 0),
                "successful_queries": batch_result["summary"].get("successful_queries", 0),
                "response_time": response_time,
                "batch_summary": {
                    "total_points": batch_result["total_points"],
                    "successful_points": batch_result["successful_points"],
                    "failed_points": batch_result["failed_points"]
                }
            },
            "timestamp": timestamp,
            **({"knowledge_base": knowledge_base, "searcher": searcher} if return_objects else {})
        }

        logger.info(f"✅ 关键词定位完成: 找到 {len(unique_dates)} 个唯一日期，平均置信度 {avg_confidence}")
        return final_result

    except Exception as e:
        logger.error(f"关键词日期定位失败: {e}")
        return {
            "question_info": {
                "year": year,
                "subject": subject,
                "qid": qid,
                "total_keywords": len(keywords)
            },
            "status": "error",
            "message": f"处理失败: {str(e)}",
            "keywords_results": [],
            "summary": {},
            "recommendations": {},
            "statistics": {
                "total_queries": 0,
                "successful_queries": 0,
                "response_time": round(time.time() - start_time, 2)
            },
            "timestamp": timestamp,
            **({"knowledge_base": knowledge_base, "searcher": searcher} if return_objects else {})
        }


def generate_review_recommendations(
        most_frequent_dates: List[Dict],
        best_keywords: List[Dict],
        avg_confidence: float
) -> Dict:
    """
    生成复习建议

    Args:
        most_frequent_dates: 最高频日期列表
        best_keywords: 最佳关键词列表
        avg_confidence: 平均置信度

    Returns:
        复习建议字典
    """
    if not most_frequent_dates:
        return {
            "primary_review_date": None,
            "supporting_dates": [],
            "focus_keywords": [],
            "review_priority": "low",
            "confidence_level": "low",
            "notes": "未找到明确的复习日期建议"
        }

    # 主要复习日期（出现频率最高的）
    primary_date = most_frequent_dates[0]["date"] if most_frequent_dates else None

    # 补充复习日期（其他高频日期）
    supporting_dates = [d["date"] for d in most_frequent_dates[1:4]] if len(most_frequent_dates) > 1 else []

    # 重点关注的关键词（找到日期最多且置信度高的）
    focus_keywords = [k["keyword"] for k in best_keywords[:3]] if best_keywords else []

    # 确定复习优先级
    if avg_confidence >= 0.7 and len(most_frequent_dates) >= 3:
        review_priority = "high"
    elif avg_confidence >= 0.5 and len(most_frequent_dates) >= 2:
        review_priority = "medium"
    else:
        review_priority = "low"

    # 置信度水平
    if avg_confidence >= 0.8:
        confidence_level = "very_high"
    elif avg_confidence >= 0.6:
        confidence_level = "high"
    elif avg_confidence >= 0.4:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    # 生成具体建议
    notes = []
    if primary_date:
        notes.append(f"主要复习日期: {primary_date}，该日期涉及 {most_frequent_dates[0]['frequency']} 个关键词")

    if supporting_dates:
        notes.append(f"补充复习日期: {', '.join(supporting_dates)}")

    if focus_keywords:
        notes.append(f"重点关注关键词: {', '.join(focus_keywords)}")

    if review_priority == "high":
        notes.append("复习优先级: 高 - 建议优先复习这些日期的笔记")
    elif review_priority == "medium":
        notes.append("复习优先级: 中 - 建议在时间允许时复习")
    else:
        notes.append("复习优先级: 低 - 相关性较弱，可作为参考")

    return {
        "primary_review_date": primary_date,
        "supporting_dates": supporting_dates,
        "focus_keywords": focus_keywords,
        "review_priority": review_priority,
        "confidence_level": confidence_level,
        "notes": " | ".join(notes)
    }


def batch_process_questions(
        questions_list: List[Dict],
        knowledge_base: NotesKnowledgeBase = None,
        searcher: ExamNotesSearcher = None,
        max_queries_per_keyword: int = 2,
        return_objects: bool = True,
        progress_callback=None
) -> Dict:
    """
    批量处理多个真题问题

    Args:
        questions_list: 真题问题列表，每个元素是question_data字典
        knowledge_base: 可选，已初始化的知识库对象
        searcher: 可选，已初始化的检索器对象
        max_queries_per_keyword: 每个关键词的最大查询数
        return_objects: 是否返回使用的对象
        progress_callback: 进度回调函数，接收(current, total, message)

    Returns:
        批量处理结果:
        {
            "status": "complete"/"partial",
            "total_questions": 10,
            "successful_questions": 8,
            "failed_questions": 2,
            "questions_results": [
                {每个问题的定位结果...},
                ...
            ],
            "summary": {
                "total_keywords_processed": 50,
                "total_unique_dates_found": 25,
                "avg_confidence": 0.75,
                "subject_distribution": {"数学二": 5, "政治": 3, "408": 2},
                "priority_distribution": {"high": 3, "medium": 4, "low": 1}
            },
            "knowledge_base": <对象>,  # 可选
            "searcher": <对象>         # 可选
        }
    """

    start_time = time.time()

    # 初始化对象（如果未提供）
    if knowledge_base is None:
        knowledge_base = NotesKnowledgeBase(api_key=AK, search_topic_id=ST_ID)

    if searcher is None:
        searcher = ExamNotesSearcher(knowledge_base=knowledge_base)

    questions_results = []
    successful_count = 0
    failed_count = 0
    all_keywords_count = 0
    all_unique_dates = set()
    all_confidences = []
    subject_distribution = defaultdict(int)
    priority_distribution = defaultdict(int)

    logger.info(f"🚀 开始批量处理 {len(questions_list)} 个真题问题")

    for i, question_data in enumerate(questions_list):
        # 进度回调
        if progress_callback:
            progress_callback(i + 1, len(questions_list), f"处理第 {i + 1} 个问题")

        logger.info(f"进度 [{i + 1}/{len(questions_list)}]: {question_data.get('year', '未知')}-"
                    f"{question_data.get('subject', '未知')}-{question_data.get('qid', '未知')}")

        # 处理单个问题
        result = locate_dates_by_keywords(
            question_data=question_data,
            knowledge_base=knowledge_base,
            searcher=searcher,
            max_queries_per_keyword=max_queries_per_keyword,
            return_objects=False  # 不在每个结果中返回对象
        )

        questions_results.append(result)

        # 统计
        if result["status"] in ["complete", "partial"]:
            successful_count += 1

            # 统计科目分布
            subject = question_data.get("subject", "未知")
            subject_distribution[subject] += 1

            # 收集唯一日期
            unique_dates = result["summary"].get("unique_dates", [])
            all_unique_dates.update(unique_dates)

            # 收集置信度
            avg_conf = result["summary"].get("avg_confidence", 0)
            if avg_conf > 0:
                all_confidences.append(avg_conf)

            # 统计优先级分布
            priority = result["recommendations"].get("review_priority", "low")
            priority_distribution[priority] += 1

            # 统计关键词数量
            keywords_count = len(question_data.get("keywords", []))
            all_keywords_count += keywords_count
        else:
            failed_count += 1

        # 避免API限制
        if i < len(questions_list) - 1:
            time.sleep(1)  # 问题间间隔1秒

    # 生成汇总信息
    total_time = round(time.time() - start_time, 2)

    summary_data = {
        "status": "complete" if successful_count > 0 else "error",
        "total_questions": len(questions_list),
        "successful_questions": successful_count,
        "failed_questions": failed_count,
        "questions_results": questions_results,
        "summary": {
            "total_keywords_processed": all_keywords_count,
            "total_unique_dates_found": len(all_unique_dates),
            "avg_confidence": round(sum(all_confidences) / len(all_confidences), 3)
            if all_confidences else 0,
            "subject_distribution": dict(subject_distribution),
            "priority_distribution": dict(priority_distribution),
            "total_time_seconds": total_time,
            "avg_time_per_question": round(total_time / len(questions_list), 2)
            if questions_list else 0
        },
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **({"knowledge_base": knowledge_base, "searcher": searcher} if return_objects else {})
    }

    logger.info(f"🎉 批量处理完成: 成功 {successful_count}/{len(questions_list)}，"
                f"找到 {len(all_unique_dates)} 个唯一日期")

    return summary_data


# 定义进度回调函数
def progress_callback_(current, total, message):
    print(f"[{current}/{total}] {message}")


def load_json_files(folder_path):
    """
    从指定文件夹加载所有JSON文件并转换为字典列表

    Args:
        folder_path (str): JSON文件所在的文件夹路径

    Returns:
        list: 包含所有JSON文件内容的字典列表
    """
    json_dicts = []

    # 确保文件夹存在
    if not os.path.exists(folder_path):
        print(f"错误：文件夹 '{folder_path}' 不存在")
        return json_dicts

    # 使用glob查找所有.json文件（包括子目录中的文件）
    json_files = glob.glob(os.path.join(folder_path, "**", "*.json"), recursive=True)

    if not json_files:
        print(f"警告：在 '{folder_path}' 中未找到任何JSON文件")
        return json_dicts

    print(f"找到 {len(json_files)} 个JSON文件")

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                json_dicts.append(data)
                print(f"成功加载: {os.path.basename(file_path)}")
        except json.JSONDecodeError as e:
            print(f"错误：文件 '{os.path.basename(file_path)}' JSON格式错误: {e}")
        except Exception as e:
            print(f"错误：读取文件 '{os.path.basename(file_path)}' 时发生错误: {e}")

    print(f"总共加载了 {len(json_dicts)} 个JSON文件")
    return json_dicts


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

    # 解析批量结果
    print(f"批量处理完成: {b_res['successful_questions']}/{b_res['total_questions']} 成功")
    print(f"总共找到 {b_res['summary']['total_unique_dates_found']} 个唯一日期")
    print(f"平均置信度: {b_res['summary']['avg_confidence']}")

    # 查看科目分布
    print("科目分布:")
    for sub, count in b_res['summary']['subject_distribution'].items():
        print(f"  {sub}: {count} 个问题")

    # 查看优先级分布
    print("复习优先级分布:")
    for priority_, count in b_res['summary']['priority_distribution'].items():
        print(f"  {priority_}: {count} 个问题")

    print(b_res['questions_results'])
