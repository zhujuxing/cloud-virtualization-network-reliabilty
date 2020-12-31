# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:34:57 2020

@author: zhujuxing
"""

import netwrokx as nx
import pandas as pd


def net_evo_obj_mod(file)->nx.Graph:
    """
    

    Parameters
    ----------
    file : TYPE
        DESCRIPTION.

    Returns
    -------
    G : TYPE
        G包含节点信息:G.nodes.data(),链路信息G.edges.data(),
        业务信息在G.graph里设置，分别是
        G.graph['VNF_info'] : dataframe对象
        G.graph['Service_info']
        G.graph['Application_info']

    """
    G = nx.Graph()
    pass

    return G

def test():
    pass

if __name__ == '__main__':
    test()