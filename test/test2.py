# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:36:15 2020

@author: zhujuxing
"""

import networkx as nx
import pandas as pd

g = nx.read_gpickle('g.gpickle')
evol = pd.read_excel('evol.xlsx',index_col=0,converters={})


g_T = g.copy()

def rul_ana(x):
    """
    

    Parameters
    ----------
    x : pd.Dataframe
        x是一个时态下的evol的dataframe.
        有三列.
        x['EvolTime']: List[Float],有两个元素，第一个表示当前演化态的开始时间，
        第二个表示当前演化态的结束时间。
        x['EvolFailNodesSet']: str,表示当前演化态的故障节点集合。
        x['EvolRecoNodesSet']: str，表示当前演化态的修复接地单集合。
        
    Returns
    -------
    

    """
    nonlocal g_T
    # 判断是修复还是故障节点
    
    
    
    # 修复节点怎么操作，对这个集合下的所有节点操作x['EvolRecoNodesSet']
        # DCGW/EOR/TOR
        # Server
        # VM
    # 故障节点集怎么操作，对这个集合下的所有节点操作x['EvolFailNodesSet']
        # DCGW/EOR/TOR
        # Server
        # VM

def net_evo_rul_ana(g,evol)->nx.Graph:
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
    g_T = g.copy()

    evol.apply(rul_ana,axis=1)
    
    return g_T
    

def test_rul_ana():
    x = evol.iloc[0]
    rul_ana(x)
    return g_T

if __name__ == '__main__':
    test_rul_ana()