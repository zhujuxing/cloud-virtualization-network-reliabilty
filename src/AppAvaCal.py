# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:37:33 2020

@author: zhujuxing
"""

# import networkx as nx
import pandas as pd
import numpy as np
import NetEvoObjMod
import NetEvoConGen
import NetEvoRulAna
import os
import time
import copy

def app_ava_cal(file,T,N):
    """
    该函数为业务可用度计算主函数。

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
    

    single_app_avail = pd.DataFrame(columns=[i+1 for i in range(N)])
    whole_app_avail = 0.0
    g = NetEvoObjMod.CloudVritualizedNetwork(file)

    for i in range(N):
        g_T = copy.deepcopy(g) #这里之前用的是copy.copy浅拷贝，导致后续修改g_T的时候使得g里的数据也发生了变动
        evol = NetEvoConGen.net_evo_con_gen(g_T, T)
        g_T= NetEvoRulAna.net_evo_rul_ana_test(g_T,evol) # 修改net_evo_rul_ana_test为正式版函数名
        single_app_avail[i+1] = g_T.graph['Application_info']['ApplicationDownTime'].apply(lambda x:1-(x/(T*365*24)))
        g_T.displayApp()


    single_app_avail['result'] = single_app_avail.apply(np.mean, axis=1)
    print('单业务可用度计算结果为：'+os.linesep)
    print(single_app_avail)
    
    whole_app_avail = np.mean(single_app_avail['result'].to_list())
    print('整网业务可用度计算结果为：%f' % whole_app_avail)
    #g.displayApp(g)
    # return single_app_avail, whole_app_avail
    return single_app_avail, whole_app_avail
    

def test():
    T = 100
    N = 50
    file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file.xlsx'
    return app_ava_cal(file, T, N)

if __name__ == '__main__':
    t1 = time.time()
    single_app_avail, whole_app_avail = test()
    t2 = time.time()
    print("总用时：",round(t2-t1, 3),"秒")