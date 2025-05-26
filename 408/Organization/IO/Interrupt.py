import random


def generate_interrupt_scenario():
    # 随机生成中断数量(2-4个)
    num_interrupts = random.randint(2, 4)

    # 生成中断ID列表
    interrupt_ids = [f"中断{i}" for i in range(1, num_interrupts + 1)]

    # 随机分配优先级(数字越小优先级越高)
    priorities = list(range(1, num_interrupts + 1))
    random.shuffle(priorities)
    priority_map = {interrupt_ids[i]: priorities[i] for i in range(num_interrupts)}

    # 随机生成处理时间(2-10个单位时间)
    process_times = {interrupt_id: random.randint(2, 10) for interrupt_id in interrupt_ids}

    # 生成到达时间(确保第一个中断到达时间为0)
    arrival_times = {interrupt_ids[0]: 0}
    for i in range(1, num_interrupts):
        # 后续中断到达时间在之前中断到达时间基础上随机增加1-5个单位
        prev_max_arrival = max(arrival_times.values())
        arrival_times[interrupt_ids[i]] = prev_max_arrival + random.randint(1, 5)

    # 随机选择一个中断作为问题中断
    question_interrupt = random.choice(interrupt_ids)

    return {
        "interrupt_ids": interrupt_ids,
        "priority_map": priority_map,
        "process_times": process_times,
        "arrival_times": arrival_times,
        "question_interrupt": question_interrupt
    }


def calculate_response_time(scenario):
    # 初始化时间线和处理状态
    current_time = 0
    processing_interrupt = None
    response_times = {}

    # 创建事件列表(到达事件和完成事件)
    events = []
    for interrupt_id in scenario["interrupt_ids"]:
        arrival_time = scenario["arrival_times"][interrupt_id]
        events.append(("arrival", arrival_time, interrupt_id))

    # 按时间排序事件
    events.sort(key=lambda x: x[1])

    # 处理每个事件
    for event_type, event_time, event_interrupt in events:
        if event_type == "arrival":
            # 更新当前时间
            current_time = max(current_time, event_time)

            # 如果没有正在处理的中断，立即处理该中断
            if processing_interrupt is None:
                processing_interrupt = event_interrupt
                response_times[processing_interrupt] = current_time - scenario["arrival_times"][processing_interrupt]

                # 添加完成事件
                completion_time = current_time + scenario["process_times"][processing_interrupt]
                events.append(("completion", completion_time, processing_interrupt))
                events.sort(key=lambda x: x[1])

            # 如果有正在处理的中断，比较优先级
            else:
                # 如果新到达的中断优先级更高
                if scenario["priority_map"][event_interrupt] < scenario["priority_map"][processing_interrupt]:
                    # 计算当前中断已处理时间
                    processed_time = current_time - scenario["arrival_times"][processing_interrupt]

                    # 更新当前中断的处理时间
                    scenario["process_times"][processing_interrupt] -= processed_time

                    # 添加当前中断的新完成事件
                    new_completion_time = current_time + scenario["process_times"][processing_interrupt]
                    events.append(("completion", new_completion_time, processing_interrupt))
                    events.sort(key=lambda x: x[1])

                    # 开始处理新中断
                    processing_interrupt = event_interrupt
                    response_times[processing_interrupt] = current_time - scenario["arrival_times"][
                        processing_interrupt]

                    # 添加新中断的完成事件
                    new_completion_time = current_time + scenario["process_times"][processing_interrupt]
                    events.append(("completion", new_completion_time, processing_interrupt))
                    events.sort(key=lambda x: x[1])

        elif event_type == "completion":
            # 更新当前时间
            current_time = max(current_time, event_time)

            # 完成当前中断处理
            if processing_interrupt == event_interrupt:
                processing_interrupt = None

    return response_times[scenario["question_interrupt"]]


def generate_question_and_answer():
    scenario = generate_interrupt_scenario()

    # 生成题目文本
    question = (
        "【考研408中断响应时间分析】\n\n"
        "考虑以下中断系统：\n"
    )

    # 添加中断信息
    for interrupt_id in scenario["interrupt_ids"]:
        question += (
            f"- {interrupt_id}: 优先级 {scenario['priority_map'][interrupt_id]}, "
            f"处理时间 {scenario['process_times'][interrupt_id]} 单位, "
            f"到达时间 {scenario['arrival_times'][interrupt_id]} 单位\n"
        )

    question += (
        f"\n假设系统采用可抢占式优先级调度，请问 {scenario['question_interrupt']} 的响应时间是多少？\n"
        "(响应时间定义为从中断到达至开始处理的时间间隔)"
    )

    # 计算答案
    response_time = calculate_response_time(scenario)

    # 生成答案解析
    answer = (
        f"【答案】\n{scenario['question_interrupt']} 的响应时间为 {response_time} 单位时间。\n\n"
        "【解析】\n"
        "1. 系统采用可抢占式优先级调度，高优先级中断可以打断低优先级中断的处理。\n"
        "2. 响应时间计算需要考虑中断到达时CPU的状态以及其他中断的干扰。\n"
        "3. 通过分析中断到达时间和优先级关系，得出该中断实际开始处理的时间点。\n"
        "4. 响应时间 = 开始处理时间 - 到达时间 = {response_time} 单位时间。"
    )

    return question, answer


if __name__ == "__main__":
    question_, answer_ = generate_question_and_answer()
    print(question_)
    print("\n" + "=" * 50 + "\n")
    print(answer_)
