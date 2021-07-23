from signal_information import SignalInformation


class Lightpath(SignalInformation):
    def __init__(self, signal_power, path, channel):
        super().__init__(signal_power, path)
        self._channel = channel
        self._rs = 32.0e9
        self.df = 50.0e9

    @property
    def channel(self):
        return self._channel

    @property
    def rs(self):
        return self._rs
