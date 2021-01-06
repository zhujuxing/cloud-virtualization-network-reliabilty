# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:36:15 2020

@author: zhujuxing
"""

import networkx as nx
import pandas as pd


def net_evo_con_gen(G,T)->pd.DataFrame:
    """
    Parameters
    ----------
    G : TYPE
        演化对象数据
    T : TYPE
        演化周期

    Returns
    -------
    evol : TYPE
        DESCRIPTION.

    """
    evol = pd.DataFrame(columns=['EvolTime','EvolFailNodesSet','EvolRecoNodesSet'])
    
    return evol

def test():
    pass

if __name__ == '__main__':
    test()