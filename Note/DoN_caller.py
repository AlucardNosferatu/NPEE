"""
考点日期定位接口函数
功能：为真题检索引擎提供考点对应笔记日期的定位服务
"""
import time
from collections import defaultdict

from DoN import ExamNotesSearcher, ST_ID, AK, NotesKnowledgeBase, logger


def locate_exam_point_dates(
        exam_point: str,
        subject: str,
        knowledge_base: NotesKnowledgeBase = None,
        searcher: ExamNotesSearcher = None,
        max_queries: int = 2,
        return_objects: bool = True
):
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
    import time
    from datetime import datetime

    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        exam_points,
        knowledge_base: NotesKnowledgeBase = None,
        searcher: ExamNotesSearcher = None,
        max_queries_per_point: int = 2,
        return_objects: bool = True
):
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
    from datetime import datetime

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
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **({"knowledge_base": knowledge_base, "searcher": searcher} if return_objects else {})
    }

    logger.info(f"🎉 批量定位完成: 成功 {successful_count}/{len(exam_points)}，找到 {len(set(all_dates))} 个日期")
    return summary_data
