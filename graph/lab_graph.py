# -*- coding: utf-8 -*-
"""Implemented as it is"""
import json
import unittest

import networkx as nx


def lab_graph_create():
    G = nx.Graph()
    G.add_node('s_1')
    G.add_node('f_1')
    print G.nodes
    # 需求1: 图的结点可以类似对象一样附着数据
    G.add_node('f_2', special='test1')
    print G.nodes
    print G.nodes['f_2']['special']
    print '+++G', G.nodes['f_2'], 'special' in G.nodes['f_2']
    print 'G.nodes(data=True)', G.nodes(data=True)
    G.add_edge('s_1', 'f_1', w=5)
    G.add_edge('s_1', 'f_2')
    print G.edges.data()
    # 需求2: 寻找相邻结点
    print G.adj['s_1'], type(G.adj['s_1'])
    print G.adj['s_1']['f_1']
    print 'f_2' in G.adj['s_1']
    # 需求3: 导出为link_dict
    # 需求4: 从GD给的json导入为graph


def read_map(path):
    with open(path, 'r') as f:
        s = f.read()
        return json.loads(s)


class Node(object):
    refmap = {}

    def __init__(self, x, y, **kwargs):
        self.x = x
        self.y = y
        self.id = None
        self.name = None
        self.attr = {}
        for key in kwargs:
            self.attr[key] = kwargs.get(key)

    def add_id(self, id):
        self.id = str(id)
        Node.refmap[self.id] = self

    def __repr__(self):
        return '{}-({}, {})'.format(self.name, self.x, self.y)


class MyUnitTest(unittest.TestCase):
    def test_node(self):
        n = Node(5, 10, sex='male')
        print n.x, n.y, n.attr['sex']
        self.assertEquals(n.attr['sex'], 'male')


def prepare_data(raw):
    """从raw字典中创建N, E"""
    N = {}
    E = []
    for e in raw['datas']:
        if e['_className'] == 'Q.Node':
            # print e
            x = e['json']['location']['x']
            y = e['json']['location']['y']
            node = Node(x, y)
            node.add_id(e['_refId'])  # str id
            if e['json']['image'] == 'Group':
                node.name = 'f_'
            elif e['json']['image'] == 'Q-server':
                node.name = 's_'
            elif e['json']['image'] == 'lamp':
                node.name = 'h_'
            else:
                raise ValueError

            if y not in N:
                N[y] = []
            N[y].append(node)
        elif e['_className'] == 'Q.Edge':
            E.append(e['json'])
        else:
            raise Exception
    sorted_key_list = sorted(N)
    for k in sorted_key_list:
        N[k] = sorted(N[k], key=lambda node: node.x)
    return N, E


def assign_name(N):
    """Assign name for N"""
    f_index = 1
    s_index = 1
    h_index = 1
    sorted_key_list = sorted(N)
    for k in sorted_key_list:
        for node in N[k]:
            if node.name[0] == 'f':
                node.name += str(f_index)
                f_index += 1
            elif node.name[0] == 's':
                node.name += str(s_index)
                s_index += 1
            else:
                node.name += str(h_index)
                h_index += 1
    print 'f has {}'.format(f_index - 1)
    print 's has {}'.format(s_index - 1)
    print 'h has {}'.format(h_index - 1)


def insert_name_to_json(raw):
    """create named_graph.json with name assigned N"""
    for e in raw['datas']:
        if e['_className'] == 'Q.Node':
            e['json']['name'] = Node.refmap[e['_refId']].name
    with open('named_graph_{}.json'.format('0'), 'w') as f:
        f.write(json.dumps(raw))


def dump_named_graph_json():
    """from raw.json to named_graph.json"""
    d = read_map('graph final.json')
    N, E = prepare_data(d)
    assign_name(N)
    insert_name_to_json(d)


def create_graph():
    """create a full-fledged graph for usage"""
    raw = read_map('graph final.json')
    N, E = prepare_data(raw)
    assign_name(N)
    G = nx.Graph()
    for y in N:
        for node in N[y]:
            G.add_node(node.name, x=node.x, y=node.y, mark='NA')
    print G.nodes(data=True)
    for e in E:
        from_refId = str(e['from']['_ref'])
        to_refId = str(e['to']['_ref'])
        G.add_edge(Node.refmap[from_refId].name, Node.refmap[to_refId].name)
    return G


class NodeManager(object):
    def __init__(self, graph):
        if isinstance(graph, nx.Graph):
            self._graph = graph
        else:
            raise ValueError

    def get_accessible_nodes(self, cur_pos, n=1, kind='f'):
        """get available nodes in n step, not penetration

        :param cur_pos: current position

        :param n: number of steps

        :param kind: 'f' or 's' or 'sfh'(all nodes)

        :return: tuple of reachable nodes
        """
        if cur_pos not in self._graph:
            return tuple()
        reachable = []
        level = {cur_pos: 0}
        Q = [cur_pos]
        visited = set()
        while Q:
            v = Q.pop(0)
            if level[v] >= n:
                break
            for u in self._graph.adj[v].keys():
                if u in visited:
                    continue
                visited.add(u)
                if u[0] in kind:
                    level[u] = level[v] + 1
                    Q.append(u)
                    reachable.append(u)
        return tuple(reachable)

    def get_available_nodes(self, cur_pos, n=1, kind='f', penetrate=True):
        """get available nodes in n step

        :param cur_pos: current position

        :param n: number of steps

        :param kind: 'f' or 's' or 'sfh'(all nodes)

        :param penetrate: is penetrating(overlook) nodes of other kinds

        :return: tuple of reachable nodes
        """
        if cur_pos not in self._graph:
            return tuple()
        reachable = []
        level = {cur_pos: 0}
        Q = [cur_pos]
        visited = set()
        visited.add(cur_pos)
        while Q:
            v = Q.pop(0)
            if level[v] >= n:
                break
            self._visit_neighbors(v, v, kind, Q, visited, reachable, level, penetrate)
        return tuple(reachable)

    def _visit_neighbors(self, vertex, parent, kind, queue, visited, reachable, level_dict, penetrate=True):
        for u in self._graph.adj[vertex].keys():
            if u in visited:
                continue
            visited.add(u)
            if u[0] not in kind and penetrate:
                self._visit_neighbors(u, parent, kind, queue, visited, reachable, level_dict, penetrate)
            if u[0] in kind:
                level_dict[u] = level_dict[parent] + 1
                queue.append(u)
                reachable.append(u)

    # def get_reachable_nodes_pass_mode(self, cur_pos, n=1, kind='f'):
    #     """get reachable nodes in penetration mode
    #     :param cur_pos:
    #     :param n:
    #     :param kind:
    #     :return:
    #     """
    #     if cur_pos not in self._graph:
    #         return tuple()
    #     reachable = []
    #     level = {cur_pos: 0}
    #     Q = [cur_pos]
    #     visited = set()
    #     visited.add(cur_pos)
    #     while Q:
    #         v = Q.pop(0)
    #         if level[v] >= n:
    #             break
    #         self._visit_linked_nodes(v, v, kind, Q, visited, reachable, level)
    #     return tuple(reachable)
    #
    # def _visit_linked_nodes(self, vertex, parent, kind, queue, visited, reachable, level_dict):
    #     for u in self._graph.adj[vertex].keys():
    #         if u in visited:
    #             continue
    #         visited.add(u)
    #         if u[0] not in kind:
    #             self._visit_linked_nodes(u, parent, kind, queue, visited, reachable, level_dict)
    #         else:
    #             level_dict[u] = level_dict[parent] + 1
    #             queue.append(u)
    #             reachable.append(u)


if __name__ == '__main__':
    G = create_graph()
    # print G.edges
    # nm = NodeManager(G)
    # print nm.get_available_nodes('s_46', 3, 'f')
    # print nm.get_reachable_nodes_pass_mode('s_46', 2, 'f')
    # print nm.get_available_nodes('s_46', 4, 'f', penetrate=True)
    lab_graph_create()
