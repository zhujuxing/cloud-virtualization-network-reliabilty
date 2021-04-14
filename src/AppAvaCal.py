# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:37:33 2020

@author: zhujuxing
"""

# import networkx as nx
import pandas as pd
import numpy as np
import src.NetEvoObjMod as NetEvoObjMod
import src.NetEvoConGen as NetEvoConGen
import src.NetEvoRulAna as NetEvoRulAna
import os
import time
import copy


def app_single_cal(file, T):
    g = NetEvoObjMod.CloudVritualizedNetwork(file)

    g_T = copy.deepcopy(g) #这里之前用的是copy.copy浅拷贝，导致后续修改g_T的时候使得g里的数据也发生了变动
    evol = NetEvoConGen.net_evo_con_gen(g_T, T)
    g_T= NetEvoRulAna.net_evo_rul_ana(g_T, evol) # 修改net_evo_rul_ana_test为正式版函数名
    result =  g_T.graph['Application_info']['ApplicationDownTime'].apply(lambda x:1-(x/(T*365*24)))
    # NetEvoRulAna.saveLog()
    NetEvoRulAna.clearVar()
    del g_T
    return result


def app_ava_cal(file, T, N):
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
    g = NetEvoObjMod.CloudVritualizedNetwork(file)

    for i in range(N):
        g_T = copy.deepcopy(g) #这里之前用的是copy.copy浅拷贝，导致后续修改g_T的时候使得g里的数据也发生了变动
        # g_T = g.copy()
        evol = NetEvoConGen.net_evo_con_gen(g_T, T)
        g_T= NetEvoRulAna.net_evo_rul_ana(g_T, evol) # 修改net_evo_rul_ana_test为正式版函数名
        single_app_avail[i+1] = g_T.graph['Application_info']['ApplicationDownTime'].apply(lambda x:1-(x/(T*365*24)))
        # g_T.displayApp()
        # NetEvoRulAna.saveLog()
        NetEvoRulAna.clearVar()
        del g_T

    single_app_avail['result'] = single_app_avail.apply(np.mean, axis=1)
    print('单业务可用度计算结果为：'+os.linesep)
    print(single_app_avail)
    
    whole_app_avail = np.mean(single_app_avail['result'].to_list())
    print('整网业务可用度计算结果为：%f' % whole_app_avail)
    #g.displayApp(g)
    # return single_app_avail, whole_app_avail
    return single_app_avail, whole_app_avail
    

def test_T():
    N = 100
    # file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file.xlsx'
    file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")\
           +os.sep+'test'+os.sep+"file_128server.xlsx"
    result = pd.DataFrame()
    for T in [10,20,50,100,200]:
        t1 = time.time()
        single_app_avail, whole_app_avail = app_ava_cal(file, T, N)
        single_app_avail.to_excel(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")\
            + os.sep+"data"+os.sep+'128server_result_(N100T%d).xlsx'%T)
        t2 = time.time()
        result_i = single_app_avail['result']
        result_i['whole'] = whole_app_avail
        result_i['time'] = t2-t1
        result[T] = result_i
        result.to_excel('T.xlsx')
    # print("总用时：",round(t2-t1, 3),"秒")
    return result

def test_N():
    T = 200
    # file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file.xlsx'
    file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")\
       +os.sep+'test'+os.sep+"file_128server - 副本.xlsx"
    result = pd.DataFrame()
    for N in [10,50,100,200,500]:
        t1 = time.time()
        single_app_avail, whole_app_avail = app_ava_cal(file, T, N)
        single_app_avail.to_excel(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")\
            + os.sep+"data"+os.sep+'128server_result_(T200N%d).xlsx'%N)
        t2 = time.time()
        result_i = single_app_avail['result']
        result_i['whole'] = whole_app_avail
        result_i['time'] = t2-t1
        result[N] = result_i
        result.to_excel("data"+os.sep+"N.xlsx")
    return result


def test_N_4():
    T = 200
    # file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'file.xlsx'
    file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")\
       +os.sep+'test'+os.sep+"file.xlsx"
    result = pd.DataFrame()
    # for N in [10,50,100,200,500]:
    for N in [10]:
        t1 = time.time()
        single_app_avail, whole_app_avail = app_ava_cal(file, T, N)
        single_app_avail.to_excel(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")\
            + os.sep+"data"+os.sep+'4server_result_(T200N%d).xlsx'%N)
        t2 = time.time()
        result_i = single_app_avail['result']
        result_i['whole'] = whole_app_avail
        result_i['time'] = t2-t1
        result[N] = result_i
        result.to_excel(os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")\
            + os.sep+"data"+os.sep+"N.xlsx")
    return result


if __name__ == '__main__':
    # result_T = test_T()
    # result_N = test_N()
    # test_N_4()
    T = 200
    file = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".") \
           +os.sep+'test'+os.sep+"file.xlsx"
    # result = app_single_cal(file, T)

    import time
    def time_it(func):
        print('-------------执行函数----------------')
        t1 = time.time()
        func()
        t2 = time.time()
        print('-------------执行结束----------------')
        print(t2-t1)

    N = 10
    # @time_it
    # def single_thread():
    #     for i in range(N):
    #         app_single_cal(file, T)
    #
    # @time_it
    # def multi_thread():
    #     import threading
    #     for i in range(N):
    #         t = threading.Thread(target=app_single_cal,args=(file, T))
    #         t.start()

    def thread_pool_m():
        import multiprocessing

        process_que = []
        for i in range(N):
            process_que.append(multiprocessing.Process(target=app_single_cal, args=(file, T)))

        for t in process_que:
            t.start()

    t1 = time.time()
    thread_pool_m()
    t2 = time.time()
    print(t2-t1)



