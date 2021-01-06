# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:36:41 2020

@author: zhujuxing
"""

import networkx as nx
import pandas as pd
import xlrd




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
    fname = 'evol.xlsx'
    bk = xlrd.open_workbook(fname)
    #获取当前文档的表
    shxrange = range(bk.nsheets)
    try:
        sh = bk.sheet_by_name("Sheet1")
    except:
        print('no sheet in %s ',format(fname))
    #获取行数
    nrows = sh.nrows
    #获取列数
    ncols = sh.ncols


    key =sh.row_values(0)# 这是第一行数据，作为字典的key值

    if nrows <= 1:
        print("没数据")
    else:
        j = 0
        for i in range(nrows-1):
            x ={}
            j +=1
            values = sh.row_values(j)
            for v in range(ncols):
                # 把key值对应的value赋值给key，每行循环
                x[key[v]]=values[v]



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
                x['EvolRecoNodesSet'] = x['EvolRecoNodesSet'].replace("[",'').replace("]",'')
                x['EvolRecoNodesSet'] = x['EvolRecoNodesSet'].split(',')

                for RecoNode in x['EvolRecoNodesSet']:#遍历演化态下的修复节点集
                    if len(RecoNode) !=0:
                        RecoNode = list(RecoNode)
                        if RecoNode['NodeType'] == 'DCGW' or RecoNode['NodeType'] == 'TOR' or RecoNode[
                            'NodeType'] == 'EOR':  # 修复节点为DCGW
                            for appID, statu in g.graph['Application_info']['applicationStatus'].item():
                                if status == 1:
                                    continue
                                else:
                                    nodes = g.graph['Application_info']['applicationWorkPath'][appID]
                                    nodes = nodes.replace("[", '').replace("]", '')
                                    nodes = nodes.split(',')
                                    for node in nodes:
                                        if node in x['EvolFailNodesSet']:
                                            break
                                        else:
                                            continue

                        if RecoNode['NodeType'] == 'Server':  # 修复节点为Server
                            pass

                        if RecoNode['NodeType'] == 'VSwitch':  # 修复节点为VSwitch
                            pass

                        if RecoNode[0] == 'VM':#修复节点为VM
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
                x['EvolFailNodesSet'] = x['EvolFailNodesSet'].replace("[",'').replace("]",'')
                x['EvolFailNodesSet'] = x['EvolFailNodesSet'].split(',')

                    if len(RecoNode) !=0:
                        RecoNode = list(RecoNode)
                for FailNode in x['EvolFailNodesSet']:#遍历演化态下的故障节点集
                    if len(RecoNode) !=0:
                        FailNode = list(FailNode)
                        if FailNode[0] == 'DCGW' or FailNode == 'EOR' or FailNode == 'TOR':#故障节点为DCGW
                            pass

                        if FailNode[0] == 'Server':#故障节点为Server
                            pass

                        if FailNode[0] == 'VM':#故障节点为VM
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

class Application:
    def __init__(self, ApplicationID, ApplicationLogicPath, ApplicationPhysPath, ApplicationDownTime):
        self.ApplicationID = ApplicationID
        self.ApplicationLogicPath = ApplicationLogicPath
        self.ApplicationPhysPath = ApplicationPhysPath
        self.ApplicationDownTime = ApplicationDownTime

    def displayApp(self):
        print("Application Name: " + self.ApplicationID)
        print("Application Logical Path:", self.ApplicationLogicPath)
        print("Application Physical Path:", self.ApplicationPhysPath)
        print("Application Total Downtime:", self.ApplicationDownTime)


def test():
    g = nx.read_gpickle('test/g.gpickle')
    evol = pd.read_excel('test/evol2.xlsx', index_col=0)
    evol['EvolFailNodesSet'] = evol['EvolFailNodesSet'].apply(lambda x: eval(x))
    evol['EvolRecoNodesSet'] = evol['EvolRecoNodesSet'].apply(lambda x: eval(x))
    evol['CurrentAllFailedNode'] = [[] for i in range(len(evol))]

    node_info = pd.read_excel('test/file.xlsx', sheet_name='node_info')
    application_info = pd.read_excel('test/file.xlsx', sheet_name='Application_info')

    appID = application_info.iloc[0, 0]
    appLogicPath = application_info.iloc[0, 1]
    appPhysPath = application_info.iloc[0, 2]
    appDownTime = application_info.iloc[0, 3]
    app1 = Application(appID, appLogicPath, appPhysPath, appDownTime)
    app1.displayApp()

    pass

if __name__ == '__main__':
    test()