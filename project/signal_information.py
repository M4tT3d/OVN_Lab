class SignalInformation:
    def __init__(self, signal_power, path):
        self._signal_power = signal_power
        self._noise_power = 0
        self._latency = 0
        self._path = path

    @property
    def path(self):
        return self._path

    @property
    def signal_power(self):
        return self._signal_power

    @property
    def latency(self):
        return self._latency

    @property
    def noise_power(self):
        return self._noise_power
    
    def add_latency(self, latency):
        self._latency += latency

    def add_noise(self, noise):
        self._noise_power += noise

    def next_node(self):
        self._path = self._path[1:]
