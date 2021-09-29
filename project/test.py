from random import shuffle

import matplotlib.pyplot as plt

from core.connection import Connection
from core.network import Network


def main():
    net = Network("jsons/exam_net.json")
    nodes = list(net.nodes.keys())
    connections = list()

    net.connect()
    for i in range(100):
        shuffle(nodes)
        connections.append(Connection(nodes[0], nodes[-1], 1e-3))
    streamed_connections = net.stream(connections)
    latencies = [connection.latency for connection in streamed_connections]
    plt.hist(latencies, bins=10)
    plt.title("Latencies")
    plt.show()
    streamed_connections = net.stream(connections, "snr")
    snrs = [connection.snr for connection in streamed_connections]
    plt.hist(snrs, bins=10)
    plt.title("SNRs")
    plt.show()
    print(net.weighted_paths)
    print(net.route_space)


if __name__ == "__main__":
    main()
