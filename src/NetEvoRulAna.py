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
import openpyxl
import collections
from openpyxl import load_workbook
import random
#TODO: shortestPath 函数中都是从D1寻找至新VNF的路径，考虑后续是否要通过其它DCGW走

Uptime = {}  # 创建一个空字典，记录业务从故障状态转换到正常状态的时刻
Downtime = {}  # 创建一个空字典，记录业务从正常状态转换到故障状态的时刻

Uplist = []
Downlist = []
sheetNum = 0

def net_evo_rul_ana_test(g, fname):

    G_T = g
    # g.displayApp()


    if type(fname) == str:
        evol = pd.read_excel(fname)
        evol['EvolTime'] = evol['EvolTime'].apply(eval)
        evol['EvolFailNodesSet'] = evol['EvolFailNodesSet'].apply(eval)
        evol['EvolRecoNodesSet'] = evol['EvolRecoNodesSet'].apply(eval)
    elif type(fname) == pd.DataFrame:
        evol = fname

    def rul_ana(x):
        '''
        每条演化规则的分析函数
        '''
        
        #print(x['EvolTime'], 'Fail: ', x['EvolFailNodesSet'], 'Reco：', x['EvolRecoNodesSet'], '\n')
        for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
            if status == 1:
                continue
            if status == 0:
                RecoNodes(G_T, appID, x)
                for key, value in Uptime.items():
                    Uplist.append((key, value))
                for key, value in Downtime.items():
                    Downlist.append((key, value))


        for FailNode in x['EvolFailNodesSet']:#遍历演化态下的故障节点集
            if FailNode[:2] != 'Vs':
                Nodetype = ''.join(re.findall(r'[A-Za-z]', FailNode))
            else:
                Nodetype = 'Vs'

            if Nodetype != '':
                if Nodetype != '' and (Nodetype == 'D' or Nodetype == 'E' or Nodetype == 'T'):#故障节点为DCGW\EOR\TOR
                    hardwareFail(G_T, FailNode, x)

                if Nodetype == 'S':#故障节点为Server
                    serverFail(G_T, FailNode, x)
                
                if Nodetype == 'Vs':#故障节点为Vswitch
                    vSwitchFail(G_T, FailNode, x)

                if Nodetype == 'V':#故障节点为VM
                    VMFail(G_T, FailNode, x)
        print('已经完成%s时刻的网络演化'%x['EvolTime'])

    evol.apply(rul_ana,axis=1)
    # print(Uptime)
    # print(Downtime)
    Uptime.clear()
    Downtime.clear()

    return G_T

def clearVar():
    sheetNum = 0
    Uplist.clear()
    Downlist.clear()

def printLog():
    global Uplist
    global Downlist
    global sheetNum
    sheetName = 'Sheet' + str(sheetNum)
    Uplist = list(dict.fromkeys(Uplist))
    Downlist = list(dict.fromkeys(Downlist))

    upDF = pd.DataFrame(Uplist, columns=['AppName2', 'Up Time'])
    upDF = upDF.sort_values(by=['AppName2', 'Up Time'])
    upDF.reset_index(drop=True, inplace=True)

    downDF = pd.DataFrame(Downlist, columns=['AppName', 'Down Time'])
    downDF = downDF.sort_values(by=['AppName', 'Down Time'])
    downDF.reset_index(drop=True, inplace=True)

    appDownTimeDF = pd.concat([downDF, upDF], axis=1)
    appDownTimeDF = appDownTimeDF.drop(columns=['AppName2'])

    print(appDownTimeDF.to_string(index=False))

    Uplist.clear()
    Downlist.clear()
    upDF.iloc[0:0]
    downDF.iloc[0:0]
    appDownTimeDF.iloc[0:0]

def saveLog():
    global Uplist
    global Downlist
    global sheetNum
    sheetName = 'Sheet' + str(sheetNum)
    Uplist = list(dict.fromkeys(Uplist))
    Downlist = list(dict.fromkeys(Downlist))

    upDF = pd.DataFrame(Uplist, columns=['AppName2', 'Up Time'])
    upDF = upDF.sort_values(by=['AppName2', 'Up Time'])
    upDF.reset_index(drop=True, inplace=True)

    downDF = pd.DataFrame(Downlist, columns=['AppName', 'Down Time'])
    downDF = downDF.sort_values(by=['AppName', 'Down Time'])
    downDF.reset_index(drop=True, inplace=True)

    appDownTimeDF = pd.concat([downDF, upDF], axis=1)
    appDownTimeDF = appDownTimeDF.drop(columns=['AppName2'])

    print(appDownTimeDF.to_string(index=False))

    fileName = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".") + os.sep + 'test' + os.sep + 'AppDownTimeLog.xlsx'
    if os.path.isfile(fileName):
        pass
    else:
        wb = openpyxl.Workbook()
        wb.save(fileName)
    with pd.ExcelWriter(fileName,engine="openpyxl",mode='a') as writer:
        appDownTimeDF.to_excel(writer, sheet_name=sheetName)

    Uplist.clear()
    Downlist.clear()
    upDF.iloc[0:0]
    downDF.iloc[0:0]
    appDownTimeDF.iloc[0:0]



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
    #Nodetype = ''.join(re.findall(r'[A-Za-z]', FailNode))
    for appID, status in G_T.graph['Application_info']['ApplicationStatus'].items():
        if status == 0:
            continue
        if status == 1:
            nodes = eval(G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'])
            #print("nodes:", nodes)
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
                                #print('backup node:', a, 'deploy node:', b)
                                newPath = shortestPath(G_T, b)

                                '''
                                G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'] = \
                                    G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'].join(
                                        '\'\'').replace(a, b).strip('\'')
                                '''

                                G_T.graph['Application_info'].at[appID, 'ApplicationWorkPath'] = str(newPath)
                                #print('after set path:', G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'])

                                #print('work path2:', G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'])
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


def serverFail(G_T, FailNode, x):
    VNF_df = G_T.graph['VNF_info']
    app_df = G_T.graph['Application_info']
    edge_df = G_T.graph['Edge_info']
    node_df = G_T.graph['Node_info']

    # 获取故障server的vm列表fail_server_vm
    fail_server_vm = []  # Vs子vm节点列表  如['V1', 'V2']
    Server_index = edge_df[(edge_df.EdgeSourceNode == FailNode)].index.tolist()  # Server节点在Edge_info中的索引    如 ['Eg9']
    Vs_node = G_T.graph['Edge_info'].loc[Server_index[0], 'EdgeDestinationNode']  # Server节点的Vs节点            如 'Vs1'
    Vs_index = edge_df[
        (edge_df.EdgeSourceNode == Vs_node)].index.tolist()  # Vs节点的索引       如['Eg13','Eg14','Eg15','Eg16']
    for i in Vs_index:
        node_i = G_T.graph['Edge_info'].loc[i, 'EdgeDestinationNode']  # vs的子节点  如 'V1'
        if G_T.graph['Node_info'].loc[node_i, 'NodeType'] == 'VM':
            fail_server_vm.append(node_i)
        else:
            pass
    # 获取故障server涉及的VNF列表  VNF_list
    VNF_list = []  # 故障VNF   ['VNF1', 'VNF2']
    for VNFID, VNFDeployNode in G_T.graph['VNF_info']['VNFDeployNode'].items():  # 如 'VNF!' '[V1,V3]'   '[V2]'
        nodes = VNFDeployNode.strip('[]').split(',')  # ['V1', 'V3']
        tmp = [val for val in nodes if val in fail_server_vm]  # 交集
        if len(tmp) > 0:  # 有交集
            VNF_list.append(VNFID)
    # 获取故障VNF对应的app
    dict_VNF_app = {}  # {'VNF1': ['App2', 'App3'], 'VNF2': ['App1']}
    app_index_list = app_df.index.tolist()  # 所有app索引  ['App1', 'App2', 'App3']
    for VNF_i in VNF_list:  # ['VNF1', 'VNF2']
        App = []
        for app_i in app_index_list:
            ApplicationVNFs = app_df.loc[app_i, 'ApplicationVNFs'].strip('[]').split(
                ',')  # ['D1', 'VNF1', 'D1']
            if VNF_i in ApplicationVNFs:
                App.append(app_i)
            else:
                pass
        dict_VNF_app[VNF_i] = App

    # 是否有空闲server进行迁移，分类考虑
    server_list = node_df[(node_df.NodeIdle == 1) & (
                 node_df.NodeType == 'Server')].index.tolist()  # 空闲节点  ['S3']

    if len(server_list) == 0:  # 若无空闲server
        # 按节点单独故障处理
        vSwitchFail(G_T, Vs_node, x)
        for vm_i in fail_server_vm:
            x['EvolFailNodesSet'].append(vm_i)   # 更新故障节点集
        for vm_i in fail_server_vm:
            VMFail(G_T, vm_i, x)
    else:  # 有空闲server
        # 迁移信息准备：迁移节点server、更改状态、迁移时间m、server的vm列表server_vm
        server = random.choice(server_list)  # 迁移后的server    如'S3'
        node_df.loc[server, 'NodeIdle'] = 0  # 状态变为占用
        node_df.loc[FailNode, 'NodeIdle'] = 1  # 状态变为空闲
        m = node_df.loc[FailNode, 'NodeFailMT']  # 迁移时间 h
        # 获取server的vm列表server_vm
        server_vm = []  # server子vm节点列表  如['V5', 'V6']
        Edge_df = G_T.graph['Edge_info']
        Server_index = Edge_df[
            (Edge_df.EdgeSourceNode == server)].index.tolist()  # Server节点在Edge_info中的索引    如 ['Eg11']
        Vs_node = G_T.graph['Edge_info'].loc[
            Server_index[0], 'EdgeDestinationNode']  # Server节点的Vs节点     如 'Vs3'
        Vs_index = Edge_df[(
                Edge_df.EdgeSourceNode == Vs_node)].index.tolist()  # Vs节点的索引   如['Eg21','Eg22','Eg23','Eg24']
        for i in Vs_index:
            node_i = G_T.graph['Edge_info'].loc[i, 'EdgeDestinationNode']  # vs的子节点  如 'V5'
            if G_T.graph['Node_info'].loc[node_i, 'NodeType'] == 'VM':
                server_vm.append(node_i)
            else:
                pass

        # 是否有主备型VNF　有则主备倒换
        type = 0
        Backup_ok = []     #备好的VNF列表
        Backup_fail = []   #备断的VNF列表
        for VNF_i in VNF_list:
            if VNF_df.loc[VNF_i, 'VNFBackupType'] == '主备':
                s = re.findall("\d+", G_T.graph['VNF_info'].loc[VNF_i, 'VNFFailST'])  # 倒换时间  ['10']  单位s
                if len(list(set(VNF_df['VNFBackupNode'][VNF_i].strip('[]').split(',')).intersection(
                        set(x['EvolFailNodesSet'])))) == 0:  # 备没断
                    Backup_ok.append(VNF_i)
                    # VNF倒换  更新主备节点
                    deployNode = VNF_df.loc[VNF_i, 'VNFDeployNode']
                    backupNode = VNF_df.loc[VNF_i, 'VNFBackupNode']
                    VNF_df.at[VNF_i, 'VNFDeployNode'] = backupNode
                    VNF_df.at[VNF_i, 'VNFBackupNode'] = deployNode
                else:
                    Backup_fail.append(VNF_i)
            else:
                pass
        # 分类讨论
        if len(Backup_ok) > 0:  # vnf存在备好
            type = 1
        elif len(Backup_ok) == 0 and len(Backup_ok) > 0:  # 所有vnf备断
            type = 2
        else:  # 无主备
            type = 3

        # 迁移, 更新故障VNF的VNFDeployNode 或 BackupNode
        for i in range(len(VNF_list)):  # 故障server的VNF  i如 0 1 2 3
            if VNF_df.loc[VNF_list[i], 'VNFBackupType'] == '主备':
                if VNF_list[i] in Backup_ok:  # 备好的vnf  迁移的是其备节点
                    BackupNode = VNF_df.loc[VNF_list[i], 'VNFBackupNode']     # '[V1]'
                    node = VNF_df.loc[VNF_list[i], 'VNFBackupNode'].strip('[]').split(',')   #  ['V1']
                    update_BackupNode = BackupNode.replace(node[0], server_vm[i])   # '[V7]'     # 前换成后   输入、结果都为str格式
                    VNF_df.loc[VNF_list[i], 'BackupNode'] = update_BackupNode
                else:   # 备断的vnf  迁移的是部署节点
                    DeployNode = VNF_df.loc[VNF_list[i], 'VNFDeployNode']     # '[V1]'
                    node = VNF_df.loc[VNF_list[i], 'VNFDeployNode'].strip('[]').split(',')   #  ['V1']
                    update_DeployNode = DeployNode.replace(node[0], server_vm[i])   # '[V7]'     # 前换成后   输入、结果都为str格式
                    VNF_df.loc[VNF_list[i], 'DeployNode'] = update_DeployNode
            elif VNF_df.loc[VNF_list[i], 'VNFBackupType'] == '主机':
                DeployNode = VNF_df.loc[VNF_list[i], 'VNFDeployNode']  # '[V1]'
                node = VNF_df.loc[VNF_list[i], 'VNFDeployNode'].strip('[]').split(',')  # ['V1']
                try: 
                    update_DeployNode = DeployNode.replace(node[0], server_vm[i])  # '[V7]'     # 前换成后   输入、结果都为str格式
                except:
                    pass
                VNF_df.loc[VNF_list[i], 'DeployNode'] = update_DeployNode
            else:  # 2way
                DeployNode = VNF_df.loc[VNF_list[i], 'VNFDeployNode']  # 如 '[V1,V3]'
                node = VNF_df.loc[VNF_list[i], 'VNFDeployNode'].strip('[]').split(',')  # ['V1','V3']
                tmp1 = [val for val in fail_server_vm if val in node]  # 如 ['V1']
                try:
                    update_DeployNode = DeployNode.replace(tmp1[0], server_vm[i])  # 如'[V7,V3]'
                except:
                    pass
                VNF_df.loc[VNF_list[i], 'VNFDeployNode'] = update_DeployNode

        # 根据VNF部署节点 获取新工作路径path  更新业务工作路径
        for VNF_i in VNF_list:  # ['VNF1']
            App_list = dict_VNF_app[VNF_i]  # ['App2', 'App3']
            for App_i in App_list:
                # 获取故障业务的vnf列表  vnfs
                vnfs = []
                ApplicationVNFs = app_df.loc[App_i, 'ApplicationVNFs'].strip('[]').split(',')  # ['D1', 'VNF1','VNF2','VNF3', 'D1']
                h = len(ApplicationVNFs)
                for i in range(1,h-1):
                    vnfs.append(ApplicationVNFs[i])
                # 对业务的每个vnf寻找路径
                path = []
                for VNF_i in vnfs:
                    DeployNode = VNF_df.loc[VNF_i, 'VNFDeployNode'].strip('[]').split(',')  # ['V5', 'V3']
                    for node_i in DeployNode:  # 考虑2way有2个部署节点
                        path_i = shortestPath(G_T, node_i)
                        path.extend(path_i)
                app_df.loc[App_i, 'ApplicationWorkPath'] = str(path)  # 更新App_i工作路径

        # 记录VNF中断时间
        dict_vnf_dowmtime = {}
        if type == 1:  # 有主备型 存在备好的vnf
            for VNF_i in VNF_list:
                if VNF_df.loc[VNF_i, 'VNFBackupType'] == '主机':
                    dict_vnf_dowmtime[VNF_i] = ((float(s[0]) / 3600) + m) # VNF中断时间为倒换+迁移时间
                elif VNF_df.loc[VNF_i, 'VNFBackupType'] == '主备':
                    if VNF_i in Backup_ok:  # 备好
                        dict_vnf_dowmtime[VNF_i] = (float(s[0]) / 3600)  # VNF中断时间为倒换时间
                    else:  # 备断
                        dict_vnf_dowmtime[VNF_i] = ((float(s[0]) / 3600) + m)  # VNF中断时间为倒换+迁移时间
                else:  # 2way
                    VNF_node = VNF_df['VNFDeployNode'][VNF_i].strip('[]').split(',')    # ['V1','V3']
                    for node in VNF_node:
                        if node not in fail_server_vm:    # 找到另一个节点
                            if node in x['EvolFailNodesSet']:  # 0 way
                                dict_vnf_dowmtime[VNF_i] = ((float(s[0]) / 3600) + m)  # VNF中断时间为倒换+迁移时间
                            else:  # 1 way
                                pass
                        else:
                            pass

        elif type == 2:  # 主备型 全部备断
            for VNF_i in VNF_list:
                if VNF_df.loc[VNF_i, 'VNFBackupType'] == '主机':
                    dict_vnf_dowmtime[VNF_i] = m   # VNF中断时间为迁移时间
                elif VNF_df.loc[VNF_i, 'VNFBackupType'] == '主备':
                    dict_vnf_dowmtime[VNF_i] = m  # VNF中断时间为迁移时间
                else:  # 2way
                    VNF_node = VNF_df['VNFDeployNode'][VNF_i].strip('[]').split(',')    # ['V1','V3']
                    for node in VNF_node:
                        if node not in fail_server_vm:    # 找到另一个节点
                            if node in x['EvolFailNodesSet']:  # 0 way
                                dict_vnf_dowmtime[VNF_i] = m   #  VNF中断时间为迁移时间
                            else:  # 1 way
                                pass
                        else:
                            pass

        elif type == 3:  # 无主备型
            for VNF_i in VNF_list:
                        if VNF_df.loc[VNF_i, 'VNFBackupType'] == '主机':
                            dict_vnf_dowmtime[VNF_i] = m    # VNF中断时间为迁移时间
                        else:  # 2way
                            VNF_node = VNF_df['VNFDeployNode'][VNF_i].strip('[]').split(',')  # ['V1','V3']
                            for node in VNF_node:
                                if node not in fail_server_vm:  # 找到另一个节点
                                    if node in x['EvolFailNodesSet']:  # 0 way
                                        dict_vnf_dowmtime[VNF_i] = m    # VNF中断时间为迁移时间
                                    else:  # 1 way
                                        pass
                                else:
                                    pass
        # 更新业务中断时间
        for appID, ApplicationVNFs in app_df['ApplicationVNFs'].items():
            # 获取故障业务的vnf列表  vnfs
            vnfs = []
            ApplicationVNFs = ApplicationVNFs.strip('[]').split(',')  # ['D1', 'VNF1','VNF2','VNF3', 'D1']
            h = len(ApplicationVNFs)
            for i in range(1, h - 1):
                vnfs.append(ApplicationVNFs[i])    #[ 'VNF1','VNF2','VNF3']
            # 取VNF中断时间最大值
            downtime = []
            for vnf_i in vnfs:
                if vnf_i in dict_vnf_dowmtime.keys():
                    downtime.append(dict_vnf_dowmtime[vnf_i])
                else:  # 若vnf没有中断时间
                    pass
            if len(downtime) == 0:  # 若业务的vnf没有中断
                pass
            else:
                time = max(downtime)
                app_df.loc[appID, 'ApplicationDownTime'] += time  # 更新业务中断时间
    a = 1



def RecoNodes(G_T, appID, x):
    nodes = eval(G_T.graph['Application_info'].loc[appID, 'ApplicationWorkPath'])
    # 如果正在遍历的app工作链路中没有该节点，则恢复该app状态为1
    if (list(set(nodes).intersection(set(x['EvolFailNodesSet'])))) == []:
        G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 1
        Uptime[appID] = float(x['EvolTime'][0])

        G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'] += (Uptime[appID] - Downtime[appID])
        G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'] = G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'].round(7)


    else:  # 如果修复节点中有nway型VNF的节点，则该VNF中有一个节点恢复，该VNF就可用。
        App_fail_node = list(set(nodes).intersection(set(x['EvolFailNodesSet'])))
        VNFs = G_T.graph['Application_info'].loc[appID, 'ApplicationVNFs'].strip('[]').split(',')
        VNFs = VNFs[1:-1]
        app_fail_VNFnodes = []
        i = 0
        for VNFID in VNFs:
            if G_T.graph['VNF_info'].loc[VNFID, 'VNFBackupType'] == '2 Way':
                VNFnodesSet = G_T.graph['VNF_info'].loc[VNFID, 'VNFDeployNode'].replace("[", '').replace("]",'').split(',')                                                                                       
                if (list(set(App_fail_node).intersection(set(VNFnodesSet))) == VNFnodesSet):  #
                    break
                else:
                    # 记录下业务VNF中故障的节点
                    app_fail_VNFnodes = list(
                        set((set(App_fail_node).intersection(set(VNFnodesSet)))).union(set(app_fail_VNFnodes)))
                    i = i + 1
            else:
                pass
        if list(set(app_fail_VNFnodes).difference(set(x['EvolFailNodesSet']))) == [] and i == len(VNFs):
            G_T.graph['Application_info'].loc[appID, 'ApplicationStatus'] = 1
            Uptime[appID] = float(x['EvolTime'][0])
            G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'] += (Uptime[appID] - Downtime[appID])
            G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'] = G_T.graph['Application_info'].loc[appID, 'ApplicationDownTime'].round(7)
        else:
            pass

def shortestPath(g, targetNode):
    targetNode = targetNode.strip('\'')
    shortestPath = nx.shortest_path(g, source="D1", target=targetNode )
    reversePath = shortestPath.copy()
    reversePath.reverse()
    shortestPath.extend(reversePath)
    return shortestPath

def testRulAna(gName, evolName):
    g_t = net_evo_rul_ana_test(gName, evolName)
    appAvaData = g_t.graph['Application_info'][['ApplicationDownTime']]
    return appAvaData

if __name__ == '__main__':
    g = CloudVritualizedNetwork(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file_128server.xlsx')
    fname = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep + 'RulAnaTestFile/evol_zjm.xlsx'
    g_t = net_evo_rul_ana_test(g, fname)
    # g.displayApp()
    # printLog()







