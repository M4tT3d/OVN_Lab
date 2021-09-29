class Connection:
    def __init__(self, start_node, final_node, signal_power):
        self._start_node = start_node
        self._final_node = final_node
        self._signal_power = signal_power
        self._snr = 0
        self._latency = 0
        self._rb = 0

    @property
    def start_node(self):
        return self._start_node

    @property
    def final_node(self):
        return self._final_node

    @property
    def signal_power(self):
        return self._signal_power

    @property
    def latency(self):
        return self._latency

    @property
    def snr(self):
        return self._snr

    @latency.setter
    def latency(self, latency):
        self._latency = latency

    @snr.setter
    def snr(self, snr):
        self._snr = snr

    @property
    def bit_rate(self):
        return self._rb

    @bit_rate.setter
    def bit_rate(self, rb):
        self._rb = rb
