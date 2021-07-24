import math

from scipy.constants import speed_of_light, h, pi


class Line:
    def __init__(self, data):
        self._label = data['label']
        self._length = data['length']
        self._successive = dict()
        self._state = ['free' for _ in range(10)]
        self._n_amplifiers = int(self._length / 80e3)  # one amp every 80km
        self._gain = 16
        self._noise_figure = 3  # 5#
        self._fiber = {
            "alpha": 0.2e-3 / (20 * math.log10(math.e)),
            "beta": 2.13e-26,
            "gamma": 1.27e-3,
            "Rs": 32e9,
            "df": 50e9
        }

    @property
    def successive(self):
        return self._successive

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        state = [s.lower().strip() for s in state]
        if set(state).issubset(set(['free', 'occupied'])):
            self._state = state
        else:
            print('ERROR: line state not recognized.Value: ', set(state) - set(['free', 'occupied']))

    def latency_generation(self):
        return self._length / (speed_of_light * 2 / 3)

    def noise_generation(self, lightpath):
        noise = self.ase_generation() + self.nli_generation(lightpath.signal_power)
        return noise

    def propagate(self, lightpath, occupation=False):
        lightpath.add_noise(self.noise_generation(lightpath))
        lightpath.add_latency(self.latency_generation())
        lightpath.signal_power = self.optimized_launch_power()
        if occupation:
            channel = lightpath.channel
            new_state = self.state.copy()
            new_state[channel] = 'occupied'
            self.state = new_state
        return self.successive[lightpath.path[0]].propagate(lightpath, occupation)

    def ase_generation(self):
        nf = 10 ** (self._noise_figure / 10)
        gain = 10 ** (self._gain / 10)
        f = 193.414e12
        bn = 12.5e9  # GHz
        return self._n_amplifiers * (h * f * bn * nf * (gain - 1))

    def n_nli(self):
        alpha = self._fiber['alpha']
        beta = self._fiber['beta']
        gamma = self._fiber['gamma']
        rs = self._fiber['Rs']
        df = self._fiber['df']
        first = 16 / (27 * pi)
        arg = ((pi ** 2) / 2) * ((beta * (rs ** 2)) / alpha) * (10 ** (2 * rs / df))
        second = math.log2(arg)
        third = (gamma ** 2) / (4 * alpha * beta * (rs ** 3))
        return first * second * third

    def nli_generation(self, signal_power):
        bn = 12.5e9  # GHz
        return (signal_power ** 3) * self.n_nli() * bn * self._n_amplifiers

    def optimized_launch_power(self):
        bn = 12.5e9
        return (self.ase_generation() / (2 * self.n_nli() * self._n_amplifiers * bn)) ** (1 / 3)

    def free_state(self):
        self._state = ['free' for _ in range(10)]
