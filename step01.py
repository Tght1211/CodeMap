import networkx as nx
import matplotlib.pyplot as plt

import os
from javalang import parse, tree

def parse_java_files(directory):
    G = nx.DiGraph()

    def process_annotation(annotations):
        return "Service" in annotations or "Component" in annotations

    def process_resource_annotation(annotations):
        return "Autowired" in [obj.name for obj in annotations]

    def process_type_declaration(declaration):
        class_name = declaration.name
        resource_attributes = []

        for field_declaration in declaration.fields:
            if process_resource_annotation(field_declaration.annotations):
                resource_attributes.append(field_declaration.type.name)

        G.add_node(f"{class_name}")
        for attribute in resource_attributes:
            G.add_edge(f"{class_name}", f"{attribute}")

    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".java"):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    source_code = file.read()
                    try:
                        tree_structure = parse.parse(source_code)
                    except:
                        continue

                    for path, node in tree_structure:
                        if isinstance(node, tree.ClassDeclaration):
                            annotations = [annotation.name for annotation in node.annotations]

                            if process_annotation(annotations):
                                process_type_declaration(node)
    return G

def add_node_info(graph, node, parent_info=""):
    children = list(graph.successors(node))
    num_children = len(children)

    graph.nodes[node]["num_children"] = num_children
    graph.nodes[node]["children"] = children
    graph.nodes[node]["parent_info"] = parent_info

    for child in children:
        add_node_info(graph, child, f"{node} -> {parent_info}")

def start(rootPath):
    G = parse_java_files(rootPath)

    # 调整 k 的值以控制节点之间的距离
    pos = nx.spring_layout(G, k=0.9)

    # 调整节点大小、字体大小和箭头大小
    plt.figure(figsize=(50, 60))  # 调整图的大小
    nx.draw(G, pos, with_labels=False, node_size=1000, node_color="skyblue", font_size=10, font_color="black",
            font_weight="bold", arrowsize=15)

    node_labels = {node: f"{node}" for node in G.nodes}

    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, verticalalignment="center")

    plt.show()

if __name__ == '__main__':
    # 填入你的java项目根目录绝对路径
    # 目前只扫描@Service 和@Component 类和它的@Autowired属性的关系以及裙带关系。
    rootPath = "D:\\Data\\Money\\MallChat\\boot\\MallChat"
    start(rootPath)

