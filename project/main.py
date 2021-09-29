import itertools
from core.network import Network, plt, np
from random import choice


# used for the traffic matrix
def main():
    sat_percent = 95
    # fixed rate_____________________________________________________________________________
    network = Network('jsons/exam_net.json')
    n_node = len(network.nodes.keys())
    saturation_fix = []
    ms_fix = []
    m = 1
    while 1:
        t_mtx = np.ones((n_node, n_node)) * 100 * m
        for i in range(n_node):
            t_mtx[i][i] = 0
        elements = list(itertools.permutations(network.nodes.keys(), 2))
        n_elem = len(elements)
        for e in elements:  # remove the diagonal
            if e[0] == e[1]:
                elements.remove(e)
        for i in range(100):
            if len(elements) == 0:
                break
            el = choice(elements)
            val = network.upgrade_traffic_matrix(t_mtx, el[0], el[1])
            if (val == 0) | (val == np.inf):
                elements.remove(el)
        sat = 0
        for row in t_mtx:
            for el in row:
                if el == float('inf'):
                    sat += 1
        sat = sat / n_elem * 100
        saturation_fix.append(sat)
        ms_fix.append(m)
        if sat > sat_percent:
            break
        m += 1
        network.free_space()
    plt.plot(ms_fix, saturation_fix)
    plt.title('Saturation Fixed-Rate')
    plt.savefig('plots/M_fixed_rate.png')
    plt.xlabel('M')
    plt.ylabel('% of unsatisfied requests')
    plt.grid(linestyle='-', linewidth=0.5)
    plt.show()

    # flex rate_____________________________________________________________________________
    network_flex_rate = Network('jsons/exam_net.json', 'flex_rate')
    n_node = len(network_flex_rate.nodes.keys())
    saturation_flex = []
    ms_flex = []
    m = 1
    while 1:
        t_mtx = np.ones((n_node, n_node)) * 100 * m
        for i in range(n_node):
            t_mtx[i][i] = 0
        elements = list(itertools.permutations(network_flex_rate.nodes.keys(), 2))
        n_elem = len(elements)
        for e in elements:  # remove the diagonal
            if e[0] == e[1]:
                elements.remove(e)
        for i in range(100):
            if len(elements) == 0:
                break
            el = choice(elements)
            val = network_flex_rate.upgrade_traffic_matrix(t_mtx, el[0], el[1])
            if (val < 0) | (val == np.inf):
                elements.remove(el)
        sat = 0
        for row in t_mtx:
            for el in row:
                if el == float('inf'):
                    sat += 1
        sat = sat / n_elem * 100
        saturation_flex.append(sat)
        ms_flex.append(m)
        if sat > sat_percent:
            break
        m += 1
        network_flex_rate.free_space()
    plt.plot(ms_flex, saturation_flex)
    plt.title('Saturation Flex-Rate')
    plt.savefig('plots/M_flex_rate.png')
    plt.xlabel('M')
    plt.ylabel('% of unsatisfied requests')
    plt.grid(linestyle='-', linewidth=0.5)
    plt.show()

    # shannon________________________________________________________________________________
    network_shannon = Network('jsons/exam_net.json', 'shannon')
    n_node = len(network_shannon.nodes.keys())
    saturation_shan = []
    ms_shan = []
    m = 1

    while 1:
        t_mtx = np.ones((n_node, n_node)) * 100 * m
        for i in range(n_node):
            t_mtx[i][i] = 0
        elements = list(itertools.permutations(network_shannon.nodes.keys(), 2))
        n_elem = len(elements)
        for e in elements:  # remove the diagonal
            if e[0] == e[1]:
                elements.remove(e)
        for i in range(100):
            if len(elements) == 0:
                break
            el = choice(elements)
            val = network_shannon.upgrade_traffic_matrix(t_mtx, el[0], el[1])
            if (val < 0) | (val == np.inf):
                elements.remove(el)
        sat = 0
        for row in t_mtx:
            for el in row:
                if el == float('inf'):
                    sat += 1
        sat = sat / n_elem * 100
        saturation_shan.append(sat)
        ms_shan.append(m)
        if sat > sat_percent:
            break
        m += 1
        network_shannon.free_space()
    plt.plot(ms_shan, saturation_shan)
    plt.title('Saturation Parameter Shannon')
    plt.savefig('plots/M_shannon.png')
    plt.xlabel('M')
    plt.ylabel('% of unsatisfied requests')
    plt.grid(linestyle='-', linewidth=0.5)
    plt.show()
    plt.plot(ms_fix, saturation_fix, label='fixed-rate')
    plt.plot(ms_flex, saturation_flex, label='flex-rate')
    plt.plot(ms_shan, saturation_shan, label='shannon')
    plt.xlabel('M')
    plt.ylabel('% of unsatisfied requests')
    plt.grid(linestyle='-', linewidth=0.5)
    plt.legend(loc='lower right')
    plt.title('Saturation Parameter')
    plt.savefig('plots/M_all.png')
    plt.show()


if __name__ == "__main__":
    main()
