import numpy as np
import pandas as pd

from network import Network
from signal_information import SignalInformation as sigInf


def main():
    net = Network("nodes.json")
    pairs = []
    df_data = dict(zip(["path", "latency", "noise", "SNR"], [[], [], [], []]))

    net.connect()
    for nodeLabel in net.nodes.keys():
        for nodeLabel2 in net.nodes.keys():
            if nodeLabel != nodeLabel2:
                pairs.append(nodeLabel + nodeLabel2)

    for pair in pairs:
        for path in net.find_paths(pair[0], pair[1]):
            path_label = ""
            for i in range(len(path)):
                if i == (len(path) - 1):
                    path_label += path[i]
                else:
                    path_label += path[i] + "->"
            df_data['path'].append(path_label)
            sig = net.propagate(sigInf(1, path))
            df_data['latency'].append(sig.latency)
            df_data['noise'].append(sig.noise_power)
            df_data['SNR'].append(10 *
                                  np.log10(sig.signal_power / sig.noise_power))
    print(pd.DataFrame(df_data))


if __name__ == "__main__":
    main()
