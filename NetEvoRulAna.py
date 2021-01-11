# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 02:25:22 2021

@author: HuangSiTong Cai
"""

import networkx as nx
import re
import pandas as pd
import NetEvoConGen

def net_evo_rul_ana_test(g, fname):
    Uptime = {}  # 创建一个空字典，记录业务从故障状态转换到正常状态的时刻
    Downtime = {}  # 创建一个空字典，记录业务从正常状态转换到故障状态的时刻
    G_T = g.copy()
    if type(fname) == str:
        evol = pd.read_excel(fname)
        evol['EvolTime'] = evol['EvolTime'].apply(eval)
        evol['EvolFailNodesSet'] = evol['EvolFailNodesSet'].apply(eval)
        evol['EvolFailNodesSet'] = evol['EvolRecoNodesSet'].apply(eval)
    elif type(fname)== pd.DataFrame:
        evol = fname

    def rul_ana(x):
        '''
            Parameters
            ----------
            x : TYPE
                x是一个时态下的evol的dataframe,x['EvolFailNodesSet'],x['EvolRecoNodesSet']
                x['time']
            Returns
            -------
            None.

        '''

        nonlocal G_T       
        # 修复节点怎么操作，对这个集合下的所有节点操作x['EvolRecoNodesSet']
           

        for RecoNode in x['EvolRecoNodesSet']:#遍历演化态下的修复节点集

            if len(RecoNode) != 0:
                RecoNode = list(RecoNode)
                
                for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                    if status == 1:
                        continue
                    if status == 0:
                        nodes = G_T.graph['Application_info']['ApplicationWorkPath'][appID]
                        nodes = nodes.replace("[", '').replace("]", '')
                        nodes = nodes.split(',')
                        for node in nodes:
                            if (node in x['EvolFailNodesSet']):
                                break
                            else:
                                continue
                        G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 1
                        Uptime[appID] = float(x['EvolTime'][0])
                        try: # TODO:调试BUG 
                            G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'] += (Uptime[appID] - Downtime[appID])
                        except:
                            pass

        # 故障节点集怎么操作，对这个集合下的所有节点操作x['EvolFailNodesSet']
            # DCGW/EOR/TOR
            # Server
            #VSwitch
            # VM
        for FailNode in x['EvolFailNodesSet']:#遍历演化态下的故障节点集
             FailNode_name = FailNode
             FailNode = list(FailNode)
             if len(FailNode) !=0:
                if FailNode[0] == 'D' or FailNode[0] == 'E' or FailNode[0] == 'T':#故障节点为DCGW
                    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                        if status == 0:
                            continue
                        if status == 1:
                            nodes = G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath']
                            nodes = nodes.replace("[", '').replace("]", '')
                            nodes = nodes.split(',')
                            for node in nodes:
                                if (node in x['EvolFailNodesSet']):
                                    G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 0
                                    Downtime[appID] = float(x['EvolTime'][0])
                                    break
                                else:
                                    continue

                if FailNode[0] == 'S':#故障节点为Server
                    pass

                if FailNode[0] == 'V':#故障节点为VM
                    for VNFID, VNFDeployNode in G_T.graph['VNF_info']['VNFDeployNode'].items():
                        nodes = VNFDeployNode
                        nodes = str(nodes).replace("[",'').replace("]",'')
                        nodes = nodes.split(',')
                        if (FailNode_name in nodes):
                            FailNode = ''.join(FailNode)
                            if G_T.graph['VNF_info']['VNFBackupType'][VNFID] == '主机':
                                for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                                    if status == 0:
                                        continue
                                    if status == 1:
                                        VNFNode = G_T.graph['VNF_info'].loc[G_T.graph['Application_info'].loc[appID, 'ApplicationService'], 'VNFDeployNode']
                                        if (FailNode in VNFNode):
                                            G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 0
                                            Downtime[appID] = float(x['EvolTime'][0])
                                        else:
                                            continue

                            if G_T.graph['VNF_info']['VNFBackupType'][VNFID] == '主备':
                                if (G_T.graph['VNF_info']['VNFBackupNode'][VNFID].replace('[', '').replace(']', '') in x['EvolFailNodesSet']):#备用路径中断，记录下此时的故障时间
                                    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                                        if status == 0:
                                            continue
                                        if status == 1:
                                            VNFNode = G_T.graph['VNF_info'].loc[G_T.graph['Application_info'].loc[appID, 'ApplicationService'], 'VNFDeployNode']
                                            if (FailNode in VNFNode):
                                                G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 0
                                                Downtime[appID] = float(x['EvolTime'][0])
                                            else:
                                                continue
                                else:#备用路径没有中断，VNF进行主备倒换
                                    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                                        if status == 0:
                                            continue
                                        if status == 1:
                                            VNF = G_T.graph['Application_info'].loc[appID, 'ApplicationService']
                                            VNFNode = G_T.graph['VNF_info'].loc[VNF, 'VNFDeployNode']
                                            if (FailNode in VNFNode):
                                                # 将倒换时间加到业务不可用时间上
                                                s = re.findall("\d+", G_T.graph['VNF_info']['VNFFailST'][VNF])
                                                G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'] += (float(s[0]) / 3600)# 更改业务工作路径
                                                a = G_T.graph['VNF_info'].loc[VNF, 'VNFBackupNode'].replace("[", '').replace("]", '')
                                                b = G_T.graph['VNF_info'].loc[VNF, 'VNFDeployNode'].replace("[", '').replace("]", '')
                                                G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'] = \
                                                G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'].replace(a, b)
                                            else:
                                                continue

                            else:#Nway型VNF
                                pass
    evol.apply(rul_ana,axis=1)
    print("\nApp Down Start time: ", Downtime)
    print("App Up Start time: ", Uptime)
    print("App Total Downtime: ", round(G_T.graph['Application_info'].loc['App1', 'ApplicationDownTime'], 5))
    print(G_T.graph['Application_info'].loc['App1', 'ApplicationWorkPath'])
    print(G_T.nodes['V1'])
    return G_T

    # -*- coding: utf-8 -*-


if __name__ == '__main__':
    g = nx.read_gpickle('test/newData/g.gpickle')
    fname = 'test/newData/evol3.xlsx'
    g_t = net_evo_rul_ana_test(g, fname)
    #for i in range(100):
#        g_T = g.copy()
#        fname = NetEvoConGen.net_evo_con_gen(g_T,10)
#        g_T = net_evo_rul_ana_test(g, fname)
    
