# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:34:57 2020

@author: zhujuxing
"""

import networkx as nx
import pandas as pd
import os
# import itertools
from itertools import product

# 增加节点类型'Vs'
class CloudVritualizedNetwork(nx.Graph):
    def __init__(self,file):
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
        # Service_info = pd.read_excel(file,sheet_name='Service_info')
        Application_info = pd.read_excel(file,sheet_name='Application_info')
        # VNF_evorule = pd.read_excel(file,sheet_name='VNF_evorule')
            
        nx.Graph.__init__(self)
        self.add_nodes_from(node_info['节点名称'])
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
            # x = node_attr[i]['NodeType']
            # attr_temp = fail_info.query('NodeType==@x')
            # node_attr[i].update(attr_temp.to_dict())
            
            if node_attr[i]['NodeType'] == 'DCGW':
                node_attr[i].update(fail_info.iloc[0].to_dict())
            elif node_attr[i]['NodeType'] == 'EOR': 
                node_attr[i].update(fail_info.iloc[1].to_dict())
            elif node_attr[i]['NodeType'] == 'TOR': 
                node_attr[i].update(fail_info.iloc[2].to_dict())
            elif node_attr[i]['NodeType'] == 'Server':
                node_attr[i].update(fail_info.iloc[3].to_dict())
            elif node_attr[i]['NodeType'] == 'Vswitch':
                node_attr[i].update(fail_info.iloc[4].to_dict())
            elif node_attr[i]['NodeType'] == 'VM':
                node_attr[i].update(fail_info.iloc[5].to_dict())
            elif node_attr[i]['NodeType'] == 'Proc':
                node_attr[i].update(fail_info.iloc[6].to_dict())
        nx.set_node_attributes(self,node_attr)
        nx.set_node_attributes(self,float('nan'),'NodeFailMR')
        nx.set_node_attributes(self,float('nan'),'NodeFailMT')
        nx.set_node_attributes(self,[],'NodeMP')
        nx.set_node_attributes(self,1,'NodeState')
        nx.set_node_attributes(self,0,'NodeIdle')
        nx.set_node_attributes(self,0.5,'Tasp')
        nx.set_node_attributes(self,168,'Tchk')
        node_idle = node_info[node_info.loc[:,'节点上部署的服务']=='空']['节点名称'].to_list()
        for i in node_idle:self.nodes[i]['NodeIdle'] = 1
        
        egs = edge_info[['源节点ID','目的节点ID']].to_numpy().tolist()
        self.add_edges_from(egs)
        nx.set_edge_attributes(self,10,'EdgeCapacity')
        nx.set_edge_attributes(self,8,'EdgeTraffic')
            
    
        for i in self.nodes:
            if self.nodes[i]['NodeType'] == 'Server':  
                self.nodes[i]['NodeFailMR'] = 0.9
                self.nodes[i]['NodeFailMT'] = 0.166667
                # g.nodes[i]['NodeMP'] = [nx.shortest_path(g,i,'S4'),
                #                         nx.shortest_path(g,i,'D1')]
                self.nodes[i]['NodeMP'] = []
    
        Application_info = Application_info.rename(columns={'业务名称':'ApplicationID',
                                                    '业务逻辑路径':'ApplicationVNFs',
                                                    '业务物理路径':'ApplicationWorkPath',
                                                    '业务中断时间':'ApplicationUnavailTime'})
        Application_info['ApplicationAvail'] = 1.0
        Application_info['ApplicationStatus'] = 1
        Application_info['ApplicationInitTraffic'] = 3.5
        Application_info['ApplicationTraffic'] = 1
        Application_info['ApplicationThreshold'] = 0
        Application_info['ApplicationDownStartTime'] = 0
        # Application_info['ApplicationVNFs'] = 'VNF2'
        Application_info = Application_info.set_index('ApplicationID')
        # 计算业务物理路径
        Application_info['ApplicationDownTime'] = 0
        Application_info['ApplicationWorkPath'] = str(['D1','T1','S1','Vs1','V2','Vs1',
                                                    'S1','T1','D1'])

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
        
    
        
        self.graph['VNF_info'] = VNF_info
        self.graph['Application_info'] = Application_info
        self.graph['Node_info'] = self.update_nodes_data()
        self.graph['Edge_info'] = self.update_edges_data()
        self.update_app_work_path()
        
    def update_nodes_data(self):
        df = pd.DataFrame(columns=['NodeType','NodeFailType',
                                   'NodeFailDistri','NodeFailMTBF',
                                   'NodeFailFDR','NodeFailFDT',
                                   'NodeFailAFRR','NodeFailAFRT',
                                   'NodeFailMTTR','NodeFailMR','NodeFailMT','NodeFailMP',
                                   'NodeState','NodeIdle','Tasp','Tchk'
                                   ])
        ndata = dict(self.nodes.data())
        for i in ndata:
            ns = pd.Series(ndata[i])
            ns.name = i
            df = df.append(ns)
        # print(df)
        return df
    
    def update_edges_data(self):
        df = pd.DataFrame(columns=['EdgeSourceNode','EdgeDestinationNode',
                                   'EdgeCapacity','EdgeTraffic'])
        edata = list(self.edges.data())
        for i in edata:
            ns = pd.Series({'EdgeSourceNode':i[0],'EdgeDestinationNode':i[1],
                            'EdgeCapacity':i[2]['EdgeCapacity'],
                            'EdgeTraffic':i[2]['EdgeTraffic']})
            df = df.append(ns,ignore_index=True)
        df.index = ['Eg%d'%(i+1) for i in range(len(edata))]
        # print(df)
        return df        
    
    def update_app_work_path(self):
        VNF_info = self.graph['VNF_info']
        def find_work_path(x,VNF_info):
            logic_path = x['ApplicationVNFs']
            logic_path = logic_path.strip('[]').split(',')
            # entrance_device = logic_path[0]
            # exit_device = logic_path[-1]
            # logic_path = logic_path[1:-1]
            work_path = []
            for i in range(len(logic_path)-1):
                source = logic_path[i]
                target = logic_path[i+1]
                if 'VNF' in source:
                    source = VNF_info.loc[source,'VNFDeployNode']
                    source = source.strip('[]').split(',')
                else:
                    source = [source]
                if 'VNF' in target:
                    target = VNF_info.loc[target,'VNFDeployNode']
                    target = target.strip('[]').split(',')
                else:
                    target = [target]
                for j,k in product(source,target):
                    work_path.extend(nx.shortest_path(self,j,k))
            return str(work_path)
        value = self.graph['Application_info'].apply(lambda x:find_work_path(x,VNF_info),axis = 1)
        self.graph['Application_info']['ApplicationWorkPath'] = value
    

def test():
    file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file.xlsx'
    g = CloudVritualizedNetwork(file)
    # nx.write_gpickle(g,'g.gpickle')
    return g

if __name__ == '__main__':
    g = test()
    ni = g.graph['Node_info']
    ei = g.graph['Edge_info']
    vi = g.graph['VNF_info']
    ai = g.graph['Application_info']