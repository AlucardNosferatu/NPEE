import random


def generate_bus_question():
    bus_width = random.choice([16, 32, 64, 128])
    frequency = random.choice([66, 100, 133, 200])
    cycles = random.choice([1, 2, 4])
    dual_edge = random.choice([True, False])  # 是否双沿触发

    # 生成题目描述
    protocol_desc = "采用突发传输方式，"
    if dual_edge:
        protocol_desc += "每个时钟周期通过上升沿和下降沿各传输一次数据，"
    question = f"某{bus_width}位总线工作于{frequency}MHz，{protocol_desc}每个总线传输周期为{cycles}个时钟周期，求总线的最大传输速率（单位MB/s）。"

    # 计算带宽
    transfers_per_cycle = 2 if dual_edge else 1
    bandwidth = (frequency * transfers_per_cycle * (bus_width / 8)) / cycles
    bandwidth = round(bandwidth, 2)

    # 生成计算过程
    formula_steps = [
        f"1. 总线宽度转换：{bus_width}位 = {bus_width // 8} 字节",
        f"2. 总线周期频率：{frequency}MHz / {cycles} = {frequency / cycles}MHz",
        f"3. 有效传输次数：{frequency / cycles}MHz × {transfers_per_cycle}次/周期 = {frequency * transfers_per_cycle / cycles}MHz" if dual_edge else "",
        f"4. 带宽计算：{bus_width // 8}字节 × {frequency * transfers_per_cycle / cycles}MHz = {bandwidth}MB/s"
    ]
    calculation = "\n".join([step for step in formula_steps if step])

    answer = f"答案：{bandwidth} MB/s\n计算步骤：\n{calculation}"

    return question, answer


# 示例运行
if __name__ == "__main__":
    q, a = generate_bus_question()
    print("题目：", q)
    print("\n答案：", a)
