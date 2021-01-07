# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:36:41 2020

@author: zhujuxing
"""

import networkx as nx
import pandas as pd
import xlrd
import re



Uptime = {}#创建一个空字典，记录业务从故障状态转换到正常状态的时刻
Downtime = {}#创建一个空字典，记录业务从正常状态转换到故障状态的时刻
g = nx.read_gpickle('g.gpickle')
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
        x['EvolTime'] = x['EvolTime'].replace("[",'').replace("]",'')
        x['EvolTime'] = x['EvolTime'].split(',')


       
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

           
            # 修复节点怎么操作，对这个集合下的所有节点操作x['EvolRecoNodesSet']
                # DCGW/EOR/TOR
                # Server
                # VM
        x['EvolRecoNodesSet'] = x['EvolRecoNodesSet'].replace("[",'').replace("]",'')
        x['EvolRecoNodesSet'] = x['EvolRecoNodesSet'].split(',')

        for RecoNode in x['EvolRecoNodesSet']:#遍历演化态下的修复节点集
            if len(RecoNode) !=0:
                RecoNode = list(RecoNode)
                if RecoNode[0] == 'D' or RecoNode[0] == 'T' or RecoNode[0] == 'E':  # 修复节点为DCGW
                    for appID, statu in g.graph['Application_info']['ApplicationStatus'].items():
                        if statu == 1:
                            continue
                        else:
                            nodes = g.graph['Application_info']['ApplicationWorkPath'][appID]
                            nodes = nodes.replace("[", '').replace("]", '')
                            nodes = nodes.split(',')
                            for node in nodes:
                                if node in x['EvolFailNodesSet']:
                                    break
                                else:
                                    continue

                if RecoNode[0] == 'S':  # 修复节点为Server
                    pass

               # if RecoNode['NodeType'] == 'VSwitch':  # 修复节点为VSwitch
               #     pass

                if RecoNode[0] == 'V':#修复节点为VM
                    for appID, statu in g.graph['Application_info']['ApplicationStatus'].items():
                        if statu == 1:
                            continue
                        if statu == 0:
                            nodes = g.graph['Application_info']['ApplicationWorkPath'][appID]
                            nodes = nodes.replace("[",'').replace("]",'')
                            nodes = nodes.split(',')
                            for node in nodes:
                                if (node in x['EvolFailNodesSet']):
                                    break
                                else:
                                    continue
                            g.graph['Application_info']['ApplicationStatus'][appID]=1
                            Uptime[appID] = x['EvolTime'][0]
                            g.graph['Application_info']['ApplicationUnavilTime'][appID] += (Uptime[appID]-Downtime[appID])
        # 故障节点集怎么操作，对这个集合下的所有节点操作x['EvolFailNodesSet']
            # DCGW/EOR/TOR
            # Server
            #VSwitch
            # VM
        x['EvolFailNodesSet'] = x['EvolFailNodesSet'].replace("[",'').replace("]",'')
        x['EvolFailNodesSet'] = x['EvolFailNodesSet'].split(',')
        for FailNode in x['EvolFailNodesSet']:#遍历演化态下的故障节点集
             FailNode_name = FailNode
             FailNode = list(FailNode)
             if len(FailNode) !=0:
               
                if FailNode[0] == 'D' or FailNode[0] == 'E' or FailNode[0] == 'T':#故障节点为DCGW
                    pass

                if FailNode[0] == 'S':#故障节点为Server
                    pass

                if FailNode[0] == 'V':#故障节点为VM
                    for i in range(len(g.graph['VNF_info'])):
                        nodes = g.graph['VNF_info']['VNFDeployNode'][i]
                        nodes = nodes.replace("[",'').replace("]",'')
                        nodes = nodes.split(',')
                        if (FailNode_name in nodes):
                            if g.graph['VNF_info']['VNFBackupType'][i] == '主机':
                                for j in range(len(g.graph['Service_info'])):
                                    VNFs = g.graph['Service_info']['ServiceVNF'][j]
                                    VNFs = VNFs.replace("[",'').replace("]",'')
                                    VNFs = VNFs.split(',')
                                    if (g.graph['VNF_info']['VNFID'][i] in VNFs):
                                        for appID, statu in g.graph['Application_info']['ApplicationStatus'].items():
                                            if statu == 0:
                                                continue
                                            if statu == 1:
                                                services = g.graph['Application_info']['ApplicationServices'][appID]
                                                services = services.replace("[",'').replace("]",'')
                                                services = services.split(',')
                                                if (g.graph['Service_info']['ServiceID'][j] in services):
                                                    g.graph['Application_info'].loc['appID','ApplicationStatus']=0
                                                    Downtime[appID] = x['EvolTime'][0]
                                                else:
                                                    continue
                                    else:
                                        continue

                            if g.graph['VNF_info']['VNFBackupType'][i] == '主备':
                                if (g.graph['VNF_info']['VNFBackupNode'][i] in x['EvolFailNodesSet']):#备用路径中断，记录下此时的故障时间
                                    for j in range(len(g.graph['Service_info'])):
                                        VNFs = g.graph['Service_info']['ServiceVNF'][j]
                                        VNFs = VNFs.replace("[",'').replace("]",'')
                                        VNFs = VNFs.split(',')
                                        if (g.graph['VNF_info']['VNFID'][i] in VNFs):#寻找该VNF上的Server
                                            for appID, statu in g.graph['Application_info']['ApplicationStatus'].items():
                                                if statu == 0:
                                                    continue
                                                if statu == 1:
                                                    services = g.graph['Application_info']['ApplicationService'][appID]
                                                    services = services.replace("[",'').replace("]",'')
                                                    services = services.split(',')
                                                    if (g.graph['Service_info'].index[j] in services):#遍历Server上的业务
                                                        g.graph['Application_info']['ApplicationStatus'][appID]=0
                                                        Downtime[appID] = x['EvolTime'][0]
                                                    else:
                                                        continue

                                        else:
                                            continue
                                else:#备用路径没有中断，VNF进行主备倒换
                                    a = g.graph['VNF_info'].loc[i,'VNFDeployNode']
                                    g.graph['VNF_info'].loc[i,'VNFDeployNode'] = g.graph['VNF_info'].loc[i,'VNFBackupNode']
                                    g.graph['VNF_info'].loc[i,'VNFBackupNode'] = a
                                    for j in range(len(g.graph['Service_info'])):
                                        VNFs = g.graph['Service_info']['ServiceVNF'][j]
                                        VNFs = VNFs.replace("[",'').replace("]",'')
                                        VNFs = VNFs.split(',')
                                        if (g.graph['VNF_info']['VNFID'][i] in VNFs):#寻找该VNF上的Server
                                            for appID, statu in g.graph['Application_info']['ApplicationStatus'].items():
                                                if statu == 0:
                                                    continue
                                                if statu == 1:
                                                    services = g.graph['Application_info']['ApplicationService'][appID]
                                                    services = services.replace("[",'').replace("]",'')
                                                    services = services.split(',')
                                                    if (g.graph['Service_info'].index[j] in services):#遍历Server上的业务
                                                        #将倒换时间加到业务不可用时间上
                                                        s = re.findall("\d+", g.graph['VNF_info']['VNFFailST'][i])
                                                        g.graph['Application_info']['ApplicationUnavailTime'][appID]  += float(s[0])
                                                        #更改业务工作路径
                                                        g.graph['Application_info']['ApplicationWorkPath'][appID] = g.graph['Application_info']['ApplicationWorkPath'][appID].replace(g.graph['VNF_info']['VNFBackupNode'][i],g.graph['VNF_info']['VNFDeployNode'][i])
                                                    else:
                                                        continue
                                        else:
                                            continue


                            else:#Nway型VNF
                                pass
    
    
    
    
    
'''  
                evol.apply(rul_ana,axis=1)
    
                return G_T] 

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
    '''
print(Downtime)
print(Uptime)
print(g.graph['Application_info']['ApplicationUnavailTime'])
print(g.graph['Application_info']['ApplicationWorkPath'])


# -*- coding: utf-8 -*-

