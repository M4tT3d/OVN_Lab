class Node:
    def __init__(self, data):
        self._label = data['label']
        self._position = tuple(data['position'])
        self._connected_nodes = data['connected_nodes']
        self._successive = dict()
        self._switching_matrix = None

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @property
    def position(self):
        return self._position

    @property
    def switching_matrix(self):
        return self._switching_matrix

    @switching_matrix.setter
    def switching_matrix(self, matrix):
        self._switching_matrix = matrix

    def propagate(self, signal, occupation=False):
        if len(signal.path) > 1:
            line_label = signal.path[:2]
            signal.next_node()
            signal = self._successive[line_label].propagate(signal, occupation)
        return signal
