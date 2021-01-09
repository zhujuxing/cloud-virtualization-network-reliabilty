# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:34:57 2020

@author: zhujuxing
"""

import networkx as nx
import pandas as pd
import os

def net_evo_obj_mod(file)->nx.Graph:
    """
    该函数为演化对象生成函数。

    Parameters
    ----------
    file : str
        网络信息.xlsx文件的路径。

    Returns
    -------
    G : TYPE
        G包含节点信息:G.nodes.data(),链路信息G.edges.data(),
        业务信息在G.graph里设置，分别是
        G.graph['VNF_info'] : dataframe对象
        G.graph['Service_info']
        G.graph['Application_info']

    """
    node_info = pd.read_excel(file,sheet_name='node_info')
    edge_info = pd.read_excel(file,sheet_name='edge_info')
    fail_info = pd.read_excel(file,sheet_name='fail_info')
    VNF_info = pd.read_excel(file,sheet_name='VNF_info')
    Service_info = pd.read_excel(file,sheet_name='Service_info')
    Application_info = pd.read_excel(file,sheet_name='Application_info')
    VNF_evorule = pd.read_excel(file,sheet_name='VNF_evorule')
        
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
    node_idle = node_info[node_info.loc[:,'节点上部署的服务']=='空']['节点名称'].to_list()
    for i in node_idle:g.nodes[i]['NodeIdle'] = 1
    
    egs = edge_info[['源节点ID','目的节点ID']].to_numpy().tolist()
    g.add_edges_from(egs)
    nx.set_edge_attributes(g,10,'EdgeCapacity')
    nx.set_edge_attributes(g,8,'EdgeTraffic')
        
    
    for i in g.nodes:
        if g.nodes[i]['NodeType'] == 'Server':
            g.nodes[i]['NodeFailMR'] = 0.9
            g.nodes[i]['NodeFailMT'] = 0.166667
            # g.nodes[i]['NodeMP'] = [nx.shortest_path(g,i,'S4'),
            #                         nx.shortest_path(g,i,'D1')]
            g.nodes[i]['NodeMP'] = []

    Application_info = Application_info.rename(columns={'业务名称':'ApplicationID',
                                                '业务逻辑路径':'ApplicationService',
                                                '业务物理路径':'ApplicationWorkPath',
                                                '业务中断时间':'ApplicationUnavailTime'})
    Application_info['ApplicationAvail'] = 1.0
    Application_info['ApplicationStatus'] = 1
    Application_info['ApplicationInitTraffic'] = 3.5
    Application_info['ApplicationTraffic'] = 1
    Application_info['ApplicationThreshold'] = 0
    Application_info['ApplicationDownStartTime'] = 0
    Application_info['ApplicationService'] = 'VNF2'
    Application_info = Application_info.set_index('ApplicationID')
    # 计算业务物理路径
    Application_info['ApplicationDownTime'] = 0
    Application_info['ApplicationWorkPath'] = 'D1,T1,S1,V1,V2,V1,S1,T1,D1'
    
    Service_info = Service_info.rename(columns={'Service名称':'ServiceID',
                                                'Service路径':'ServiceVNF'})
    Service_info = Service_info.set_index('ServiceID')
    
    VNF_info = pd.merge(VNF_info,VNF_evorule,how='left',on=['VNF名称','备份类型'])
    VNF_info['倒换控制链路'] = str([])
    VNF_info = VNF_info.rename(columns={'VNF名称':'VNFID',
                                        '数据类型':'VNFDataType',
                                        '备份类型':'VNFBackupType',
                                        '工作节点':'VNFDeployNode',
                                        '备用节点':'VNFBackupNode',
                                        '倒换概率':'VNFFailSR',
                                        '倒换时间':'VNFFailST',
                                        '倒换控制链路':'VNFSwitchPath'})
    VNF_info.set_index('VNFID')
    VNF_info['VNFWait'] = 0
    VNF_info = VNF_info.set_index('VNFID')
    # # 增加寻找VNF控制链路模块
    # VNF_gps = VNF_info.groupby(VNF_info['VNFDataType'])
    # VNF_data = VNF_gps.get_group('数据')
    # VNF_NCE = VNF_gps.get_group('NCE')
    # VNF_DCGW = VNF_gps.get_group('DCGW')
    # VNF_data.apply(lambda x: ,axis = 1)
    

    
    g.graph['VNF_info'] = VNF_info
    g.graph['Service_info'] = Service_info
    g.graph['Application_info'] = Application_info
    g.graph['Node_info'] = show_nodes_data(g)
    g.graph['Edge_info'] = show_edges_data(g)
    # nx.write_gpickle(g,'g.gpickle')
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

def test():
    file = os.getcwd()+os.sep+'test'+os.sep+'file.xlsx'
    g = net_evo_obj_mod(file)
    nx.write_gpickle(g,'g.gpickle')
    return g

if __name__ == '__main__':
    g = test()
    ni = g.graph['Node_info']
    ei = g.graph['Edge_info']
    vi = g.graph['VNF_info']
    si = g.graph['Service_info']
    ai = g.graph['Application_info']