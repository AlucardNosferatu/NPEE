# ---------- K叉树节点定义 ----------
from collections import deque

from search import SearchEngine


class KTreeNode:
    def __init__(self, val, children=None):
        self.val = val
        self.children = children if children is not None else []

    def __repr__(self):
        return f"KTreeNode({self.val})"


# 构建示例 K 叉树：
#        1
#      / | \
#     2  3  4
#    / \    |
#   5   6   7
node5 = KTreeNode(5)
node6 = KTreeNode(6)
node2 = KTreeNode(2, [node5, node6])
node3 = KTreeNode(3)
node7 = KTreeNode(7)
node4 = KTreeNode(4, [node7])
root = KTreeNode(1, [node2, node3, node4])


# ---------- BFS 注入函数实现 ----------
def bfs_process(current_node, candidates):
    """
    将当前节点的所有孩子添加到 candidates 队列的末尾。
    """
    for child in current_node.children:
        candidates.append(child)  # 入队（尾部）


def bfs_select(current_node, candidates):
    """
    从 candidates 队列的左侧取出下一个状态（出队）。
    如果队列为空，返回 None（此时应停止搜索）。
    """
    _ = current_node
    if candidates:
        return candidates.popleft()  # 从左侧弹出
    else:
        return None


def bfs_stop_cond(current_node):
    """
    终止条件：找到值为 7 的节点。
    """
    return current_node.val == 7


# ---------- 初始化搜索引擎 ----------
# 初始候选集：一个包含根节点的队列
initial_candidates = deque()

engine = SearchEngine(
    process_func=bfs_process,
    select_func=bfs_select,
    stop_cond_func=bfs_stop_cond,
    initial_state=root,
    initial_candidates=initial_candidates
)

# ---------- 执行 BFS 遍历 ----------
step = 0
print("BFS traversal order:")
while not engine.is_stopped():
    print(f"Step {step}: visiting {engine.current_state.val}")
    engine.step()
    step += 1

print(f"Search stopped. Found target node with value {engine.current_state.val} at step {step}")
