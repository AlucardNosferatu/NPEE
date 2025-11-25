import ipaddress
import random


class QuestionGenerator:
    @staticmethod
    def generate_subnet_mask_question():
        """生成子网掩码计算题目"""
        # 随机选择一个A、B、C类网络
        classes = [
            {"prefix": "10.", "default_mask": 8},
            {"prefix": "172.16.", "default_mask": 12},
            {"prefix": "192.168.", "default_mask": 16}
        ]
        network_class = random.choice(classes)

        # 随机生成基础网络 - 修复IP地址生成逻辑
        base_ip = network_class["prefix"]
        if network_class["default_mask"] == 8:
            # A类地址: 10.x.0.0
            base_ip += f"{random.randint(0, 255)}.0.0"
        elif network_class["default_mask"] == 12:
            # B类地址: 172.16.x.0
            base_ip += f"{random.randint(0, 15)}.0"
        else:
            # C类地址: 192.168.x.0
            base_ip += f"{random.randint(0, 255)}.0"

        # 随机确定子网数量（2的幂）
        subnet_bits = random.randint(1, 6)  # 最多64个子网
        num_subnets = 2 ** subnet_bits

        question = f"已知IP地址为{base_ip}/{network_class['default_mask']}，需要划分{num_subnets}个子网。\n"
        question += "请计算：\n"
        question += "1. 新的子网掩码\n"
        question += "2. 每个子网的网络地址\n"
        question += "3. 每个子网的广播地址\n"
        question += "4. 每个子网的可用主机数"

        # 生成答案
        answer = []
        new_prefix = network_class["default_mask"] + subnet_bits
        new_mask = ipaddress.IPv4Network(f"0.0.0.0/{new_prefix}").netmask
        answer.append(f"1. 新的子网掩码: {new_mask} ({new_prefix})")

        network = ipaddress.IPv4Network(f"{base_ip}/{network_class['default_mask']}", strict=False)
        subnets = list(network.subnets(prefixlen_diff=subnet_bits))

        answer.append("2-4. 各子网信息:")
        for i, subnet in enumerate(subnets):
            answer.append(f"\n子网 {i + 1}:")
            answer.append(f"   网络地址: {subnet.network_address}")
            answer.append(f"   广播地址: {subnet.broadcast_address}")
            answer.append(f"   可用主机数: {subnet.num_addresses - 2}")

        return question, answer

    @staticmethod
    def generate_cidr_aggregation_question():
        """生成CIDR聚合题目"""
        # 随机选择一个起始网络
        base_ip = f"192.168.{random.randint(0, 63)}.0"
        base_prefix = random.randint(16, 24)
        base_network = ipaddress.IPv4Network(f"{base_ip}/{base_prefix}", strict=False)

        # 确定要聚合的子网数量
        num_subnets = random.randint(2, 4)

        # 生成子网
        subnets = []
        current_network = base_network
        for _ in range(num_subnets):
            # 确保子网可以进一步划分
            if current_network.prefixlen < 30:
                sub_prefix = current_network.prefixlen + 1
                subnets_list = list(current_network.subnets(new_prefix=sub_prefix))
                current_network = subnets_list[1]  # 使用第二个子网继续划分
                subnets.append(subnets_list[0])
            else:
                subnets.append(current_network)

        question = "请计算以下子网的CIDR聚合结果：\n"
        for i, subnet in enumerate(subnets):
            question += f"{i + 1}. {subnet.network_address}/{subnet.prefixlen}\n"

        # 生成答案
        # 找到最长共同前缀
        binary_ips = [bin(int(subnet.network_address))[2:].zfill(32) for subnet in subnets]
        common_prefix = ""
        for i in range(32):
            bits = [ip[i] for ip in binary_ips]
            if len(set(bits)) == 1:
                common_prefix += bits[0]
            else:
                break

        aggregated_prefix = len(common_prefix)
        aggregated_ip_int = int(common_prefix.ljust(32, '0'), 2)
        aggregated_ip = ipaddress.IPv4Address(aggregated_ip_int)
        aggregated_network = ipaddress.IPv4Network(f"{aggregated_ip}/{aggregated_prefix}", strict=False)

        answer = [f"聚合后的网络地址和掩码: {aggregated_network.network_address}/{aggregated_prefix}"]

        return question, answer

    @staticmethod
    def generate_vlsm_question():
        """生成VLSM超网划分题目"""
        # 随机选择一个B类网络
        base_ip = f"172.16.{random.randint(0, 15)}.0"
        base_prefix = 16

        # 随机生成不同部门的主机需求
        departments = [
            {"name": "销售部", "hosts": random.randint(100, 200)},
            {"name": "技术部", "hosts": random.randint(50, 100)},
            {"name": "财务部", "hosts": random.randint(20, 50)},
            {"name": "人力资源部", "hosts": random.randint(10, 20)},
            {"name": "行政部", "hosts": random.randint(5, 10)}
        ]
        # 随机选择3-5个部门
        num_departments = random.randint(3, 5)
        departments = random.sample(departments, num_departments)
        # 按主机数从大到小排序
        departments.sort(key=lambda x: x["hosts"], reverse=True)

        question = f"已知网络地址为{base_ip}/{base_prefix}，需要为以下部门划分子网：\n"
        for i, dept in enumerate(departments):
            question += f"{i + 1}. {dept['name']}: {dept['hosts']}台主机\n"
        question += "请使用VLSM方法进行子网划分，为每个部门分配合适的子网，并计算：\n"
        question += "1. 每个子网的网络地址\n"
        question += "2. 子网掩码\n"
        question += "3. 广播地址\n"
        question += "4. 可用IP地址范围"

        # 生成答案 - 完全重写VLSM逻辑
        answer = []
        base_network = ipaddress.IPv4Network(f"{base_ip}/{base_prefix}", strict=False)
        current_address = base_network.network_address

        for dept in departments:
            # 计算所需的主机位数
            required_hosts = dept["hosts"]
            host_bits = 0
            while (2 ** host_bits) - 2 < required_hosts:
                host_bits += 1

            # 计算子网前缀长度
            subnet_prefix = 32 - host_bits

            # 计算子网大小
            subnet_size = 2 ** host_bits

            # 确保当前地址对齐到子网边界
            current_int = int(current_address)
            if current_int % subnet_size != 0:
                # 对齐到下一个子网边界
                current_int = ((current_int // subnet_size) + 1) * subnet_size
                current_address = ipaddress.IPv4Address(current_int)

            # 检查是否超出基网络范围
            if current_int + subnet_size - 1 > int(base_network.broadcast_address):
                answer.append(f"\n{dept['name']}: 网络地址不足")
                break

            # 创建子网
            subnet = ipaddress.IPv4Network(f"{current_address}/{subnet_prefix}", strict=False)

            answer.append(f"\n{dept['name']} ({dept['hosts']}台主机):")
            answer.append(f"1. 网络地址: {subnet.network_address}")
            answer.append(f"2. 子网掩码: {subnet.netmask} ({subnet_prefix})")
            answer.append(f"3. 广播地址: {subnet.broadcast_address}")
            answer.append(f"4. 可用IP地址范围: {subnet.network_address + 1} - {subnet.broadcast_address - 1}")

            # 更新下一个子网的起始地址
            current_address = subnet.broadcast_address + 1

        return question, answer

    @staticmethod
    def generate_random_question():
        """随机选择一种题型生成题目"""
        question_types = [
            QuestionGenerator.generate_subnet_mask_question,
            QuestionGenerator.generate_cidr_aggregation_question,
            QuestionGenerator.generate_vlsm_question
        ]
        generator = random.choice(question_types)
        return generator()


def main():
    print("欢迎使用IP地址与子网划分随机题目生成器！\n")

    while True:
        print("\n请选择操作：")
        print("1. 生成随机题目")
        print("2. 生成子网掩码计算题目")
        print("3. 生成CIDR聚合题目")
        print("4. 生成VLSM超网划分题目")
        print("5. 退出")

        choice = input("\n请输入选项(1-5): ")

        if choice == '5':
            print("感谢使用，再见！")
            break

        try:
            if choice == '1':
                question, answer = QuestionGenerator.generate_random_question()
            elif choice == '2':
                question, answer = QuestionGenerator.generate_subnet_mask_question()
            elif choice == '3':
                question, answer = QuestionGenerator.generate_cidr_aggregation_question()
            elif choice == '4':
                question, answer = QuestionGenerator.generate_vlsm_question()
            else:
                print("无效的选项，请重新输入。")
                continue

            print("\n" + "=" * 50)
            print("题目:")
            print(question)

            show_answer = input("\n是否显示答案？(y/n): ")
            if show_answer.lower() == 'y':
                print("\n" + "=" * 50)
                print("答案:")
                for line in answer:
                    print(line)
                print("=" * 50)
        except Exception as e:
            print(f"生成题目时出错: {e}")


if __name__ == "__main__":
    main()
