import networkx as nx
import matplotlib.pyplot as plt

def print_hi():


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

    # 绘制图形
    pos = nx.spring_layout(G)  # 定义节点的布局
    nx.draw(G, pos, with_labels=True, node_size=900, node_color="skyblue", font_size=10, font_color="black",
            font_weight="bold", arrowsize=15)

    # 显示图形
    plt.show()


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
