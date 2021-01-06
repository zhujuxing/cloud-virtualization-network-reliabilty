# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:36:41 2020

@author: zhujuxing
"""

import netwrokx as nx
import pandas as pd


Uptime = {}#创建一个空字典，记录业务从故障状态转换到正常状态的时刻
Downtime = {}#创建一个空字典，记录业务从正常状态转换到故障状态的时刻
def net_evo_rul_ana(G,evol,Uptime,Downtime)->nx.Graph:
    """
    

    Parameters
    ----------
    G : TYPE
        DESCRIPTION.
    evol : TYPE
        DESCRIPTION.

    Returns
    -------
    G_T : TYPE
        经过T时间后的网络演化对象模型

    """
    G_T = G.copy()
    

    def rul_ana(x):
        """
        

        Parameters
        ----------
        x : TYPE
            x是一个时态下的evol的dataframe,x['EvolFailNodesSet'],x['EvolRecoNodesSet']
            x['time']
        Returns
        -------
        None.

        """
        
        nonlocal G_T
        # 修复节点怎么操作，对这个集合下的所有节点操作x['EvolRecoNodesSet']
            # DCGW/EOR/TOR
            # Server
            # VM
        for RecoNode in x['EvolRecoNodesSet']:#遍历演化态下的修复节点集
            if RecoNode['NodeType']=DCGW:#修复节点为DCGW
            
            
            if RecoNode['NodeType']=EOR:#修复节点为EOR
            
            
            if RecoNode['NodeType']=TOR:#修复节点为TOR
            
            
            if RecoNode['NodeType']=Server:#修复节点为Server
            
            
            if RecoNode['NodeType']=VSwitch:#修复节点为VSwitch
            
            
            if RecoNode['NodeType']=VM:#修复节点为VM
                for appID, statu in g.graph['Application_info']['applicationStatus'].item():
                    if statu == 1:
                        continue
                    if statu == 0:
                        nodes = g.graph['Application_info']['applicationWorkPath'][appID]
                        nodes = nodes.replace("[",'').replace("]",'')
                        nodes = nodes.split(',')
                        for node in nodes:
                            if (node in x['EvolFailNodesSet']):
                                break
                            else:
                                continue
                        g.graph['Application_info']['applicationStatus'][appID]=1
                        Uptime[appID] = x['time']
                        g.graph['Application_info']['applicationUnavilTime'][appID] += ([Uptime[appID]-Downtime[appID])
    
                        
                            
                    
                                
                        
                        
                    
                    
            
        # 故障节点集怎么操作，对这个集合下的所有节点操作x['EvolFailNodesSet']
            # DCGW/EOR/TOR
            # Server
            #VSwitch
            # VM
       for FailNode in x['EvolFailNodesSet']:#遍历演化态下的故障节点集
            if FailNode['NodeType']=DCGW:#故障节点为DCGW
            
            
            if FailNode['NodeType']=EOR:#故障节点为EOR
            
            
            if FailNode['NodeType']=TOR:#故障节点为TOR
            
            
            if FailNode['NodeType']=Server:#故障节点为Server
            
            
            if FailNode['NodeType']=VSwitch:#故障节点为VSwitch
            
            
            if FailNode['NodeType']=VM:#故障节点为VM
                for i in range(len(g.graph['VNF_info'])):
                    nodes = g.graph['VNF_info']['VNFDeployNode'][i][1]
                    nodes = nodes.replace("[",'').replace("]",'')
                    nodes = nodes.split(',')
                    if (FailNode in nodes):
                        if g.graph['VNF_info']['VNFBackupType'][i] == '主机':
                            for j in range(len(g.graph['Service_info'])):
                                VNFs = g.graph['Service_info']['ServiceVNF'][j]
                                VNFs = VNFs,replace("[",'').replace("]",'')
                                VNFs = VNFs.split(',')
                                if (g.graph['VNF_info']['VNFID'][i] in VNFs):
                                    for appID, statu in g.graph['Application_info']['applicationStatus'].item():
                                        if statu == 0:
                                            continue
                                        if statu == 1:
                                            services = g.graph['Application_info']['applicationServices'][appID]
                                            services = services.replace("[",'').replace("]",'')
                                            services = services.split(',')
                                            if (g.graph['Service_info']['ServiceID'][j] in services):
                                                g.graph['Application_info']['applicationStatus'][appID]=0
                                                Downtime[appID] = x['time']
                                            else:
                                                continue
                                else:
                                    continue
                        
                        if g.graph['VNF_info']['VNFBackupType'][i] == '主备':
                            if (g.graph['VNF_info']['VNFBackupNode'][i] in x['EvolFailNodesSet']):#备用路径中断，记录下此时的故障时间
                                for j in range(len(g.graph['Service_info'])):
                                    VNFs = g.graph['Service_info']['ServiceVNF'][j]
                                    VNFs = VNFs,replace("[",'').replace("]",'')
                                    VNFs = VNFs.split(',')
                                    if (g.graph['VNF_info']['VNFID'][i] in VNFs):#寻找该VNF上的Server
                                        for appID, statu in g.graph['Application_info']['applicationStatus'].item():
                                            if statu == 0:
                                                continue
                                            if statu == 1:
                                                services = g.graph['Application_info']['applicationServices'][appID]
                                                services = services.replace("[",'').replace("]",'')
                                                services = services.split(',')
                                                if (g.graph['Service_info']['ServiceID'][j] in services):#遍历Server上的业务
                                                    g.graph['Application_info']['applicationStatus'][appID]=0
                                                    Downtime[appID] = x['time']
                                                else:
                                                    continue
                                                    
                                    else:
                                        continue
                            else:#备用路径没有中断，VNF进行主备倒换
                                a = g.graph['VNF_info']['VNFDeployNode'][i]
                                g.graph['VNF_info']['VNFDeployNode'][i] = g.graph['VNF_info']['VNFBackupNode'][i]
                                g.graph['VNF_info']['VNFBackupNode'][i] = a
                                for j in range(len(g.graph['Service_info'])):
                                    VNFs = g.graph['Service_info']['ServiceVNF'][j]
                                    VNFs = VNFs,replace("[",'').replace("]",'')
                                    VNFs = VNFs.split(',')
                                    if (g.graph['VNF_info']['VNFID'][i] in VNFs):#寻找该VNF上的Server
                                        for appID, statu in g.graph['Application_info']['applicationStatus'].item():
                                            if statu == 0:
                                                continue
                                            if statu == 1:
                                                services = g.graph['Application_info']['applicationServices'][appID]
                                                services = services.replace("[",'').replace("]",'')
                                                services = services.split(',')
                                                if (g.graph['Service_info']['ServiceID'][j] in services):#遍历Server上的业务
                                                    #将倒换时间加到业务不可用时间上
                                                    g.graph['Application_info']['applicationUnavilTime'][appID] += g.graph['VNF_info']['VNFFailST'][i]
                                                    #更改业务工作路径
                                                    g.graph['Application_info']['applicationWorkPath'][appID] = g.graph['Application_info']['applicationWorkPath'][appID].replace(g.graph['VNF_info']['VNFBackupNode'][i],g.graph['VNF_info']['VNFDeployNode'][i])
                                                else:
                                                    continue
                                    else:
                                        continue
                                    
                                    
                        else:#Nway型VNF
                        
                   
                        
                    
                    
                    
    
    evol.apply(rul_ana,axis=1)
    
    return G_T
   
     

def test():
    pass

if __name__ == '__main__':
    test()