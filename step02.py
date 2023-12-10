import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mplcursors

def add_node_info(graph, node, parent_info=""):
    """
    Add information to the node, including the number of children and a list of children.
    """
    children = list(graph.successors(node))
    num_children = len(children)

    # Set the node attributes
    graph.nodes[node]["num_children"] = num_children
    graph.nodes[node]["children"] = children
    graph.nodes[node]["parent_info"] = parent_info

    # Recursively add information for each child
    for child in children:
        add_node_info(graph, child, f"{node} -> {parent_info}")

def start():
    # 创建一个有向图
    G = nx.DiGraph()

    # 添加节点
    G.add_node("A")
    G.add_node("B")
    G.add_node("C")
    G.add_node("D")
    G.add_node("E")
    G.add_node("F")
    G.add_node("G")

    # 添加边表示依赖关系
    G.add_edge("A", "B")
    G.add_edge("A", "C")
    G.add_edge("B", "D")
    G.add_edge("B", "E")
    G.add_edge("C", "E")
    G.add_edge("C", "F")
    G.add_edge("D", "G")
    G.add_edge("E", "F")
    G.add_edge("E", "G")

    # 为每个节点添加信息
    add_node_info(G, "A")

    # 创建3D图形
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # 绘制节点
    pos = nx.spring_layout(G, k=0.5)  # 调整 k 的值以控制节点之间的距离
    for node, (x, y) in pos.items():
        ax.text(x, y, 0, node, color='skyblue', size=8, ha='center', va='center')

    # 绘制边
    for edge in G.edges():
        x = [pos[edge[0]][0], pos[edge[1]][0]]
        y = [pos[edge[0]][1], pos[edge[1]][1]]
        z = [0, 0]
        ax.plot(x, y, z, color='gray', linestyle='dashed')

    # 设置坐标轴标签
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # 添加节点信息标签
    node_labels = {
        node: f"{node}\n\nson: {G.nodes[node]['num_children']}\n{G.nodes[node]['parent_info']}\n{G.nodes[node]['children']}"
        for node in G.nodes}

    # 鼠标悬停显示标签
    mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(node_labels[sel.target]))

    # 显示图形
    plt.show()

if __name__ == '__main__':
    start()
