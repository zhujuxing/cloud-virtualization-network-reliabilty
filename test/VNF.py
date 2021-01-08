# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 16:05:47 2021

@author: zhujuxing
"""

import networkx as nx
import pandas as pd


g = nx.read_gpickle('g.gpickle')
VNF_info = g.graph['VNF_info']
VNF1_info = VNF_info.iloc[0]

class VNF():
    VNFID = str
    VNFDataType = str
    VNFBackupType = str
    VNFDeployNode = list
    VNFBackupNode = list
    VNFFailSR = float
    VNFFailST = float # 所有时间换算为小时。
    VNFSwitchPath = list
    VNFWait = float
    VNFState = int # VNF共有三个状态，0表示VNF正常，1表示VNF正在切换/迁移，2表示VNF的流量中断。
    
    def __init__(self,x:pd.Series):
        self.VNFID = x.name
        self.VNFDataType = x['VNFDataType']
        self.VNFBackupType = x['VNFBackupType']
        self.VNFDeployNode = x['VNFDeployNode']
        self.VNFBackupNode = x['VNFBackupNode']
        self.VNFFailSR = x['VNFFailSR']
        self.VNFFailST = x['VNFFailSt']
        self.VNFSwitchPath = x['VNFSwitchPath']
        self.VNFWait = x['VNFWait']
        self.VNFState = x['VNFState']
        
        
    def switch(self,g):
        
        return g    
        
    def migrate(self,g):
        return g