# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 02:25:22 2021

@author: HuangSiTong Cai
"""

import networkx as nx
import re
import pandas as pd
import NetEvoConGen
from NetEvoObjMod import CloudVritualizedNetwork
import copy
import os
import random
#TODO: 将功能拆解为多个小块函数

Uptime = {}  # 创建一个空字典，记录业务从故障状态转换到正常状态的时刻
Downtime = {}  # 创建一个空字典，记录业务从正常状态转换到故障状态的时刻

def net_evo_rul_ana_test(g, fname):

    G_T = copy.copy(g)
    if type(fname) == str:
        evol = pd.read_excel(fname)
        evol['EvolTime'] = evol['EvolTime'].apply(eval)
        evol['EvolFailNodesSet'] = evol['EvolFailNodesSet'].apply(eval)
        evol['EvolRecoNodesSet'] = evol['EvolRecoNodesSet'].apply(eval)
    elif type(fname)== pd.DataFrame:
        evol = fname

    def rul_ana(x):
        print( '\n---------------Start-------------\n')
        print('x:', x)
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
        #for RecoNode in x['EvolRecoNodesSet']:#遍历演化态下的修复节点集

        for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
            if status == 1:
                continue
            if status == 0:                
                nodes = eval(G_T.graph['Application_info'].loc[appID,'ApplicationWorkPath'])
                #如果正在遍历的app工作链路中没有该节点，则恢复该app状态为1
                if (list(set(nodes).intersection(set(x['EvolFailNodesSet'])))) ==[]:
                    G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 1
                    Uptime[appID] = float(x['EvolTime'][0])
                    G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'] += (Uptime[appID] - Downtime[appID])

                else:#如果修复节点中有nway型VNF的节点，则该VNF中有一个节点恢复，该VNF就可用。
                    App_fail_node = list(set(nodes).intersection(set(x['EvolFailNodesSet'])))
                    # VNFs = G_T.graph['Application_info'].loc[appID,'ApplicationVNFs'].split(',')
                    VNFs = G_T.graph['Application_info'].loc[appID,'ApplicationVNFs'].strip('[]').split(',')
                    VNFs = VNFs[1:-1]
                    app_fail_VNFnodes = []
                    i = 0
                    for VNFID in VNFs:
                        try:
                            if G_T.graph['VNF_info'].loc[VNFID,'VNFBackupType'] == '2 Way':
                                VNFnodesSet = G_T.graph['VNF_info'].loc[VNFID,'VNFDeployNodes'].replace("[",'').replace("]",'').split(',')
                                if (list(set(App_fail_node).intersection(set(VNFnodesSet))) == VNFnodesSet):#
                                    break
                                else:
                                    #记录下业务VNF中故障的节点
                                    app_fail_VNFnodes = list(set((set(App_fail_node).intersection(set(VNFnodesSet)))).union(set(app_fail_VNFnodes)))
                                    i = i+1
                            else:
                                pass
                        except:
                            pass
                    if list(set(app_fail_VNFnodes).difference(set(x['EvolFailNodesSet']))) == [] and i == len(VNFs):
                        G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 1
                        Uptime[appID] = float(x['EvolTime'][0])
                    else:
                        pass

        for FailNode in x['EvolFailNodesSet']:#遍历演化态下的故障节点集
            if FailNode[:2] != 'Vs':
                Nodetype = ''.join(re.findall(r'[A-Za-z]', FailNode))
            else:
                Nodetype = 'Vs'

            if Nodetype != '':
                if Nodetype != '' and (Nodetype == 'D' or Nodetype == 'E' or Nodetype == 'T'):#故障节点为DCGW\EOR\TOR
                    hardwareFail(G_T, FailNode, x)

                if Nodetype == 'S':#故障节点为Server
                    continue#server故障还在调试中

                    # 获取故障server的vm节点列表fail_server_vm
                    fail_server_vm = []  # Vs子vm节点列表  如['V1', 'V2']
                    Edge_df = G_T.graph['Edge_info']
                    Server_index = Edge_df[
                        (Edge_df.EdgeSourceNode == FailNode)].index.tolist()  # Server节点在Edge_info中的索引    如 ['Eg9']
                    Vs_node = G_T.graph['Edge_info'].loc[
                        Server_index[0], 'EdgeDestinationNode']  # Server节点的Vs节点            如 'Vs1'
                    Vs_index = Edge_df[(
                            Edge_df.EdgeSourceNode == Vs_node)].index.tolist()  # Vs节点的索引                      如['Eg13','Eg14','Eg15','Eg16']

                    for i in Vs_index:
                        node_i = G_T.graph['Edge_info'].loc[i, 'EdgeDestinationNode']  # vs的子节点  如 'V1'
                        if G_T.graph['Node_info'].loc[node_i, 'NodeType'] == 'VM':
                            fail_server_vm.append(node_i)
                        else:
                            pass

                    VNF_list = []  # 故障VNF
                    for VNFID, VNFDeployNode in G_T.graph['VNF_info'][
                        'VNFDeployNode'].items():  # 如 'VNF!'      '[V1,V3]'   '[V2]'
                        nodes = VNFDeployNode
                        nodes = str(nodes).replace("[", '').replace("]", '')  # 去掉[]   如 'V1,V3'
                        nodes = nodes.split(',')  # 如  ['V1', 'V3']

                        tmp = [val for val in nodes if val in fail_server_vm]  # 交集
                        if len(tmp) > 0:  # 有交集
                            VNF_list.append(VNFID)
                    # vnf_app = {}
                    # for VNF_i in VNF_list:
                    #     app_index = G_T.graph['Application_info'][(G_T.graph['Application_info'].ApplicationVNFs == VNF_i)].index.tolist()
                    #     vnf_app[vnf] = app_index

                    m = G_T.graph['Node_info'].loc[FailNode, 'NodeFailMT']  # 迁移时间

                    for VNF_i in VNF_list:
                        if G_T.graph['VNF_info'].loc[VNF_i, 'VNFBackupType'] == '主备':
                            s = re.findall("\d+",
                                           G_T.graph['VNF_info'].loc[VNF_i, 'VNFFailST'])  # 倒换时间(float(s[0]) / 3600)
                            app_index = G_T.graph['Application_info'][(G_T.graph[
                                                                           'Application_info'].ApplicationVNFs == VNF_i)].index.tolist()  # 故障VNF所在的业务    如 ['App1']
                            for app_i in app_index:
                                G_T.graph['Application_info'].loc[app_i, 'ApplicationDownTime'] += (
                                        (float(s[0]) / 3600) + (m / 3600))

                        elif G_T.graph['VNF_info'].loc[VNF_i, 'VNFBackupType'] == '2 Way':
                            app_index = G_T.graph['Application_info'][(G_T.graph[
                                                                           'Application_info'].ApplicationVNFs == VNF_i)].index.tolist()  # 故障VNF所在的业务    如 ['App1']
                            if (set(G_T.graph['VNF_info']['VNFDeployNode'][VNF_i].replace('[', '').replace(']', '')
                                            .split(',')).issubset(set(x['EvolFailNodesSet']))):  # 若0 way
                                for app_i in app_index:
                                    G_T.graph['Application_info'].loc[app_i, 'ApplicationStatus'] = 0
                                    Downtime[app_i] = float(x['EvolTime'][0])
                            else:  # 若 1 way
                                pass

                        else:  # 主机
                            app_index = G_T.graph['Application_info'][(G_T.graph[
                                                                           'Application_info'].ApplicationVNFs == VNF_i)].index.tolist()  # 故障VNF所在的业务    如 ['App1']
                            for app_i in app_index:
                                G_T.graph['Application_info'].loc[app_i, 'ApplicationStatus'] = 0
                                Downtime[app_i] = float(x['EvolTime'][0])

                    # 迁移策略

                    server_list = G_T.graph['Node_info'][(G_T.graph['Node_info'].NodeIdle == 0) & (
                            G_T.graph['Node_info'].NodeType == 'Server')].index.tolist()  # 空闲节点
                    server = random.choice(server_list)  # 迁移后的server

                    # 寻找迁移后的server子vm节点
                    server_vm = []  # server子vm节点列表  如['V3', 'V4']
                    Edge_df = G_T.graph['Edge_info']
                    Server_index = Edge_df[
                        (Edge_df.EdgeSourceNode == server)].index.tolist()  # Server节点在Edge_info中的索引    如 ['Eg9']
                    Vs_node = G_T.graph['Edge_info'].loc[
                        Server_index[0], 'EdgeDestinationNode']  # Server节点的Vs节点            如 'Vs1'
                    Vs_index = Edge_df[(
                            Edge_df.EdgeSourceNode == Vs_node)].index.tolist()  # Vs节点的索引                      如['Eg13','Eg14','Eg15','Eg16']

                    for i in Vs_index:
                        node_i = G_T.graph['Edge_info'].loc[i, 'EdgeDestinationNode']  # vs的子节点  如 'V1'
                        if G_T.graph['Node_info'].loc[node_i, 'NodeType'] == 'VM':
                            server_vm.append(node_i)
                        else:
                            pass

                        # 更新VNF部署节点信息

                        fail_server_vm = []  # Vs子vm节点列表  如['V1', 'V2']
                        server_vm = []  # server子vm节点列表  如['V4', 'V5']

                        for i in range(len(VNF_list)):
                            DeployNode = G_T.graph['VNF_info'].loc[VNF_list[i], 'VNFDeployNode']  # 如 ['V1', 'V3']
                            tmp1 = [val for val in fail_server_vm if val in DeployNode]  # 如 ['V1']
                            update_DeployNode = DeployNode.replace(tmp1, server_vm[i])  # 如 ['V4', 'V3']

                
                if Nodetype == 'Vs':#故障节点为Vswitch
                    vSwitchFail(G_T, FailNode, x)

                if Nodetype == 'V':#故障节点为VM
                    VMFail(G_T, FailNode, x)
        print('---------------end---------------')
    evol.apply(rul_ana,axis=1)
    print("\nApp Down Start time: ", Downtime)
    print("App Up Start time: ", Uptime)
    print("App Total Downtime: ", round(G_T.graph['Application_info'].loc['App1', 'ApplicationDownTime'], 5))
    print("App Total Downtime: ", round(G_T.graph['Application_info'].loc['App2', 'ApplicationDownTime'], 5))
    # print(G_T.graph['Application_info'].loc['App1', 'ApplicationWorkPath'])
    # print(G_T.nodes['V1'])
    # print(G_T.graph['Application_info']['ApplicationVNFs'])
    # print(G_T.graph['VNF_info']['VNFDeployNode'])
    return G_T

    # -*- coding: utf-8 -*-

#针对硬件故障节点，如DCGW，EOR，TOR的处理方式
def hardwareFail(G_T, FailNode, x):
    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
        if status == 0:
            continue
        if status == 1:
            nodes = eval(G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'])
            if (FailNode in nodes):
                G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 0
                Downtime[appID] = float(x['EvolTime'][0])
            else:
                continue

def vSwitchFail(G_T, FailNode, x):
    Nodetype = ''.join(re.findall(r'[A-Za-z]', FailNode))
    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
        if status == 0:
            continue
        if status == 1:
            nodes = eval(G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'])
            print("nodes:", nodes)
            if (FailNode in nodes):
                G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 0
                Downtime[appID] = float(x['EvolTime'][0])
            else:
                continue
            
def VMFail(G_T, FailNode, x):
    for VNFID, VNFDeployNode in G_T.graph['VNF_info']['VNFDeployNode'].items():
        nodes = VNFDeployNode
        nodes = str(nodes).replace("[", '').replace("]", '')
        nodes = nodes.split(',')
        if (FailNode in nodes):
            FailNode = ''.join(FailNode)
            if G_T.graph['VNF_info']['VNFBackupType'][VNFID] == '主机':
                for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                    if status == 0:
                        continue
                    if status == 1:
                        # VNFNode = G_T.graph['VNF_info'].loc[G_T.graph['Application_info'].loc[appID, 'ApplicationService'], 'VNFDeployNode']
                        ApplicationNode = eval(G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'])
                        if (FailNode in ApplicationNode):
                            G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 0
                            Downtime[appID] = float(x['EvolTime'][0])
                        else:
                            continue

            if G_T.graph['VNF_info']['VNFBackupType'][VNFID] == '主备':
                if (G_T.graph['VNF_info']['VNFBackupNode'][VNFID].replace('[', '').replace(']', '') in x[
                    'EvolFailNodesSet']):  # 备用路径中断，记录下此时的故障时间
                    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                        if status == 0:
                            continue
                        if status == 1:
                            # VNFNode = G_T.graph['VNF_info'].loc[G_T.graph['Application_info'].loc[appID, 'ApplicationService'], 'VNFDeployNode']
                            ApplicationNode = eval(G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'])
                            if (FailNode in ApplicationNode):
                                G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 0
                                Downtime[appID] = float(x['EvolTime'][0])
                            else:
                                continue
                else:  # 备用路径没有中断，VNF进行主备倒换
                    # TODO: 增加倒换时业务中断的考虑
                    Node_name = G_T.graph['VNF_info'].loc[VNFID, 'VNFDeployNode']
                    G_T.graph['VNF_info'].loc[VNFID, 'VNFDeployNode'] = G_T.graph['VNF_info'].loc[
                        VNFID, 'VNFBackupNode']
                    G_T.graph['VNF_info'].loc[VNFID, 'VNFBackupNode'] = Node_name
                    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                        if status == 0:
                            continue
                        if status == 1:
                            VNFs = G_T.graph['Application_info'].loc[appID, 'ApplicationVNFs']

                            if (VNFID in VNFs):
                                # 将倒换时间加到业务不可用时间上
                                s = re.findall("\d+", G_T.graph['VNF_info'].loc[VNFID, 'VNFFailST'])
                                G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'] += (float(s[0]) / 3600)
                                # 更改业务工作路径
                                a = G_T.graph['VNF_info'].loc[VNFID, 'VNFBackupNode'].replace("[", '').replace("]",
                                                                                                               '').join(
                                    '\'\'')
                                b = G_T.graph['VNF_info'].loc[VNFID, 'VNFDeployNode'].replace("[", '').replace("]",
                                                                                                               '').join(
                                    '\'\'')
                                G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'] = \
                                    G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'].join(
                                        '\'\'').replace(a, b).strip('\'')
                            else:
                                continue

            else:  # Nway性业务的故障处理
                if (set(G_T.graph['VNF_info']['VNFDeployNode'][VNFID].replace('[', '').replace(']', '')
                                .split(',')).issubset(set(x['EvolFailNodesSet']))):
                    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
                        if status == 0:
                            continue
                        if status == 1:
                            VNFs = G_T.graph['Application_info'].loc[appID, 'ApplicationVNFs']
                            if (VNFID in VNFs):
                                G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 0
                                Downtime[appID] = float(x['EvolTime'][0])
                            else:
                                continue
                else:
                    continue



if __name__ == '__main__':
    g = CloudVritualizedNetwork(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file.xlsx')
    fname = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+ 'newData/evol3.xlsx'
    g_t = net_evo_rul_ana_test(g, fname)
    #for i in range(100):
#        g_T = g.copy()
#        fname = NetEvoConGen.net_evo_con_gen(g_T,10)
#        g_T = net_evo_rul_ana_test(g, fname)
    
