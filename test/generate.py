# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 21:40:00 2021

@author: zhujuxing
"""

import networkx as nx
import pandas as pd
# import numpy as np
# import itertools

node_info = pd.read_excel('file.xlsx',sheet_name='node_info')
fail_info = pd.read_excel('file.xlsx',sheet_name='fail_info')
VNF_info = pd.read_excel('file.xlsx',sheet_name='VNF_info')
Service_info = pd.read_excel('file.xlsx',sheet_name='Service_info')
Application_info = pd.read_excel('file.xlsx',sheet_name='Application_info')
VNF_evorule = pd.read_excel('file.xlsx',sheet_name='VNF_evorule')
    
g = nx.Graph()
g.graph['VNF_info'] = VNF_info
g.graph['Service_info'] = Service_info
g.graph['Application_info'] = Application_info

g.add_nodes_from(node_info['节点名称'])


node_attr = {node_info.loc[i,'节点名称']:
             {'NodeType':node_info.loc[i,'节点类型']} for i in node_info.index}

fail_info=fail_info.rename(columns={'节点类型':'NodeType',
                                    '节点故障模式':'NodeFailType',
                                    '节点平均故障间隔时间':'NodeFailMTBF',
                                    '节点故障时间分布':'NodeFailDistri',
                                    '节点故障检测率':'NodeFailFDR',
                                    '节点故障检测时间':'NodeFailFDT',
                                    '节点自动维修概率':'NodeFailAFDR',
                                    '节点自动维修时间':'NodeFailAFDT',
                                    '节点平均人工维修时间':'NodeFailMTTR',
                                    '节点维修时间分布':'NodeRecoDistri',
                                    '节点备份策略':'NodeRecoStra'}) 
for i in node_attr:
    if node_attr[i]['NodeType'] == 'DCGW':
        node_attr[i].update(fail_info.iloc[0].to_dict())
    elif node_attr[i]['NodeType'] == 'TOR': 
        node_attr[i].update(fail_info.iloc[1].to_dict())
    elif node_attr[i]['NodeType'] == 'Server':
        node_attr[i].update(fail_info.iloc[2].to_dict())
    elif node_attr[i]['NodeType'] == 'VM':
        node_attr[i].update(fail_info.iloc[3].to_dict())
    elif node_attr[i]['NodeType'] == 'Proc':
        node_attr[i].update(fail_info.iloc[4].to_dict())
nx.set_node_attributes(g,node_attr)
nx.set_node_attributes(g,float('nan'),'NodeFailMR')
nx.set_node_attributes(g,float('nan'),'NodeFailMT')
nx.set_node_attributes(g,[],'NodeMP')
nx.set_node_attributes(g,1,'NodeState')
nx.set_node_attributes(g,1,'NodeIdle')
nx.set_node_attributes(g,0.5,'Tasp')
nx.set_node_attributes(g,168,'Tchk')


edges_set = node_info[['节点名称','叶子节点']].dropna()
for i in edges_set.index:
    source = edges_set.loc[i,'节点名称']
    g.add_edges_from([(source,j) for j in edges_set.loc[i,'叶子节点'].split(',')])
nx.set_edge_attributes(g,10,'EdgeCapacity')
nx.set_edge_attributes(g,8,'EdgeTraffic')
    

for i in g.nodes:
    if g.nodes[i]['NodeType'] == 'Server':
        g.nodes[i]['NodeFailMR'] = 0.9
        g.nodes[i]['NodeFailMT'] = 0.166667
        g.nodes[i]['NodeMP'] = [nx.shortest_path(g,i,'S4'),
                                nx.shortest_path(g,i,'D1')]
