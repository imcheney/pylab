# -*- coding: utf-8 -*-
"""Component definition."""

import json
import logging
from collections import deque

import networkx as nx

_logger = logging.getLogger('world')


class Node(object):
    refmap = {}

    def __init__(self, x, y, **kwargs):
        self.x = x
        self.y = y
        self.id = None
        self.name = None
        self.attr = {}  # for future attributes
        for key in kwargs:
            self.attr[key] = kwargs.get(key)

    def add_id(self, id):
        self.id = str(id)
        Node.refmap[self.id] = self

    def __repr__(self):
        return '{}-({}, {})'.format(self.name, self.x, self.y)


class MapManager(object):
    """Everything related to nodes and the map"""
    def __init__(self):
        super(MapManager, self).__init__()

        self._graph = MapManager._create_graph()
        self._marks = {}

    def unmark_all(self, entity):
        if entity.eid in self._marks:
            pos_list = self._marks[entity.eid]
            self._marks[entity.eid] = []
        else:
            pos_list = []
            self._marks[entity.eid] = []
        return pos_list

    def mark_node(self, entity, pos_name):
        if entity.eid not in self._marks:
            self._marks[entity.eid] = []
        self._marks[entity.eid].append(pos_name)

    def is_on_map(self, pos_name):
        return pos_name in self._graph.nodes

    def unpin_map_position(self, entity, pos_name):
        if ('on_node' not in self._graph.nodes[pos_name]) or (not self._graph.nodes[pos_name]['on_node']):
            return
        self._graph.nodes[pos_name]['on_node'].remove(entity)

    def pin_map_position(self, entity, pos_name):
        if ('on_node' not in self._graph.nodes[pos_name]) or (not self._graph.nodes[pos_name]['on_node']):
            self._graph.nodes[pos_name]['on_node'] = []
        self._graph.nodes[pos_name]['on_node'].append(entity)

    # def is_surrounded(self, entity):
    #     """check if star is surrounded by fans."""
    #     if entity.tag != server_conf.TAG_STAR:
    #         raise ValueError("Entity should be a star to be surrounded.")
    #     if not self.get_move_nodes(entity.tag, entity.get_component(TransformComponent).position, 1):
    #         return False
    #     else:
    #         return True

    def get_shortest_path(self, source, target):
        """
        example: self.get_shortest_path('s_46', 's_47') --> ['s_46', 'f_52', 'f_53', 's_47']
        """
        return nx.shortest_path(self._graph, source, target)

    # def get_move_nodes(self, tag, pos, n):
    #     """Return a list of nodes."""
    #     if tag == server_conf.TAG_FANS:
    #         return self.get_available_nodes(pos, n, 'f', True, False) + [pos]
    #     else:
    #         return self.get_available_nodes(pos, n, 's', True, True)  # 但是不会被down的粉丝阻挡
    #
    # def get_attack_nodes(self, tag, pos, n):
    #     if tag == server_conf.TAG_FANS:
    #         return self.get_available_nodes(pos, n, 's', False, False)
    #     else:
    #         # if pos is special, attack_range += 1
    #         # if self._graph.nodes[pos]['special']:
    #         #     n += 1  # range+1
    #         # _logger.info('Star is on a special node! Attack range + 1!')
    #         return self.get_available_nodes(pos, n, 'f', True, False)

    def is_on_special_node(self, pos_name):
        _logger.info('---Star is on a special node! Attack range + 1!---')
        return self._graph.nodes[pos_name]['special']

    def get_route(self, dest):
        pos = dest
        route = deque([pos])
        while 'route_parent' in self._graph.nodes[pos] and self._graph.nodes[pos]['route_parent']:
            route.appendleft(self._graph.nodes[pos]['route_parent'])
            pos = self._graph.nodes[pos]['route_parent']
        return tuple(route)

    def get_available_nodes(self, cur_pos, n=1, kind='f', penetrate=True, blockable=False):
        """get available nodes in n step.

        :param cur_pos: current position

        :param n: number of steps

        :param kind: 'f' or 's' or 'sfh'(all nodes)

        :param penetrate: is penetrating(overlook) nodes of other kinds

        :param blockable: is enemy's standing on a node blocking me from pass it?

        :return: tuple of reachable nodes
        """
        if cur_pos not in self._graph:
            return tuple()
        reachable = []
        level = {cur_pos: 0}
        self._graph.nodes[cur_pos]['route_parent'] = None
        Q = [cur_pos]
        visited = set()
        visited.add(cur_pos)
        while Q:
            v = Q.pop(0)
            if level[v] >= n:
                break
            self._visit_neighbors(v, v, kind, Q, visited, reachable, level, penetrate, blockable)
        return reachable

    def _visit_neighbors(self, vertex, level_parent, kind, queue, visited, reachable, level_dict, penetrate=True, blockable=False):
        for u in self._graph.adj[vertex].keys():
            if u in visited:
                continue
            visited.add(u)
            if u[0] not in kind and penetrate:
                if blockable and self._check_is_blocked(u):  # give up this
                    pass
                else:  # keep finding
                    self._graph.nodes[u]['route_parent'] = vertex
                    self._visit_neighbors(u, level_parent, kind, queue, visited, reachable, level_dict, penetrate, blockable)
            if u[0] in kind:  # good node
                self._graph.nodes[u]['route_parent'] = vertex
                level_dict[u] = level_dict[level_parent] + 1
                queue.append(u)
                reachable.append(u)

    def _check_is_blocked(self, pos_name):
        if 'on_node' in self._graph.nodes[pos_name]:
            for entity in self._graph.nodes[pos_name]['on_node']:
                if entity.tag == 2:
                    return True
        return False

    @staticmethod
    def _create_graph():
        """create a full-fledged graph for usage"""
        raw = MapManager._read_map('graph final.json')
        N, E = MapManager._prepare_data(raw)
        MapManager._assign_name(N)
        G = nx.Graph()
        for y in N:
            for node in N[y]:
                G.add_node(node.name, x=node.x, y=node.y, mark='NA', special=False)
        # for f_node, s_node in server_conf.GDC["special_building_nodes"].itervalues():  # set special-building nodes
        #     G.nodes[f_node]['special'] = True
        #     G.nodes[s_node]['special'] = True
        _logger.debug('G.nodes(data=True): {}'.format(G.nodes(data=True)))
        for e in E:
            from_refId = str(e['from']['_ref'])
            to_refId = str(e['to']['_ref'])
            G.add_edge(Node.refmap[from_refId].name, Node.refmap[to_refId].name)
        _logger.info('mapx - game map graph created.')
        return G

    @staticmethod
    def dump_named_graph_to_json():
        """from raw.json to named_graph.json"""
        d = MapManager._read_map('graph final.json')
        N, E = MapManager._prepare_data(d)
        MapManager._assign_name(N)
        MapManager._insert_name_to_json(d)

    @staticmethod
    def _read_map(path):
        with open(path, 'r') as f:
            s = f.read()
            return json.loads(s)

    @staticmethod
    def _prepare_data(raw):
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
                    raise ValueError()

                if y not in N:
                    N[y] = []
                N[y].append(node)
            elif e['_className'] == 'Q.Edge':
                E.append(e['json'])
            else:
                raise Exception()
        sorted_key_list = sorted(N)
        for k in sorted_key_list:
            N[k] = sorted(N[k], key=lambda node: node.x)
        return N, E

    @staticmethod
    def _assign_name(N):
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
        _logger.debug('f has {}'.format(f_index - 1))
        _logger.debug('s has {}'.format(s_index - 1))
        _logger.debug('h has {}'.format(h_index - 1))

    @staticmethod
    def _insert_name_to_json(raw):
        """create named_graph.json with name assigned N"""
        for e in raw['datas']:
            if e['_className'] == 'Q.Node':
                e['json']['name'] = Node.refmap[e['_refId']].name
        with open('named_graph_{}.json'.format('0'), 'w') as f:
            f.write(json.dumps(raw))


if __name__ == '__main__':
    mm = MapManager()
