import itertools
import json

import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from pandas import array as pd_array
from scipy import special as math

from node import Node
from connection import Connection
from lightpath import Lightpath
from line import Line
from signal_information import SignalInformation


def distance_node(xy_node1, xy_node2):
    dx = (xy_node2[0] - xy_node1[0]) ** 2
    dy = (xy_node2[1] - xy_node1[1]) ** 2
    return (dx + dy) ** (1 / 2)


def path_to_line(path):
    path = path.replace('-->', '')
    return set([path[i] + path[i + 1] for i in range(len(path) - 1)])


def line_set_to_path(line_set):
    path = ""
    elements = list(itertools.permutations(list(line_set), len(list(line_set))))
    for i in range(len(elements)):
        flag = 1
        for j in range(len(elements[i]) - 1):
            if elements[i][j][1] != elements[i][j + 1][0]:
                flag = 0
            j += 2
        if flag == 1:
            for j in range(len(elements[i])):
                path += elements[i][j][0]
            return path


class Network(object):
    def __init__(self, json_path, transceiver='fixed_rate'):
        # load the file in a json variable
        with open(json_path) as json_file:
            data = json.load(json_file)
            # empty struct dict
            self._nodes = dict()
            self._lines = dict()
            self._weighted_paths = None
            self._connected = False
            self._route_space = None
            # json file--> dict, load in dict node's label --> init Node
            for node_label in data:
                node_dict = data[node_label]
                node_dict['label'] = node_label.upper()
                self._nodes[node_label] = Node(node_dict)
                if 'transceiver' not in data[node_label].keys():
                    self._nodes[node_label].transceiver = transceiver
                else:
                    self._nodes[node_label].transceiver = data[node_label]['transceiver']
                for adj_node_label in node_dict['connected_nodes']:
                    line_dict = dict()
                    line_label = node_label.upper() + adj_node_label.upper()
                    line_dict['label'] = line_label
                    line_dict['length'] = distance_node(data[node_label]['position'], data[adj_node_label]['position'])
                    self._lines[line_label] = Line(line_dict)

    @property
    def nodes(self):
        return self._nodes

    # connect the network --> dict
    def connect(self):
        nodes_dict = self._nodes
        lines_dict = self._lines
        switching_matrix = {}
        for node_label in nodes_dict:
            node = nodes_dict[node_label]
            for connected_node in node.connected_nodes:
                inner_dict = {connected_node: np.zeros(10)}
                for connected_node2 in node.connected_nodes:
                    if connected_node2 != connected_node:
                        dict_tmp = {connected_node2: np.ones(10)}
                        inner_dict.update(dict_tmp)
                switching_matrix.update({connected_node: inner_dict})
                line_label = node_label + connected_node
                line = lines_dict[line_label]
                line.successive[connected_node] = nodes_dict[connected_node]
                node.successive[line_label] = lines_dict[line_label]
            node.switching_matrix = switching_matrix
            switching_matrix = {}
        self._connected = True
    
    def find_paths(self, label1, label2):
        cross_nodes = [key for key in self._nodes.keys()
                       if ((key != label1) & (key != label2))]
        cross_lines = self._lines.keys()
        inner_paths = {'0': label1}
        for i in range(len(cross_nodes) + 1):
            inner_paths[str(i + 1)] = []
            for inner_path in inner_paths[str(i)]:
                inner_paths[str(i + 1)] += [
                    inner_path + cross_node
                    for cross_node in cross_nodes
                    if ((inner_path[-1] + cross_node in cross_lines) &
                        (cross_node not in inner_path))]
        paths = []
        for i in range(len(cross_nodes) + 1):
            for path in inner_paths[str(i)]:
                if path[-1] + label2 in cross_lines:
                    paths.append(path + label2)
        return paths

    def propagate(self, lightpath, occupation=False):
        path = lightpath.path
        first_node = self._nodes[path[0]]
        prop_s_i = first_node.propagate(lightpath, occupation)
        return prop_s_i
    
    def draw(self):
        font = {'family': 'serif',
                'color': 'blue',
                'weight': 'normal',
                'size': 15
                }
        for node_label in self._nodes:
            n0 = self._nodes[node_label]
            x0 = n0.position[0] / 1e3
            y0 = n0.position[1] / 1e3
            plt.plot(x0, y0)
            plt.text(x0, y0, node_label, fontdict=font)
            for connect_n_label in n0.connected_nodes:
                n1 = self._nodes[connect_n_label]
                x1 = n1.position[0] / 1e3
                y1 = n1.position[1] / 1e3
                plt.plot([x0, x1], [y0, y1])
        plt.xlabel('Km')
        plt.title('Network')
        plt.show()

    def set_weighted_paths(self, signal_power):
        if not self._connected:
            self.connect()
        all_couples = []
        for label1 in self._nodes.keys():
            for label2 in self._nodes.keys():
                if label2 != label1:
                    all_couples.append(label1 + label2)
        df = DataFrame()
        paths = []
        latencies = []
        noises = []
        snrs = []
        for couples in all_couples:
            for path in self.find_paths(couples[0], couples[1]):
                path_str = ''
                for node in path:
                    path_str += node + '-->'
                paths.append(path_str[:-3])
                s_i = SignalInformation(signal_power, path)
                if couples in self._lines.keys():
                    line = self._lines[couples]
                    signal_power = line.optimized_launch_power()
                s_i.signal_power = signal_power
                s_i = self.propagate(s_i, occupation=False)
                latencies.append(s_i.latency)
                noises.append(s_i.noise_power)
                snrs.append(10 * np.log10(s_i.latency / s_i.noise_power))
        df['path'] = paths
        df['latency'] = latencies
        df['noise'] = noises
        df['snr'] = snrs
        self._weighted_paths = df

        # set the route space free
        route_space = DataFrame()
        route_space['path'] = paths
        for i in range(10):  # every line has 10 channel
            route_space[str(i)] = ['free'] * len(paths)
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
        available_path = self.available_paths(start_node, final_node)
        if available_path:
            inout_df = self._weighted_paths.loc[
                self._weighted_paths.path.isin(available_path)]
            best_snr = np.max(inout_df.snr.values)
            best_path = inout_df.loc[
                inout_df.snr == best_snr].path.values[0]
        else:
            best_path = None
        return best_path

    def find_best_latency(self, start_node, final_node):
        available_path = self.available_paths(start_node, final_node)
        if available_path:
            inout_df = self._weighted_paths.loc[
                self._weighted_paths.path.isin(available_path)]
            best_latency = np.min(inout_df.latency.values)
            best_path = inout_df.loc[
                inout_df.latency == best_latency].path.values[0]
        else:
            best_path = None
        return best_path

    #  for each element of connections set the attribute latency or snr (latency by default)
    def stream(self, connections, best='latency'):
        streamed_connections = list()
        for connection in connections:
            if best == 'latency':
                path = self.find_best_latency(connection.start_node, connection.final_node)
            elif best == 'snr':
                path = self.find_best_snr(connection.start_node, connection.final_node)
            else:
                print('ERROR INPUT VALUE:', best)
                continue
            if path:
                path_occupancy = self._route_space.loc[self._route_space.path == path].T.values[1:]
                channel = [i for i in range(len(path_occupancy))
                           if path_occupancy[i] == 'free'][0]
                lightpath = Lightpath(connection.signal_power, path, channel)
                rb = self.calculate_bit_rate(lightpath, self._nodes[connection.start_node].transceiver)
                if rb == 0:
                    continue
                else:
                    connection.bit_rate = rb
                path_occupancy = self._route_space.loc[self._route_space.path == path].T.values[1:]
                channel = [i for i in range(len(path_occupancy))
                           if path_occupancy[i] == 'free'][0]
                path = path.replace('-->', '')
                in_lightpath = Lightpath(connection.signal_power, path, channel)
                out_lightpath = self.propagate(in_lightpath, True)
                connection.latency = out_lightpath.latency
                connection.snr = 10 * np.log10(in_lightpath.signal_power / out_lightpath.noise_power)
                self.update_route_space(path, channel)
            else:
                connection.latency = 0
                connection.snr = 0
            streamed_connections.append(connection)
        return streamed_connections

    def update_route_space(self, path, channel):
        all_paths = [path_to_line(p) for p in self._route_space.path.values]
        states = self._route_space[str(channel)]
        lines = path_to_line(path)
        for i in range(len(all_paths)):
            line_set = all_paths[i]
            if lines.intersection(line_set):
                states[i] = 'occupied'
                path_to_update = line_set_to_path(line_set)
                for j in range(len(path_to_update)):
                    if j not in (0, len(path_to_update) - 1):
                        if ((path_to_update[j - 1] in self._nodes[path_to_update[j]].connected_nodes) & (
                                path_to_update[j + 1] in self._nodes[path_to_update[j]].connected_nodes)):
                            self._nodes[path_to_update[j]].switching_matrix[path_to_update[j - 1]][
                                path_to_update[j + 1]][
                                channel] = 0
        self._route_space[str(channel)] = states

    def calculate_bit_rate(self, lightpath, strategy):
        ber_t = 1e-3
        bn = 12.5e9  # noise bandwidth
        rs = lightpath.rs
        path = lightpath.path
        rb = 0
        gsnr_db = pd_array(self._weighted_paths.loc[self._weighted_paths['path'] == path]['snr'])[0]
        gsnr = 10 ** (gsnr_db / 10)
        if strategy == 'fixed_rate':
            if gsnr >= 2 * ((math.erfcinv(2 * ber_t)) ** 2) * (rs / bn):
                rb = 100
            else:
                rb = 0
        if strategy == 'flex_rate':
            if gsnr < 2 * ((math.erfcinv(2 * ber_t)) ** 2) * (rs / bn):
                rb = 0
            elif (gsnr >= 2 * ((math.erfcinv(2 * ber_t)) ** 2) * (rs / bn)) and (
                    gsnr < (14 / 3) * ((math.erfcinv((3 / 2) * ber_t)) ** 2) * (rs / bn)):
                rb = 100
            elif (gsnr >= (14 / 3) * ((math.erfcinv((3 / 2) * ber_t)) ** 2) * (rs / bn)) and (
                    gsnr < 10 * ((math.erfcinv((8 / 3) * ber_t)) ** 2) * (rs / bn)):
                rb = 200
            elif gsnr >= 10 * ((math.erfcinv((8 / 3) * ber_t)) ** 2) * (rs / bn):
                rb = 400
        if strategy == 'shannon':
            rb = 2 * rs * np.log2(1 + bn / rs * gsnr) / 1e9
        return rb

    def upgrade_traffic_matrix(self, mtx, node_a, node_b):
        nodes = list(self._nodes.keys())
        nodes.sort()
        a = nodes.index(node_a)
        b = nodes.index(node_b)
        connection = Connection(node_a, node_b, 1e-3)
        list_con = [connection]
        self.stream(list_con)
        btr = connection.bit_rate
        if btr == 0:
            mtx[a][b] = float('inf')
            return float('inf')
        mtx[a][b] -= btr
        return mtx[a][b]
    
    def free_space(self):
        states = ['free' for _ in range(len(self._route_space['path']))]
        for line in self._lines.values():
            line.free_state()
        for i in range(10):
            self._route_space[str(i)] = states
