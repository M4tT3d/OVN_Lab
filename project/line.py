import numpy as np
from scipy.constants import speed_of_light, h, pi


class Line:
    def __init__(self, data):
        self._label = data['label']
        self._length = data['length']
        self._successive = dict()
        self._state = ["free" for i in range(10)]
        self._n_amplifiers = int(self._length / 80e3)  # one amp every 80km
        self._gain = 16
        self._noise_figure = 3
        self._alpha = 0.2e-3  # fiber loss dB/m
        self._beta2 = 2.13e-26  # 0.6e-26  #
        self._gamma = 1.27e-3

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

    def noise_generation(self, signal_power):
        return 1e-9 * signal_power * self._length

    def propagate(self, signal, occupation=False):
        signal.add_noise(self.noise_generation(signal.signal_power))
        signal.add_latency(self.latency_generation())
        if occupation:
            new_state = self._state.copy()
            new_state[signal.channel] = "occupied"
            self.state = new_state
        return self._successive[signal.path[0]].propagate(signal, occupation)

    def ase_generation(self):
        nf = 10 ** (self._noise_figure / 10)
        g = 10 ** (self._gain / 10)
        f = 193.414e12
        bn = 12.5e9  # GHz
        ase = self._n_amplifiers * h * f * bn * nf * (g - 1)
        return ase

    def nli_generation(self, signal_power, dfp, rsp):
        bn = 12.5e9  # GHz
        eta_nli = self.eta_nli(dfp, rsp)
        nli = (signal_power ** 3) * eta_nli * self._n_amplifiers * bn
        return nli

    def eta_nli(self, dfp, rsp):
        df = dfp
        rs = rsp
        a = self._alpha / (20 * np.log10(np.e))
        nch = 10
        b2 = self._beta2
        e_nli = 16 / (27 * pi) * np.log(pi ** 2 * b2 * rs ** 2 * nch ** (2 * rs / df) / (2 * a)) * self.gamma ** 2 / (
                    4 * a * b2 * rs ** 3)
        return e_nli
