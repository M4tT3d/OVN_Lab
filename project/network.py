import json

import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame

from lightpath import Lightpath
from line import Line
from node import Node


def distance_node(xy_node1, xy_node2):
    dx = (xy_node2[0] - xy_node1[0]) ** 2
    dy = (xy_node2[1] - xy_node1[1]) ** 2
    return (dx + dy) ** (1 / 2)


def path_to_line(path):
    path = path.replace("->", "")
    return [path[i] + path[i + 1] for i in range(len(path) - 1)]


class Network:
    def __init__(self, json_path):
        with open(json_path) as json_file:
            data = json.load(json_file)
            self._nodes = dict()
            self._lines = dict()
            self._weighted_paths = None
            self._connected = False
            self._route_space = None
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
        self._connected = True

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

    def propagate(self, signal, occupation=False):
        return self._nodes[signal.path[0]].propagate(signal, occupation)

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

    def set_weighted_paths(self, signal_power):
        pairs = []
        df_data = dict(zip(["path", "latency", "noise", "SNR"], [[], [], [], []]))
        if not self._connected:
            self.connect()
        for nodeLabel in self._nodes.keys():
            for nodeLabel2 in self._nodes.keys():
                if nodeLabel != nodeLabel2:
                    pairs.append(nodeLabel + nodeLabel2)
        for pair in pairs:
            for path in self.find_paths(pair[0], pair[1]):
                path_label = ""
                for i in range(len(path)):
                    if i == (len(path) - 1):
                        path_label += path[i]
                    else:
                        path_label += path[i] + "->"
                df_data['path'].append(path_label)
                sig = self.propagate(Lightpath(signal_power, path, 0))
                df_data['latency'].append(sig.latency)
                df_data['noise'].append(sig.noise_power)
                df_data['SNR'].append(10 * np.log10(sig.signal_power / sig.noise_power))
        self._weighted_paths = DataFrame(df_data)
        route_space = DataFrame()
        route_space['path'] = df_data['path']
        for i in range(10):
            route_space[str(i)] = ['free' for i in range(len(df_data['path']))]
        self._route_space = route_space

    def available_paths(self, start_node, final_node):
        if self._weighted_paths is None:
            self.set_weighted_paths(1)
        paths = [path for path in self._weighted_paths['path'].values if
                 (start_node.upper() == path[0]) and (final_node.upper() == path[-1])]
        available_paths = list()
        for path in paths:
            free_path_channels = self._route_space.loc[self._route_space.path == path].T.values[1:]
        if 'free' in free_path_channels:
            available_paths.append(path)
        return available_paths

    def find_best_snr(self, start_node, final_node):
        paths = self.available_paths(start_node, final_node)
        if paths:
            best_snr = self._weighted_paths.loc[self._weighted_paths.path.isin(paths)].SNR.values.max()
            best_path = self._weighted_paths.loc[best_snr == self._weighted_paths.SNR].path.values[0]
            return best_path
        return None

    def find_best_latency(self, start_node, final_node):
        paths = self.available_paths(start_node, final_node)
        if paths:
            best_latency = self._weighted_paths.loc[self._weighted_paths.path.isin(paths)].latency.values.min()
            best_path = self._weighted_paths.loc[best_latency == self._weighted_paths.latency].path.values[0]
            return best_path
        return None

    def stream(self, connections, best="latency"):
        streamed_conn = list()
        for connection in connections:
            if best == "latency":
                path = self.find_best_latency(connection.start_node, connection.final_node)
            elif best == "snr":
                path = self.find_best_snr(connection.start_node, connection.final_node)
            if path:
                free_path_channels = self._route_space.loc[self._route_space.path == path].T.values[1:]
                for i in range(len(free_path_channels)):
                    if free_path_channels[i] == "free":
                        channel = i
                        break
                signal = self.propagate(Lightpath(connection.signal_power, path.replace("->", ""), channel), True)
                connection.latency = signal.latency
                connection.snr = 10 * np.log10(connection.signal_power / signal.noise_power)
                self.update_route_space(path, channel)
            else:
                connection.snr = 0
                connection.latency = None
            streamed_conn.append(connection)
        return streamed_conn

    def update_route_space(self, path, channel):
        paths = [path_to_line(path) for path in self._route_space.path.values]
        channel_state = self._route_space[str(channel)]
        signal_path = path_to_line(path)
        for i in range(len(paths)):
            path = paths[i]
            for line in signal_path:
                if line in path:
                    channel_state[i] = "occupied"
                    break
        self._route_space[str(channel)] = channel_state
