import networkx as nx
import sys
import os
from javalang import parse, tree
import json
import Levenshtein
import tkinter as tk
from tkinter import filedialog
from functools import partial

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
project_name = ''
# 增加递归深度限制
sys.setrecursionlimit(10000)
visited_nodes_all = []
map_interface_impl = {}
multiple = 1
elastic_distance = 1.8


def add_node_info(root, graph, node, parent_info=""):
    visited_nodes_all.append(node)
    children = list(graph.successors(node))
    num_children = len(children)

    # Set the node attributes
    graph.nodes[node]["num_children"] = num_children
    graph.nodes[node]["children"] = children
    graph.nodes[node]["parent_info"] = parent_info

    # Recursively add information for each child
    for child in children:
        if child not in visited_nodes_all:
            add_node_info(root, graph, child, f"{node} -> {parent_info}")


def most_similar_string(string, string_set):
    min_distance = float('inf')
    most_similar_string = None

    for s in string_set:
        distance = Levenshtein.distance(string, s)
        if distance < min_distance:
            min_distance = distance
            most_similar_string = s

    return most_similar_string


def process_annotation(annotations):
    return "Service" in annotations or "Component" in annotations or "SI" in annotations


def process_resource_annotation(annotations):
    return "Autowired" in [obj.name for obj in annotations] or "Resource" in [obj.name for obj in
                                                                              annotations] or "SI" in [obj.name for
                                                                                                       obj in
                                                                                                       annotations]


def lazy(annotations):
    return "Lazy" in [obj.name for obj in annotations]


def parse_java_files(directory):
    G = nx.DiGraph()

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
                map_interface_impl[declaration.implements[0].name] = class_name
                class_name = declaration.implements[0].name
            else:
                # 展示最像当前类的接口
                old = class_name
                class_name = most_similar_string(class_name, [obj.name for obj in declaration.implements])
                map_interface_impl[class_name] = old
        else:
            # 就直接展示实现类
            class_name = class_name
            map_interface_impl[class_name] = class_name

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


def cat(son):
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
    return category


def start(rootPath):
    G = parse_java_files(rootPath)
    # 为每个节点添加信息,从第一个开始
    for node in G.nodes:
        add_node_info(node, G, node)

    # 调整 k 的值以控制节点之间的距离
    pos = nx.spring_layout(G, k=elastic_distance)

    # todo:调整，改成根据包路径来分类 [目前先安装依赖数量分类]
    for node in G.nodes:
        son = len(G.nodes[node]['children'])
        # 使用范围检查来判断 son 的取值范围
        category = cat(son)

        parent_path = ''
        children = []
        if len(G.nodes[node]) != 0:
            parent_path = G.nodes[node]['parent_info']
            children = G.nodes[node]['children']
        data = NodeData(node, node, (son + 1) * multiple, pos.get(node)[0], pos.get(node)[1], son, category,
                        parent_path,
                        children)
        nodes.append(data)

    # 拾取判断循环依赖

    node_dicts = [node.__dict__() for node in nodes]
    link_dicts = [link.__dict__() for link in links]
    res_dict = {'nodes': node_dicts, 'links': link_dicts, 'categories': categories}

    json_str = json.dumps(res_dict)
    print(f"当前项目全部依赖：\n {json_str}")
    file_path = 'json/' + project_name[2:] + '/' + project_name + '.json'

    folder_path_to_clear = 'json/' + project_name[2:] + '/'
    floder(f'json/{project_name[2:]}')
    delete_files_in_folder(folder_path_to_clear)
    with open(file_path, 'w') as f:
        f.write(json_str)
    # plt.show()

    # 生成每个服务节点的子节点JSON文件
    for node in G.nodes:
        child_G = nx.DiGraph()
        visited_nodes = {node}
        health = '😀'
        child_links = []
        child_node_data = []
        parent_path = ''
        health = generate_child_nodes_json(health, node, child_G, child_links, G, node, parent_path, visited_nodes)

        # 调整 k 的值以控制节点之间的距离
        pos = nx.spring_layout(child_G, k=elastic_distance)

        for children_node in visited_nodes:
            children_num = len(G.nodes[children_node]["children"])
            node_data = NodeData(children_node, children_node, (children_num + 1) * multiple, pos.get(children_node)[0],
                                 pos.get(children_node)[1], children_num,
                                 cat(children_num), parent_path, G.nodes[children_node]["children"])
            child_node_data.append(node_data)

        child_node_dict = [node.__dict__() for node in child_node_data]
        child_link_dicts = [link.__dict__() for link in child_links]
        child_res_dict = {'nodes': child_node_dict, 'links': child_link_dicts, 'categories': categories}

        child_json_str = json.dumps(child_res_dict)
        print("\n ====================== ")
        print("\n" + child_json_str)
        child_json_filename = f'json/{project_name[2:]}/{node}-{health}.json'
        with open(child_json_filename, 'w') as child_json_file:
            child_json_file.write(child_json_str)
        print(f"Child JSON file generated: {child_json_filename}")


class BreakOuterLoop(Exception):
    pass


def floder(folder_name):
    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"文件夹 '{folder_name}' 已创建成功。")
    else:
        print(f"文件夹 '{folder_name}' 已经存在。")


def generate_child_nodes_json(health, root, child_G, child_links, graph, parent_node, parent_path, visited_nodes):
    children_nodes = graph.nodes[parent_node]["children"]

    child_G.add_node(f"{parent_node}")
    # 遍历子节点
    for child_node in children_nodes:
        child_G.add_edge(f"{parent_node}", f"{child_node}")
        link = NodeLink(parent_node, child_node)
        child_links.append(link)
        if child_node == root:
            count = 0
            try:
                # 文件拾取[需要根据根节点到子根节点的链路，找存在Lazy与否]
                index = 0
                for root_chi, _, files in os.walk(rootPath):
                    for file_name in files:
                        children_nodes = graph.nodes[root]["children"]
                        split = parent_path.split("->")
                        split.append(str(parent_node))
                        a_list = [name.strip() for name in split if name.strip()]
                        b_list = [map_interface_impl.get(name) for name in a_list]
                        name_list = [name + ".java" for name in b_list]
                        if index < len(name_list):
                            if file_name.endswith(".java") and file_name == name_list[index]:
                                index = index + 1
                                file_path = os.path.join(root_chi, file_name)
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
                                                for field_declaration in node.fields:
                                                    index_of_file_name = name_list.index(file_name)
                                                    if map_interface_impl.get(field_declaration.type.name) is not None:
                                                        if map_interface_impl.get(
                                                                field_declaration.type.name) + '.java' in name_list and process_resource_annotation(
                                                            field_declaration.annotations) and lazy(
                                                            field_declaration.annotations):
                                                            res = file_name.rsplit('.', 1)[0] + '🍜'
                                                            if health == '😀':
                                                                health = '🎈' + res
                                                            else:
                                                                if res in health:
                                                                    health = health.replace(res, res + "🍜")
                                                                else:
                                                                    health = health + res
                                                            raise BreakOuterLoop  # 抛出自定义异常以跳出外层循环
            except BreakOuterLoop:
                count = 1
                pass
            if count == 0:
                res = map_interface_impl.get(str(parent_node)) + '🧨'
                if health == '😀':
                    health = '🎈' + res
                else:
                    if res in health:
                        health = health.replace(res, res + "🧨")
                    else:
                        health = health + res
        if child_node not in visited_nodes:
            visited_nodes.add(child_node)
            child_path = f"{parent_node} -> {parent_path}"

            # Check if the child node name is the same as the parent node
            if child_node == parent_node:
                continue  # Stop recursion for this child node

            health = generate_child_nodes_json(health, root, child_G, child_links, graph, child_node, child_path,
                                               visited_nodes)

    return health


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


def delete_files_in_folder(folder_path):
    # 获取文件夹中的所有文件名
    file_list = os.listdir(folder_path)

    # 遍历文件夹中的所有文件并删除
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(file_path):
                # 删除文件
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


# 下面是参考展示示例
# https://echarts.apache.org/examples/zh/editor.html?c=graph&lang=js
if __name__ == '__main__':
    # 填入你的java项目根目录绝对路径
    # 目前只扫描@Service 和@Component 类和它的@Autowired属性的关系以及裙带关系。
    rootPath = "D:\\data\\javaWork\\magicube-openapi"  # 支持面板填写（本地项目路径）
    pathZu = rootPath.split("\\")
    name = ''  # 支持面板填写（项目名称）
    elastic_distance = 1.8  # 支持面板填写（节点距离）
    multiple = 1  # 支持面板填写
    if name == '':
        name = pathZu[len(pathZu) - 1]
    project_name = '0-' + name
    start(rootPath)
