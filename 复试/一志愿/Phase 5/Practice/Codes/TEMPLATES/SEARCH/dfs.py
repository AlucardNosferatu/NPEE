# 二叉树节点定义
from search import SearchEngine


class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# 构建示例树
root = TreeNode(1,
                TreeNode(2, TreeNode(4), TreeNode(5)),
                TreeNode(3, None, TreeNode(6)))


# 注入函数
def process_stack(current, candidates):
    """将当前节点的左右子节点（非空）推入 candidates（栈）"""
    if current.left:
        candidates.append(current.left)
    if current.right:
        candidates.append(current.right)


def select_stack(current, candidates):
    """从栈顶弹出一个节点作为下一个状态"""
    _ = current
    return candidates.pop() if candidates else None


def stop_if_five(current):
    return current.val == 5


# 初始化候选集为包含根节点的栈
engine = SearchEngine(
    process_func=process_stack,
    select_func=select_stack,
    stop_cond_func=stop_if_five,
    initial_state=root,
    initial_candidates=[root]  # 初始栈中只有根节点
)

# 执行搜索
step = 0
while not engine.is_stopped():
    print(f"Step {step}: visiting node {engine.current_state.val}")
    engine.step()
    step += 1
print(f"Found {engine.current_state.val} at step {step}")
