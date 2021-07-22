from scipy.constants import speed_of_light


class Line:
    def __init__(self, data):
        self._label = data['label']
        self._length = data['length']
        self._successive = dict()

    @property
    def successive(self):
        return self._successive

    def latency_generation(self):
        return self._length / (speed_of_light * 2 / 3)

    def noise_generation(self, signal_power):
        return 1e-9 * signal_power * self._length

    def propagate(self, signal):
        signal.add_noise(self.noise_generation(signal.signal_power))
        signal.add_latency(self.latency_generation())
        return self._successive[signal.path[0]].propagate(signal)