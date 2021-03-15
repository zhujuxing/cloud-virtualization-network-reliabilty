from copy import deepcopy
from itertools import product
import networkx as nx
import matplotlib.pyplot as plt
from networkx.utils import pairwise
import src.NetEvoObjMod
import os
import numpy as np
from src.NetEvoObjMod import CloudVritualizedNetwork


def DrawNetworkApplicaiton(g, filename):
    # 1.读取配置文件信息
    network: CloudVritualizedNetwork = deepcopy(g)
    node_info = network.graph['Node_info']
    edge_info = network.graph['Edge_info']
    app_info = network.graph['Application_info']
    vnf_info = network.graph['VNF_info']

    dcgw_num = node_info.query("NodeType == 'DCGW'").shape[0]
    eor_num = node_info.query("NodeType == 'EOR'").shape[0]
    tor_num = node_info.query("NodeType == 'TOR'").shape[0]
    server_num = node_info.query("NodeType == 'Server'").shape[0]
    vs_num = node_info.query("NodeType == 'Vswitch'").shape[0]
    vm_num = node_info.query("NodeType == 'VM'").shape[0]
    proc_num = node_info.query("NodeType == 'Proc'").shape[0]

    # node_num_list = [dcgw_num, eor_num, tor_num, server_num, vs_num, vm_num]
    node_num_dict = {
        "DCGW": dcgw_num,
        "EOR": eor_num,
        "TOR": tor_num,
        "Server": server_num,
        "Vswitch": vs_num,
        "VM": vm_num,
        "Proc": proc_num
    }
    node_name_dict = {
        "DCGW": "D",
        "EOR": "E",
        "TOR": "T",
        "Server": "S",
        "Vswitch": "Vs",
        "VM": "V",
        "Proc": "P"
    }
    node_layer_dict = {
        "DCGW": 1,
        "EOR": 2,
        "TOR": 3,
        "Server": 4,
        "Vswitch": 5,
        "VM": 6,
        "Proc": 7
    }

    layer_num = len(node_num_dict)

    # 2.确认各种类型的节点坐标与颜色
    pos = {}
    for key in node_num_dict.keys():
        if node_num_dict[key] != 0:
            pos.update(
                {(node_name_dict[key] + str(i + 1)): np.array(
                    [(i + 1) * (1 / (node_num_dict[key] + 1)), 1 - (node_layer_dict[key] / layer_num)]) \
                 for i in range(node_num_dict[key])})
    # TODO:需要改进节点位置算法

    pos = {}
    def get_neigbors(g, node, depth=1):
        output = {}
        layers = dict(nx.bfs_successors(g, source=node, depth_limit=depth))
        nodes = [node]
        output.update({0: [node]})
        for i in range(1, depth + 1):
            output[i] = []
            for x in nodes:
                output[i].extend(layers.get(x, []))
            nodes = output[i]
        return output

    layer_nodes = get_neigbors(network, 'D1', 6)
    layer_nodes = [layer_nodes[i] for i in layer_nodes.keys() if layer_nodes[i]]
    layer_num = len(layer_nodes) + 1
    pos.update(
        {("D" + str(i + 1)): np.array([(i + 1) * (1 / (dcgw_num + 1)), 1 - (1 / layer_num)]) for i in range(dcgw_num)})
    for layer in layer_nodes:
        x_cordinates = [pos[i][0] for i in layer]
        for i in layer:
            nodes_next_layer = edge_info.query("EdgeSourceNode == '%s'" % i)['EdgeDestinationNode'].to_list()
            if len(nodes_next_layer) != 0:
                n = len(nodes_next_layer)
                x = pos[i][0]
                if len(layer) == 1:
                    l = 0.5
                else:
                    l = (np.array(x_cordinates[1:]) - np.array(x_cordinates[:-1])).mean()
                pos.update({j: np.array([x - (l / 2) + ((nodes_next_layer.index(j) + 1) * l) / (n + 1), 1 - ((layer_nodes.index(layer)+2) / layer_num)]) for j in nodes_next_layer})

    node_color_dict = {
        "DCGW": "cyan",
        "EOR": "green",
        "TOR": "green",
        "Server": "blue",
        "Vswitch": "blue",
        "VM": "yellow",
        "Proc": "blue"
    }

    node_shape_dict = {
        "DCGW": "^",
        "EOR": "^",
        "TOR": "D",
        "Server": "o",
        "Vswitch": "o",
        "VM": "o",
        "Proc": "o"
    }

    # 3.画图
    # 3.1画出不同层次的节点
    fig = plt.figure(figsize=(20, 10))
    plt.rcParams['font.sans-serif'] = ["SimHei"]
    plt.rcParams['axes.unicode_minus'] = False
    ax1 = fig.add_subplot(2, 1, 1)
    # # 暂时先不画proc
    # network.remove_nodes_from(node_info.query("NodeType == 'Proc'").index)
    # 开始画图
    nx.draw_networkx(network, pos=pos, with_labels=True, node_size=3, node_color='blue')
    for key in node_color_dict.keys():
        if node_num_dict[key] != 0:
            node_list = [(node_name_dict[key] + str(i + 1)) for i in range(node_num_dict[key])]
            nx.draw_networkx_nodes(network, pos=pos, nodelist=node_list,
                                   node_size=20, node_shape=node_shape_dict[key], node_color=node_color_dict[key])
    # TODO:3.2画出空闲的VM和server,目前的算法里，没有更新G.grpah['Node_info']['NodeVNF']信息，没法在倒换迁移后表示空的VNF。
    ax1.set_title('NFVnet')

    ax2 = fig.add_subplot(2, 1, 2)
    app_color_list = ['k', 'r', 'tan', 'y', 'g', 'c', 'skyblue', 'b', 'm', 'pink']
    for row in app_info.iterrows():
        app_chains = row[1]["ApplicationVNFs"].strip('[]').split(',')
        network_application = nx.DiGraph()
        layers = [vnf_info.loc[i, "VNFDeployNode"].strip('[]').split(',') for i in app_chains[1:-1]]
        layers.insert(0, app_chains[0])
        layers.insert(len(layers), app_chains[-1])
        for layer1, layer2 in pairwise(layers):
            if type(layer1) == str:
                layer1 = [layer1]
            if type(layer2) == str:
                layer2 = [layer2]
            for i in product(layer1, layer2):
                path = nx.shortest_path(network, source=i[0], target=i[1])
                for s, d in pairwise(path):
                    network_application.add_edges_from(product([s], [d]))
            nx.draw_networkx(network_application, pos=pos, with_labels=False, node_size=3,
                             node_color=app_color_list[int(row[0][-1])], edge_color=app_color_list[int(row[0][-1])])
    ax2.set_title('Application of Cloud Network')
    fig.savefig(filename)
    del network


def test():
    file = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".") + os.sep + 'test' + os.sep + 'file.xlsx'
    network = NetEvoObjMod.CloudVritualizedNetwork(file)
    fname = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".") + os.sep + 'data' + os.sep + '云化虚拟网络.png'
    DrawNetworkApplicaiton(network, fname)


if __name__ == '__main__':
    test()
