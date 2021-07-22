import json

import matplotlib.pyplot as plt

from line import Line
from node import Node


def distance_node(xy_node1, xy_node2):
    dx = (xy_node2[0] - xy_node1[0]) ** 2
    dy = (xy_node2[1] - xy_node1[1]) ** 2
    return (dx + dy) ** (1 / 2)


class Network:
    def __init__(self, json_path):
        with open(json_path) as json_file:
            data = json.load(json_file)
            self._nodes = dict()
            self._lines = dict()
            for node_label in data:
                node_data = data[node_label]
                node_data['label'] = node_label.upper()
                self._nodes[node_label] = Node(node_data)
                for adj_node_label in data[node_label]['connected_nodes']:
                    line_dict = dict()
                    line_label = node_label.upper() + adj_node_label.upper()
                    line_dict['label'] = line_label
                    line_dict['length'] = distance_node(data[node_label]['position'], data[adj_node_label]['position'])
                    self._lines[line_label] = Line(line_dict)

    @property
    def nodes(self):
        return self._nodes

    def connect(self):
        for node_label in self._nodes:
            for adj_node_label in self._nodes[node_label].connected_nodes:
                line_label = node_label + adj_node_label
                self._lines[line_label].successive[adj_node_label] = self._nodes[adj_node_label]
                self._nodes[node_label].successive[line_label] = self._lines[line_label]

    def _search_all_paths(self, first_node, last_node, visited, path, paths):
        visited[first_node] = True
        path.append(first_node)

        if first_node == last_node:
            label = ""
            for i in path:
                label += i
            paths.append(label)
            return
        for adj_node in self._nodes[first_node].connected_nodes:
            if not visited[adj_node]:
                self._search_all_paths(adj_node, last_node, visited.copy(), path.copy(), paths)

    def find_paths(self, first_node, last_node):
        visited = dict()
        for i in self._nodes.keys():
            visited[i] = False
        path = []
        paths = []
        self._search_all_paths(first_node.upper(), last_node.upper(), visited, path, paths)
        return paths

    def propagate(self, signal):
        return self._nodes[signal.path[0]].propagate(signal)

    def draw(self):
        for nodeLabel in self._nodes:
            x = self._nodes[nodeLabel].position[0]
            y = self._nodes[nodeLabel].position[1]
            plt.plot(x, y, 'go', markersize=10)
            plt.text(x + 25, y + 25, nodeLabel)
            for adjNode in self._nodes[nodeLabel].connected_nodes:
                x1 = self._nodes[adjNode].position[0]
                y1 = self._nodes[adjNode].position[1]
                plt.plot([x, x1], [y, y1], 'b-', linewidth=1)
        plt.title('Network')
        plt.show()
