class Node:
    def __init__(self, data):
        self._label = data['label']
        self._position = tuple(data['position'])
        self._connected_nodes = data['connected_nodes']
        self._successive = dict()

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @property
    def position(self):
        return self._position

    def propagate(self, signal, occupation=False):
        if len(signal.path) > 1:
            line_label = signal.path[:2]
            signal.next_node()
            signal = self._successive[line_label].propagate(signal, occupation)
        return signal
