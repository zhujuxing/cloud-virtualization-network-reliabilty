# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 16:05:47 2021

@author: zhujuxing
"""

import networkx as nx
import pandas as pd
import re
# import random


class VNF():
    VNFID = str
    VNFDataType = str
    VNFBackupType = str
    VNFDeployNode = list
    VNFBackupNode = list
    VNFFailSR = float
    VNFFailST = float # 所有时间换算为小时。
    VNFSwitchPath = list
    # VNFWait = float
    VNFTraffic = float
    VNFTrafficThreshold = float
    VNFFailNodes = list
    VNFUnavailTime = list
    VNFTimer = float
    VNFState = int
    
    def __init__(self,x:pd.Series,NCE_nodes,DCGW_nodes):
        self.VNFID = x.name
        self.VNFDataType = x['VNFDataType']
        self.VNFBackupType = x['VNFBackupType']
        self.VNFDeployNode = x['VNFDeployNode'].strip('[]').split(',')
        self.VNFBackupNode = x['VNFBackupNode']
        self.VNFFailSR = x['VNFFailSR']
        self.VNFFailST = convert(x['VNFFailST'])
        self.VNFSwitchPath = x['VNFSwitchPath']
        self.VNFFailNodes = []
        # self.VNFSwitchPath = self.update_swith_path(g,self.)
        # self.VNFWait = x['VNFWait']
        self.VNFTraffic = 1
        self.VNFTrafficThreshold = 0
        self.VNFUnavailTime = []
        self.VNFTimer = 0
        self.VNFState = 0
        

    def fail(self,node,t) :
        if node in self.VNFFailNodes:
            pass
        else: 
            self.VNFFailNodes.append(node)
            self.update_traffic()
            if (self.VNFTraffic<=self.VNFTrafficThreshold) & (self.VNFState == 0):
                self.VNFTimer = t
                self.VNFState = 1
                
        
    def recovery(self,node,t):
        if node in self.VNFFailNodes:
            self.VNFFailNodes.remove(node)
            self.update_traffic()
            if (self.VNFTraffic > self.VNFTrafficThreshold) & (self.VNFState != 0):
                self.VNFUnavailTime.append([self.VNFTimer,t])
                self.VNFTimer = t
                self.VNFState = 0
        else:
            pass

    def wait(self,t):
        pass
    
    def update_traffic(self):
        self.VNFTraffic = 1-len(self.VNFFailNodes)/len(self.VNFDeployNode)
        
    def set_traffic(self,traffic_size:float):
        self.VNFTraffic = traffic_size
    
    def switch(self,work_node):
        if self.VNFBackupType == '主备':
            self.VNFDeployNode.remove(work_node)
            self.VNFDeployNode.append(self.VNFBackupNode)
            self.VNFBackupNode = work_node
        elif len(self.VNFBackupType.split(' ')) == 2:
            self.VNFSwitchBack = self.VNFDeployNode.copy()
            self.VNFDeployNode.remove(work_node)
        elif self.VNFBackupType == '主机':
            pass

    def switchback(self):
        if self.VNFBackupType == '主备':
            temp = self.VNFBackupNode
            self.VNFBackupNode = self.VNFDeployNode.pop(0)
            self.VNFDeployNode.append(temp)
        elif len(self.VNFBackupType.split(' ')) == 2:
            self.VNFDeployNode = self.VNFSwitchBack
        elif self.VNFBackupType == '主机':
            pass
        
    def migrate_work(self,CurrentVM,MigrateVM):
        if self.VNFBackupType == '主备':
            self.VNFDeployNode = [MigrateVM]
        elif len(self.VNFBackupType.split(' ')) == 2:
            self.VNFDeployNode.remove(CurrentVM)
            self.VNFDeployNode.append(MigrateVM)
        elif self.VNFBackupType == '主机':
            pass

    def migrate_backup(self,MigrateVM):        
        if self.VNFBackupType == '主备':
            self.VNFBackupNode = MigrateVM
        elif len(self.VNFBackupType.split(' ')) == 2:
            pass
        elif self.VNFBackupType == '主机':
            pass

    def update_switch_path(self,g,work_node,NCE_nodes,DCGW_nodes):
        NCE_nodes.extend(DCGW_nodes)
        self.VNFSwitchPath = [nx.shortest_path(g,work_node,i) for i in NCE_nodes]
    
def convert(x):
    '''
    转换数据格式，年、min-->小时

    '''
    if isinstance(x, str):
        s = re.findall("\d+", x)[0]
        dig = int(s)
        if '年' in x:
            return 365*24*dig
        if 'min' in x:
            return dig/60
        if 's' in x:
            return dig/3600
        if 'h' in x:
            return dig
    else:
        return x    

def test():
    g = nx.read_gpickle('g.gpickle')
    VNF_info = g.graph['VNF_info']

    VNF1_info = VNF_info.iloc[1]
    gps = VNF_info.groupby('VNFDataType')
    NCE_nodes = list(map(lambda x:x.strip('[]'),gps.get_group('NCE')['VNFDeployNode'].to_list()))
    DCGW_nodes = list(map(lambda x:x.strip('[]'),gps.get_group('DCGW')['VNFDeployNode'].to_list()))

    vnf1 = VNF(VNF1_info,NCE_nodes,DCGW_nodes)
    vnf2 = VNF(VNF_info.iloc[0],NCE_nodes,DCGW_nodes)
    
    vnf1.fail('V3',0)
    vnf1.recovery('V3',1)
    vnf1.switch('V3')
    vnf1.switchback()
    print(vnf1.__dict__)
    vnf1.migrate_work('V3','V8')
    print(vnf1.__dict__)
    # vnf1.update_switch_path(g,'V3',NCE_nodes,DCGW_nodes)
    # print(vnf1.VNFSwitchPath)
    
    vnf2.fail('V2',0)
    vnf2.recovery('V2',1)
    vnf2.switch('V2')
    vnf2.switchback()
    print(vnf2.__dict__)
    vnf2.migrate_work('V2','V9') 
    # vnf2.update_switch_path(g,'V2',NCE_nodes,DCGW_nodes)
    # print(vnf2.VNFSwitchPath)
    print(vnf2.__dict__)
    
    
if __name__ == '__main__':
    test()
