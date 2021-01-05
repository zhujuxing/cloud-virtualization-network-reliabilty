# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 21:40:00 2021

@author: zhujuxing
"""

import networkx as nx
import pandas as pd
# import numpy as np
# import itertools

def main():
    """
    该函数返回总体设计报告中的案例设计的网络模型G。
    其需要读入报告中所提供的各项表格数据，保存在file.xlsx中。
    返回的网络数据保存在g.gpickle中，网络


    """
    node_info = pd.read_excel('file.xlsx',sheet_name='node_info')
    fail_info = pd.read_excel('file.xlsx',sheet_name='fail_info')
    VNF_info = pd.read_excel('file.xlsx',sheet_name='VNF_info')
    Service_info = pd.read_excel('file.xlsx',sheet_name='Service_info')
    Application_info = pd.read_excel('file.xlsx',sheet_name='Application_info')
    VNF_evorule = pd.read_excel('file.xlsx',sheet_name='VNF_evorule')
        
    g = nx.Graph()
  
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
    nx.set_node_attributes(g,0,'NodeIdle')
    nx.set_node_attributes(g,0.5,'Tasp')
    nx.set_node_attributes(g,168,'Tchk')
    g.nodes['S3']['NodeIdle'] = 1
    g.nodes['V7']['NodeIdle'] = 1
    g.nodes['V8']['NodeIdle'] = 1
    g.nodes['V9']['NodeIdle'] = 1
    
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
    nx.write_gpickle(g,'g.gpickle')
    
    
    Application_info = Application_info.rename(columns={'业务名称':'ApplicationID',
                                                '业务逻辑路径':'ApplicationService',
                                                '业务物理路径':'ApplicationWorkPath',
                                                '业务中断时间':'ApplicationUnavailTime'})
    Application_info['ApplicationAvail'] = 1.0
    Application_info['ApplicationStatus'] = 1
    Application_info['ApplicationInitTraffic'] = 3.5
    Application_info['ApplicationTraffic'] = 1
    Application_info['ApplicationThreshold'] = 0
    Application_info = Application_info.set_index('ApplicationID')
    
    
    Service_info = Service_info.rename(columns={'Service名称':'ServiceID',
                                                'Service路径':'ServiceVNF'})
    Service_info = Service_info.set_index('ServiceID')
    
    VNF_info = pd.merge(VNF_info,VNF_evorule,on=['VNF名称','类型'])
    VNF_info = VNF_info.rename(columns={'VNF名称':'VNFID',
                                        '类型':'VNFBackupType',
                                        '工作节点':'VNFDeployNode',
                                        '备用节点':'VNFBackupNode',
                                        '倒换概率':'VNFFailSR',
                                        '倒换时间':'VNFFailST',
                                        '倒换控制链路':'VNFSwitchPath'})
    VNF_info.set_index('VNFID')
    VNF_info['VNFWait'] = 0
    
    g.graph['VNF_info'] = VNF_info
    g.graph['Service_info'] = Service_info
    g.graph['Application_info'] = Application_info
    return g
            
def show_nodes_data(g):
    df = pd.DataFrame(columns=['NodeType','NodeFailType',
                               'NodeFailDistri','NodeFailMTBF',
                               'NodeFailFDR','NodeFailFDT',
                               'NodeFailAFRR','NodeFailAFRT',
                               'NodeFailMTTR','NodeFailMR','NodeFailMT','NodeFailMP',
                               'NodeState','NodeIdle','Tasp','Tchk'
                               ])
    ndata = dict(g.nodes.data())
    for i in ndata:
        ns = pd.Series(ndata[i])
        ns.name = i
        df = df.append(ns)
    print(df)
    return df 

def show_edges_data(g):
    df = pd.DataFrame(columns=['EdgeSourceNode','EdgeDestinationNode',
                               'EdgeCapacity','EdgeTraffic'])
    edata = list(g.edges.data())
    for i in edata:
        ns = pd.Series({'EdgeSourceNode':i[0],'EdgeDestinationNode':i[1],
                        'EdgeCapacity':i[2]['EdgeCapacity'],
                        'EdgeTraffic':i[2]['EdgeTraffic']})
        df = df.append(ns,ignore_index=True)
    df.index = ['Eg%d'%(i+1) for i in range(len(edata))]
    print(df)
    return df
                
        
if __name__ == '__main__':
    g = main()
    ndf = show_nodes_data(g)
    edf = show_edges_data(g)
  
    
