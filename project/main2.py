import copy
from random import shuffle

from core.connection import Connection
from core.network import Network, plt, np


# used for the simulation of 100 connections with all the transceiver strategies
def main():
    network = Network('jsons/exam_net.json')
    network_flex_rate = Network('jsons/exam_net.json', 'flex_rate')
    network_shannon = Network('jsons/exam_net.json', 'shannon')
    node_labels = list(network.nodes.keys())
    connections = []
    for i in range(100):
        shuffle(node_labels)
        connections.append(Connection(node_labels[0], node_labels[-1], 1e-3))

    connections1 = copy.deepcopy(connections)
    connections2 = copy.deepcopy(connections)
    connections3 = copy.deepcopy(connections)
    bins = np.linspace(90, 700, 20)
    # fixed rate_____________________________________________________________________________
    streamed_connections_fixed_rate = network.stream(connections1, best='snr')

    snrs = [connection.snr for connection in streamed_connections_fixed_rate]
    snrs_ = np.ma.masked_equal(snrs, 0)
    plt.hist(snrs_, bins=20)

    plt.title('SNR Distribution Full fixed-rate')
    plt.xlabel('dB')
    plt.savefig('plots/SNRDistributionFullfixed_rate.png')
    plt.show()

    bit_rate_fixed_rate = [connection.bit_rate for connection in streamed_connections_fixed_rate]
    brfr = np.ma.masked_equal(bit_rate_fixed_rate, 0)
    plt.hist(brfr, bins, label='fixed-rate')

    plt.title('BitRate Full fixed-rate')
    plt.xlabel('Gbps')
    plt.savefig('plots/BitRateFullfixed_rate.png')
    plt.show()

    # flex rate_____________________________________________________________________________

    streamed_connections_flex_rate = network_flex_rate.stream(connections2, best='snr')

    snrs = [connection.snr for connection in streamed_connections_flex_rate]
    snrs_ = np.ma.masked_equal(snrs, 0)
    plt.hist(snrs_, bins=20)

    plt.title('SNR Distribution Full flex-rate')
    plt.xlabel('dB')
    plt.savefig('plots/SNRDistributionFullflex_rate.png')
    plt.show()

    bit_rate_flex_rate = [connection.bit_rate for connection in streamed_connections_flex_rate]
    brfr = np.ma.masked_equal(bit_rate_flex_rate, 0)
    plt.hist(brfr, bins, label='flex_rate')

    plt.xlabel('Gbps')
    plt.title('BitRate Full Flex-Rate')
    plt.savefig('plots/BitRateFullFlex_Rate.png')
    plt.show()

    # shannon________________________________________________________________________________

    streamed_connections_shannon = network_shannon.stream(connections3, best='snr')

    snrs = [connection.snr for connection in streamed_connections_shannon]
    snrs_ = np.ma.masked_equal(snrs, 0)
    plt.hist(snrs_, bins=20)

    plt.title('SNR Distribution Full Shannon')
    plt.xlabel('dB')
    plt.savefig('plots/SNRDistributionFullshannon.png')
    plt.show()

    bit_rate_shannon = [connection.bit_rate for connection in streamed_connections_shannon]
    brs = np.ma.masked_equal(bit_rate_shannon, 0)

    plt.hist(brs, bins, label='shannon')

    plt.xlabel('Gbps')
    plt.title('BitRate Full Shannon')
    plt.savefig('plots/BitRateFullShannon.png')
    plt.show()

    # _______________________________________________________________________________________
    latencies = [connection.latency for connection in streamed_connections_shannon]
    plt.hist(np.ma.masked_equal(latencies, 0), bins=25)
    plt.title('Latency Distribution')
    plt.savefig('plots/LatencyDistribution.png')
    plt.show()
    snrs = [connection.snr for connection in streamed_connections_shannon]
    plt.hist(np.ma.masked_equal(snrs, 0), bins=20)
    plt.title('SNR Dstribution')
    plt.savefig('plots/SNRDistribution.png')
    plt.show()

    # total capacity _________________________________________________________________________

    print("Average Latency: ", np.ma.mean(np.ma.masked_equal(latencies, 0)))
    print("Average SNR: ", np.ma.mean(np.ma.masked_equal(snrs, 0)))
    print("Total Capacity Fixed-Rate:", np.ma.sum(bit_rate_fixed_rate))
    print("Average Capacity Fixed-Rate:", np.ma.mean(np.ma.masked_equal(bit_rate_fixed_rate, 0)))
    print("Total Capacity Flex-Rate:", np.ma.sum(bit_rate_flex_rate))
    print("Average Capacity Flex-Rate:", np.ma.mean(np.ma.masked_equal(bit_rate_flex_rate, 0)))
    print("Total Capacity Shannon:", np.ma.sum(bit_rate_shannon).round(2))
    print("Average Capacity Shannon:", np.ma.mean(np.ma.masked_equal(bit_rate_shannon, 0).round(2)))


if __name__ == "__main__":
    main()
