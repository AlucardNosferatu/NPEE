import random


# 定义二叉树节点类
class TreeNode:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None
        self.height = 1

    # 遍历二叉树
    def traversal(self, mode='preorder'):
        if self is None:
            return []

        result = []
        if mode == 'preorder':
            result.append(self.val)
            result.extend(self.left.traversal(mode))
            result.extend(self.right.traversal(mode))
        elif mode == 'inorder':
            result.extend(self.left.traversal(mode))
            result.append(self.val)
            result.extend(self.right.traversal(mode))
        elif mode == 'postorder':
            result.extend(self.left.traversal(mode))
            result.extend(self.right.traversal(mode))
            result.append(self.val)

        return result

    # 构建二叉搜索树或AVL树
    def build_bst(self, value, avl=False):
        if value <= self.val:
            if self.left is None:
                self.left = TreeNode(value)
            else:
                self.left.build_bst(value, avl)
        else:
            if self.right is None:
                self.right = TreeNode(value)
            else:
                self.right.build_bst(value, avl)

        if avl:
            self.update_height()
            return self.balance()

    # 更新节点高度
    def update_height(self):
        left_height = self.left.height if self.left else 0
        right_height = self.right.height if self.right else 0
        self.height = max(left_height, right_height) + 1

    # 获取节点的平衡因子
    def get_balance_factor(self):
        left_height = self.left.height if self.left else 0
        right_height = self.right.height if self.right else 0
        return left_height - right_height

    # 平衡二叉树
    def balance(self):
        balance_factor = self.get_balance_factor()
        if balance_factor > 1:
            if self.left.get_balance_factor() < 0:
                self.left = self.left.rotate_left()
            return self.rotate_right()
        elif balance_factor < -1:
            if self.right.get_balance_factor() > 0:
                self.right = self.right.rotate_right()
            return self.rotate_left()
        else:
            return self

    # 右旋转
    def rotate_right(self):
        new_root = self.left
        new_left_subtree = new_root.right
        self.left = new_left_subtree
        new_root.right = self
        self.update_height()
        new_root.update_height()
        return new_root

    # 左旋转
    def rotate_left(self):
        new_root = self.right
        new_right_subtree = new_root.left
        self.right = new_right_subtree
        new_root.left = self
        self.update_height()
        new_root.update_height()
        return new_root


# 创建完全二叉树
def create_complete_binary_tree(height):
    if height <= 0:
        return None
    root = TreeNode(random.randint(1, 100))
    root.left = create_complete_binary_tree(height - 1)
    root.right = create_complete_binary_tree(height - 1)
    return root


# 打印二叉树
def print_binary_tree(root):
    if root is None:
        return
    print(root.val)
    print_binary_tree(root.left)
    print_binary_tree(root.right)


# 插入随机生成的10个节点到二叉搜索树
bst = TreeNode(None)
random_values = random.sample(range(1, 101), 10)
for v in random_values:
    bst.build_bst(v)
