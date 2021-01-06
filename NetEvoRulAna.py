# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:36:41 2020

@author: zhujuxing
"""

import networkx as nx
import pandas as pd


def net_evo_rul_ana(G,evol)->nx.Graph:
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
        # 故障节点集怎么操作，对这个集合下的所有节点操作x['EvolFailNodesSet']
            # DCGW/EOR/TOR
            # Server
            # VM
    
    
    evol.apply(rul_ana,axis=1)
    
    return G_T
    

def test():
    pass

if __name__ == '__main__':
    test()