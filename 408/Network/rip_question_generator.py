import random


def generate_rip_question():
    # 生成网络列表（6-10个网络）
    networks = [f"192.168.{i}.0/24" for i in range(6, random.randint(11, 15))]
    random.shuffle(networks)

    # 生成路由器名称
    routers = ["RouterA", "RouterB", "RouterC", "RouterD"]
    random.shuffle(routers)
    local_router = routers[0]
    neighbor_router = routers[1]

    # 生成本地路由表
    local_routes = {}
    num_local_routes = random.randint(3, 5)

    # 首先添加直连路由（跳数为1）
    direct_networks = random.sample(networks[:num_local_routes], min(2, num_local_routes))
    for net in direct_networks:
        local_routes[net] = (1, neighbor_router)  # 直连路由跳数固定为1

    # 添加其他路由
    remaining_networks = [net for net in networks[:num_local_routes] if net not in direct_networks]
    for net in remaining_networks:
        hop = random.randint(2, 15)  # 非直连路由跳数从2开始
        next_hop = random.choice([r for r in routers[2:] if r != local_router])
        local_routes[net] = (hop, next_hop)

    # 直连跳数固定为1（RIP协议特性）
    direct_hop = 1

    # 生成邻居路由表
    neighbor_routes = {}

    # 确保部分网络在两个路由表中都存在
    common_networks = random.sample(networks[:num_local_routes], random.randint(1, min(3, num_local_routes)))
    for net in common_networks:
        # 为相同网络生成不同跳数
        original_hop = local_routes[net][0]
        # 确保邻居跳数至少为1
        new_hop = random.choice([h for h in range(1, 16) if h != original_hop])
        neighbor_routes[net] = (
            new_hop, random.choice([r for r in routers if r not in [local_router, neighbor_router]])
        )

    # 添加一些本地路由表中没有的新网络
    new_networks = [net for net in networks if net not in local_routes]
    # 修复：确保采样数不超过可用网络数
    sample_size = min(len(new_networks), random.randint(2, 4))
    for net in random.sample(new_networks, sample_size):
        hop = random.randint(1, 14)  # 确保总跳数不超过15 (1 + 14 = 15)
        neighbor_routes[net] = (hop, random.choice([r for r in routers if r not in [local_router, neighbor_router]]))

    # 生成题目文本
    question = f"""
RIP路由表更新题目

题目描述:
{local_router}收到了来自邻居路由器{neighbor_router}的路由更新信息。

请根据RIP协议的"跳数+1"原则更新{local_router}的路由表，注意RIP协议的最大跳数为15跳。

本地路由器{local_router}的当前路由表:
"""
    for net, (hop, next_hop) in local_routes.items():
        question += f"网络: {net}, 跳数: {hop}, 下一跳: {next_hop}\n"

    question += f"""

从邻居路由器{neighbor_router}收到的路由表信息:
"""
    for net, (hop, next_hop) in neighbor_routes.items():
        question += f"网络: {net}, 跳数: {hop}, 下一跳: {next_hop}\n"

    # 计算正确答案
    updated_routes = local_routes.copy()
    for net, (neighbor_hop, neighbor_next_hop) in neighbor_routes.items():
        new_hop = neighbor_hop + direct_hop
        if new_hop >= 16:  # 跳数超过15，不可达
            continue

        if net not in updated_routes:
            # 新网络
            updated_routes[net] = (new_hop, neighbor_router)
        else:
            current_hop, current_next_hop = updated_routes[net]
            if neighbor_router == current_next_hop:
                # 同一来源，更新跳数
                updated_routes[net] = (new_hop, neighbor_router)
            elif new_hop < current_hop:
                # 更好的路径
                updated_routes[net] = (new_hop, neighbor_router)

    # 生成答案文本
    answer = f"""
RIP路由表更新答案

更新后的{local_router}路由表:
"""
    for net, (hop, next_hop) in sorted(updated_routes.items()):
        answer += f"网络: {net}, 跳数: {hop}, 下一跳: {next_hop}\n"

    answer += """

更新说明:
1. 对于每个从邻居收到的路由条目，计算跳数 = 邻居跳数 + 到邻居的直接跳数(固定为1)
2. 如果计算的跳数 >= 16，则认为该网络不可达，不添加到路由表
3. 如果该网络不在本地路由表中，直接添加
4. 如果下一跳是相同的路由器，更新跳数
5. 如果通过邻居的新路径跳数更少，更新路由表条目
6. 其他情况保持原有路由条目不变
7. 注意：RIP协议中，能够收到路由更新意味着这两个路由器是直连邻居，直连跳数始终为1
"""

    return question, answer


# 主函数
if __name__ == "__main__":
    q, a = generate_rip_question()
    print(q)

    # 等待用户查看题目后按回车查看答案
    input("\n按回车键查看答案...")
    print(a)
