from signal_information import SignalInformation


class Lightpath(SignalInformation):
    def __init__(self, signal_power, path, channel):
        super().__init__(signal_power, path)
        self._channel = channel

    @property
    def channel(self):
        return self._channel
