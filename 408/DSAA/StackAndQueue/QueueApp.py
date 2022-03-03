from graphviz import Digraph


def make_a_full_tree(depth=3, dot_graph=None, g_id_list=None):
    if dot_graph is None:
        dot_graph = Digraph(comment='A Full Tree')
    if g_id_list is None:
        g_id_list = list(range(0, 1024))
    g_id = 'Node_' + str(g_id_list.pop(0))
    parent = {'data': None, 'left': None, 'right': None, 'id': g_id}
    dot_graph.node(g_id, g_id)
    if depth > 0:
        parent['left'], g_id_left, _ = make_a_full_tree(depth - 1, dot_graph, g_id_list)
        dot_graph.edge(g_id, g_id_left, constraint='True')
        parent['right'], g_id_right, _ = make_a_full_tree(depth - 1, dot_graph, g_id_list)
        dot_graph.edge(g_id, g_id_right, constraint='True')
    return parent, g_id, dot_graph


def level_traverse(tree):
    queue = [tree]
    output = []
    while len(queue) > 0:
        parent = queue.pop(0)
        output.append(parent['id'])
        if parent['left'] is not None:
            queue.append(parent['left'])
        if parent['right'] is not None:
            queue.append(parent['right'])
    return output


if __name__ is '__main__':
    ft, gid, graph = make_a_full_tree()
    res = level_traverse(ft)
    graph.view()
    print('Done')
