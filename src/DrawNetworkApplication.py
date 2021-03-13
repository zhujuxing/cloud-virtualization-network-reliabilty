from typing import Dict

import networkx as nx
import matplotlib.pyplot as plt
import NetEvoObjMod
import os
import numpy as np
import pandas as pd

# 1.读取配置文件信息

file = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".") + os.sep + 'test' + os.sep + 'file.xlsx'
network = NetEvoObjMod.CloudVritualizedNetwork(file)

node_info = network.graph['Node_info']
Edge_info = network.graph['Edge_info']
app_info = network.graph['Application_info']
vnf_info = network.graph['VNF_info']

dcgw_num = node_info.query("NodeType == 'DCGW'").shape[0]
eor_num = node_info.query("NodeType == 'EOR'").shape[0]
tor_num = node_info.query("NodeType == 'TOR'").shape[0]
server_num = node_info.query("NodeType == 'Server'").shape[0]
vs_num = node_info.query("NodeType == 'Vswitch'").shape[0]
vm_num = node_info.query("NodeType == 'VM'").shape[0]

# node_num_list = [dcgw_num, eor_num, tor_num, server_num, vs_num, vm_num]
node_num_dict = {
    "DCGW": dcgw_num,
    "EOR": eor_num,
    "TOR": tor_num,
    "Server": server_num,
    "Vswitch": vs_num,
    "VM": vm_num
}
node_name_dict = {
    "DCGW": "D",
    "EOR": "E",
    "TOR": "T",
    "Server": "S",
    "Vswitch": "Vs",
    "VM": "V"
}
layer_num = sum((1 for i in node_num_dict.values() if i != 0))

# 2.确认各种类型的节点坐标与颜色
pos = {}
for key in node_num_dict.keys():
    if node_num_dict[key] != 0:
        pos.update(
            {(node_name_dict[key] + str(i+1)): np.array([(i + 1) * (1 / (node_num_dict[key] + 1)), 1 - (1 / layer_num)]) \
             for i in range(node_num_dict[key])})

node_color_dict = {
    "DCGW": "cyan",
    "EOR": "green",
    "TOR": "green",
    "Server": "blue",
    "Vswitch": "blue",
    "VM": "yellow"
}

node_shape_dict = {
    "DCGW": "^",
    "EOR": "^",
    "TOR": "D",
    "Server": "o",
    "Vswitch": "o",
    "VM": "o"
}

# 3.画图
fig = plt.figure(figsize=(40, 10))
plt.rcParams['font.sans-serif'] = ["SimHei"]
plt.rcParams['axes.unicode_minus'] = False
ax1 = fig.add_subplot(2, 1, 1)
nx.draw_networkx(network, pos=pos, with_labels=False, node_size=3, node_color='blue')
for key in node_color_dict.keys():
    if node_num_dict[key] != 0:
        node_list = [(node_name_dict(key)+str(i+1)) for i in range(node_num_dict(key))]
        nx.draw_networkx_nodes(network, pos=pos, nodelist=node_list,
                               node_size=20, node_shape=node_shape_dict[key], node_color=node_color_dict[key])
VM_idle = nodes_info1[nodes_info1['VNF'] == 'none']['NodeID'].to_list()
nx.draw_networkx_nodes(g, pos=pos, nodelist=VM_idle,
                       node_size=20, node_shape='o', node_color='white')
server_idle = nodes_info1[nodes_info1['Idle'] == 1]['NodeID'].to_list()
nx.draw_networkx_nodes(g, pos=pos, nodelist=server_idle,
                       node_size=20, node_shape='o', node_color='white')
ax1.set_title('NFVnet')

ax2 = fig.add_subplot(2, 1, 2)
# color_list = ['k', 'r', 'tan', 'y', 'g', 'c', 'skyblue', 'b', 'm', 'pink']
# for row in Application_info.iterrows():
#     AppChains = row[1]['ApplicationVNFs']
#     G1 = nx.DiGraph()
#     layers = [VNF_info[VNF_info['id'] == i]['deploynode'].iloc[0] for i in AppChains]
#     layers.insert(0, 'D0')
#     layers.insert(len(layers), 'D1')
#     for layer1, layer2 in pairwise(layers):
#         if type(layer1) == str:
#             layer1 = [layer1]
#         if type(layer2) == str:
#             layer2 = [layer2]
#         for i in itertools.product(layer1, layer2):
#             path = nx.shortest_path(g, source=i[0], target=i[1])
#             for s, d in pairwise(path):
#                 G1.add_edges_from(itertools.product([s], [d]))
#     nx.draw_networkx(G1, pos=pos, with_labels=False, node_size=3,
#                      node_color=color_list[row[0]], edge_color=color_list[row[0]])
#     Application_info.loc[row[0], 'WorkPath'] = G1.nodes
#
#     G2 = nx.DiGraph()
#     layers = []
#     for i in AppChains:
#         df_t = VNF_info[VNF_info['id'] == i].iloc[0]
#         if df_t['type'] == '1:1backup':
#             layers.append(df_t['backupnode'])
#         else:
#             layers.append(df_t['deploynode'])
#     layers.insert(0, 'D0')
#     layers.insert(len(layers), 'D1')
#     for layer1, layer2 in pairwise(layers):
#         if type(layer1) == str:
#             layer1 = [layer1]
#         if type(layer2) == str:
#             layer2 = [layer2]
#         for i in itertools.product(layer1, layer2):
#             path = nx.shortest_path(g, source=i[0], target=i[1])
#             for s, d in pairwise(path):
#                 G2.add_edges_from(itertools.product([s], [d]))
#     Application_info.loc[row[0], 'BackupPath'] = G2.nodes
ax2.set_title('Application of Cloud Network')
fig.savefig('云化虚拟网络.png')
nx.write_gpickle(g, 'g.gpickle')
