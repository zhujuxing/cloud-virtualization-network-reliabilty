# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:37:33 2020

@author: zhujuxing
"""


import networkx as nx
import pandas as pd
import NetEvoObjMod
import NetEvoConGen
import NetEvoRulAna
import os


def app_ava_cal(file,T,N):
    """
    

    Parameters
    ----------
    file : TYPE
        DESCRIPTION.
    T : TYPE
        DESCRIPTION.
    N : TYPE
        DESCRIPTION.

    Returns
    -------
    single_app_avail : TYPE
        DESCRIPTION.
    whole_app_avail : TYPE
        DESCRIPTION.

    """
    
    
    single_app_avail = pd.DataFrame()
    whole_app_avail = 0.0
    g = NetEvoObjMod.net_evo_obj_mod(file)
    evol = NetEvoConGen.net_evo_con_gen(g,T)
    # return single_app_avail, whole_app_avail
    return evol
    

def test():
    T = 100
    N = 10
    file = os.getcwd()+os.sep+'test'+os.sep+'file.xlsx'
    return app_ava_cal(file,T,N)

if __name__ == '__main__':
    e = test()