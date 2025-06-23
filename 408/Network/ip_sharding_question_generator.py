import random


def generate_ip_datagram_size():
    """生成合理的IP数据报大小（包含首部）"""
    # IP首部最小20字节，最大60字节（选项部分最长40字节）
    header_length = random.randint(5, 15) * 4  # 以4字节为单位
    # 数据部分长度随机，同时确保总长度是8的倍数（便于计算分片偏移）
    data_length = random.randint(1, 1500) * 8
    total_length = header_length + data_length
    return total_length, header_length


def generate_mtu():
    """生成合理的MTU值"""
    # 常见以太网MTU为1500字节，也有其他值
    common_mtus = [576, 1492, 1500, 9000]
    if random.random() < 0.7:  # 70%概率使用常见MTU
        return random.choice(common_mtus)
    else:  # 30%概率使用自定义MTU
        return random.randint(500, 10000)


def calculate_shards(mtu, datagram_size, header_length):
    """计算分片后的各分组信息"""
    data_size = datagram_size - header_length
    mtu_data = mtu - header_length  # MTU中可用于数据的部分

    # 确保数据部分是8的倍数（因为分片偏移量以8字节为单位）
    if mtu_data % 8 != 0:
        mtu_data = (mtu_data // 8) * 8

    if data_size <= mtu_data:
        # 无需分片
        return [(datagram_size, 0, 0)]

    shards = []
    remaining_data = data_size
    offset = 0

    while remaining_data > 0:
        if remaining_data > mtu_data:
            current_data = mtu_data
            mf = 1  # 还有后续分片
        else:
            current_data = remaining_data
            mf = 0  # 最后一个分片

        shard_length = current_data + header_length
        shard_offset = offset // 8  # 分片偏移量以8字节为单位
        shards.append((shard_length, shard_offset, mf))

        remaining_data -= current_data
        offset += current_data

    return shards


def generate_question():
    """生成题目和答案"""
    mtu = generate_mtu()
    datagram_size, header_length = generate_ip_datagram_size()
    header_length_bytes = header_length
    header_length_words = header_length // 4  # 以32位字为单位

    # 确保数据报大小大于MTU（否则不会分片，题目太简单）
    while datagram_size <= mtu + 20:  # 至少需要分片一次
        datagram_size, header_length = generate_ip_datagram_size()

    shards = calculate_shards(mtu, datagram_size, header_length)

    # 生成题目文本
    question = (f"已知网络的MTU为{mtu}字节，一个IP数据报总长度为{datagram_size}字节，"
                f"IP首部长度为{header_length_words}个字（{header_length_bytes}字节）。\n\n"
                f"要求：计算该IP数据报分片后的各分组信息，包括每个分片的总长度、"
                f"分片偏移量和MF标志位。")

    # 生成答案文本
    answer = f"题目条件：MTU = {mtu}字节，IP数据报总长度 = {datagram_size}字节，首部长度 = {header_length_bytes}字节\n\n分片计算过程：\n"
    answer += f"数据部分长度 = {datagram_size} - {header_length_bytes} = {datagram_size - header_length_bytes}字节\n"
    answer += f"每个分片的数据部分最大长度 = {mtu} - {header_length_bytes} = {mtu - header_length_bytes}字节\n"
    if (mtu - header_length_bytes) % 8 != 0:
        answer += f"注意：MTU中可用于数据的部分需要是8的倍数，因此每个分片的数据部分最大长度调整为{(mtu - header_length_bytes) // 8 * 8}字节\n"

    answer += "\n分片结果：\n"
    answer += "| 分片序号 | 总长度(字节) | 数据部分长度(字节) | 分片偏移量(8字节块) | 分片偏移量(字节) | MF标志 |\n"
    answer += "|----------|--------------|---------------------|---------------------|------------------|--------|\n"

    for i, (length, offset, mf) in enumerate(shards):
        data_length = length - header_length
        offset_bytes = offset * 8
        answer += f"| {i + 1}        | {length}         | {data_length}               | {offset}                 | {offset_bytes}            | {mf}      |\n"

    return question, answer


def main():
    """主函数：生成并展示题目和答案"""
    print("=" * 50)
    print("MAC地址与IP分组分片题目生成器 - MTU分片计算")
    print("=" * 50)

    while True:
        print("\n正在生成题目...")
        question, answer = generate_question()

        print("\n" + "题目：".center(50, "-"))
        print(question)

        input("\n按Enter键查看答案...")

        print("\n" + "答案：".center(50, "-"))
        print(answer)

        choice = input("\n是否生成新题目？(y/n): ").strip().lower()
        if choice != 'y':
            print("\n感谢使用题目生成器！")
            break


if __name__ == "__main__":
    main()