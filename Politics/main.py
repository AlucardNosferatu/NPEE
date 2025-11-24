from lxml import etree


def prune_xml(xml_content, max_level):
    """
    修剪XML中的节点，保留到指定层级，删除更深的分支
    :param xml_content: XML内容字符串
    :param max_level: 最大保留层级（根节点为1级）
    :return: 修剪后的XML字符串
    """
    # 解析XML
    root = etree.fromstring(xml_content)

    def recursive_prune(node, current_level):
        # 如果当前层级等于最大层级，删除所有子节点
        if current_level == max_level:
            # 清除所有子节点
            node[:] = []
            return
        # 否则继续递归处理子节点（层级+1）
        for child in node:
            recursive_prune(child, current_level + 1)

    # 从根节点开始处理（根节点为1级）
    recursive_prune(root, 1)

    # 转换回字符串并返回
    return etree.tostring(root, encoding='UTF-8', pretty_print=True)


if __name__ == "__main__":
    # 读取原始XML文件
    fname = '毛中特'
    with open(fname+'.mm', "rb") as f:
        xml_content = f.read()

        # 设置保留的最大层级（例如保留到3级）
    level = 5  # 可修改为4或其他需要的层级

    # 修剪XML
    pruned_xml = prune_xml(xml_content, level)

    # 保存处理后的文件
    with open(fname + f"_保留{level}级.mm", "wb") as f:
        f.write(pruned_xml)

    print(f"已生成保留{level}级的XML文件")
