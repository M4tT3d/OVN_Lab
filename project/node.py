class Node:
    def __init__(self, data):
        self._label = data['label']
        self._position = data['position']
        self._connected_nodes = data['connected_nodes']
        self._successive = dict()
        self._switching_matrix = None
        self._transceiver = ''

    @property
    def label(self):
        return self._label

    @property
    def position(self):
        return self._position

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, value):
        self._successive = value

    @property
    def switching_matrix(self):
        return self._switching_matrix

    @switching_matrix.setter
    def switching_matrix(self, value):
        self._switching_matrix = value

    @property
    def transceiver(self):
        return self._transceiver

    @transceiver.setter
    def transceiver(self, value):
        self._transceiver = value

    #  update a signal information object modifying its path attribute
    #  and call the successive element  propagate method
    def propagate(self, lightpath, occupation=False):
        path = lightpath.path  # signal information--> path
        if len(path) > 1:
            line_label = path[:2]  # the 1st and the 2nd element of path
            lightpath.next_node()
            lightpath = self.successive[line_label].propagate(lightpath, occupation)
        return lightpath
