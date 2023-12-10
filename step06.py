import networkx as nx
import matplotlib.pyplot as plt
import os
from javalang import parse, tree
import json
import Levenshtein

nodes = []
links = []
categories = [{"name": "A"},
              {"name": "B"},
              {"name": "C"},
              {"name": "D"},
              {"name": "E"},
              {"name": "F"},
              {"name": "G"},
              {"name": "H"},
              {"name": "I"}]
# json文件输出地址
file_path = 'json/all.json'


def add_node_info(graph, node, parent_info=""):
    children = list(graph.successors(node))
    num_children = len(children)

    # Set the node attributes
    graph.nodes[node]["num_children"] = num_children
    graph.nodes[node]["children"] = children
    graph.nodes[node]["parent_info"] = parent_info

    # Recursively add information for each child
    for child in children:
        add_node_info(graph, child, f"{node} -> {parent_info}")


def most_similar_string(string, string_set):
    min_distance = float('inf')
    most_similar_string = None

    for s in string_set:
        distance = Levenshtein.distance(string, s)
        if distance < min_distance:
            min_distance = distance
            most_similar_string = s

    return most_similar_string


def parse_java_files(directory):
    G = nx.DiGraph()

    def process_annotation(annotations):
        return "Service" in annotations or "Component" in annotations or "SI" in annotations

    def process_resource_annotation(annotations):
        return "Autowired" in [obj.name for obj in annotations] or "Resource" in [obj.name for obj in
                                                                                  annotations] or "SI" in [obj.name for
                                                                                                           obj in
                                                                                                           annotations]

    def process_type_declaration(declaration):
        class_name = declaration.name
        resource_attributes = []

        for field_declaration in declaration.fields:
            if process_resource_annotation(field_declaration.annotations):
                resource_attributes.append(field_declaration.type.name)

        if declaration.implements is not None and len(declaration.implements) > 0:
            # 有实现接口
            if len(declaration.implements) == 1:
                # 只是实现一个接口
                class_name = declaration.implements[0].name
            else:
                # 展示最像当前类的接口
                class_name = most_similar_string(class_name, [obj.name for obj in declaration.implements])
        else:
            # 就直接展示实现类
            class_name = class_name

        # print(f"class: {class_name}")
        G.add_node(f"{class_name}")
        for attribute in resource_attributes:
            # print(f"    lib: {attribute}")
            G.add_edge(f"{class_name}", f"{attribute}")
            link = NodeLink(class_name, attribute)
            links.append(link)

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

    # 为每个节点添加信息,从第一个开始
    for node in G.nodes:
        add_node_info(G, node)

    # 调整 k 的值以控制节点之间的距离
    pos = nx.spring_layout(G, k=0.9)

    # 不需要python画图
    # 调整节点大小、字体大小和箭头大小
    # plt.figure(figsize=(50, 60))  # 调整图的大小
    # nx.draw(G, pos, with_labels=False, node_size=1000, node_color="skyblue", font_size=10, font_color="black",font_weight="bold", arrowsize=15)
    # node_labels = {node: f"{node}" for node in G.nodes}
    # nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, verticalalignment="center")


    # todo:调整，改成根据包路径来分类 [目前先安装依赖数量分类]
    for node in G.nodes:
        son = len(G.nodes[node]['children'])
        category = 0
        # 使用范围检查来判断 son 的取值范围
        if 0 <= son < 1:
            category = 0
        elif 1 <= son < 2:
            category = 1
        elif 2 <= son < 3:
            category = 2
        elif 3 <= son < 4:
            category = 3
        elif 4 <= son < 5:
            category = 4
        elif 5 <= son < 6:
            category = 5
        elif 7 <= son < 9:
            category = 6
        elif 9 <= son < 11:
            category = 7
        else:
            category = 8

        parent_path = ''
        children = []
        if len(G.nodes[node]) != 0:
            parent_path = G.nodes[node]['parent_info']
            children = G.nodes[node]['children']
        data = NodeData(node, node, son * 5, pos.get(node)[0], pos.get(node)[1], son, category, parent_path, children)
        nodes.append(data)


    # 拾取判断循环依赖

    node_dicts = [node.__dict__() for node in nodes]
    link_dicts = [link.__dict__() for link in links]
    res_dict = {'nodes': node_dicts, 'links': link_dicts, 'categories': categories}

    json_str = json.dumps(res_dict)
    print(f"\n {json_str}")
    with open(file_path, 'w') as f:
        f.write(json_str)
    # plt.show()


class NodeLink:
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __dict__(self):
        return {'source': self.source, 'target': self.target}


class NodeData:
    def __init__(self, sid, name, symbolSize, x, y, value, category, parent_path, children):
        self.children = children
        self.category = category
        self.value = value
        self.y = y
        self.x = x
        self.sid = sid
        self.symbolSize = symbolSize
        self.name = name
        self.parent_path = parent_path

    def __dict__(self):
        return {
            'category': self.category,
            'value': self.value,
            'y': self.y,
            'x': self.x,
            'sid': self.sid,
            'symbolSize': self.symbolSize,
            'name': self.name,
            'parentPath': self.parent_path,
            'children': self.children
        }


# 下面是参考展示示例
# https://echarts.apache.org/examples/zh/editor.html?c=graph&lang=js
if __name__ == '__main__':
    # 填入你的java项目根目录绝对路径
    # 目前只扫描@Service 和@Component 类和它的@Autowired属性的关系以及裙带关系。
    rootPath = "D:\\Data\\Money\\MallChat\\boot\\MallChat"
    start(rootPath)

