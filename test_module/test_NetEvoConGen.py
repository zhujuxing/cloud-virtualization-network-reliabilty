# -*- coding: utf-8 -*-
'''
本文档用于测试演化条件生成结果。

分成4部分(代码块)：
--单构件单故障模式|
--单构件多故障模式| ->等价类划分,T取 年
--多构件多故障模式|
--T值的不同取值  

'''
# from src.NetEvoObjMod import CloudVritualizedNetwork
from src.NetEvoConGen import *
import os
import pandas as pd
import numpy as np

def test_MTBF(x,T):
    try:
        timelist = x['FailureTime'][0]
    except:
        timelist = x['FailureTime']
    timelist.append(T)
    time_end = np.array(timelist)
    time_start = timelist[:-1]
    time_start.insert(0, 0)
    time_start = np.array(time_start)
    test_MTBF_val = np.mean(time_end - time_start)
    return test_MTBF_val / 24 / 365

def test_MTBF1(x):
    try:
        timelist = x['FailureTime'][0]
        listlen = len(timelist)
    except:
        timelist = x['FailureTime']
        listlen = len(timelist)
    test_MTBF_val = T / listlen if listlen != 0 else T
    return test_MTBF_val / 24 / 365

def test_singe_componet_single_failmode_multiTimes(T,Gpath,N):
    print("---------------------开始单构件单故障模式测试---------------------")
    # --单构件单故障模式
    T, node_info = init(Gpath, T)
    MTBF_df = pd.DataFrame(columns=list(range(N)))
    node_df = node_info.loc[:, ['NodeID', 'NodeType', 'NodeFailMTBF', 'NodeFailMTTR']]
    for i in range(N):
        test_node_info = singleFR(node_info, T).loc[:, ['NodeID', 'NodeType', 'FailureTime',
                                                         'NodeFailMTBF', 'NodeFailMTTR']]
        # print(singleFR(node_info,T))
        temp = test_node_info.apply(lambda x: test_MTBF(x,T), axis=1)
        MTBF_df[i] = temp
    node_df['MTBF_CAL'] = MTBF_df.apply(np.mean, axis=1)
    print(node_df)

def test_singe_componet_single_failmode(T,Gpath):
    global node_info1, test_node_info, test_node_info1, test_MTBF, temp
    print("---------------------开始单构件单故障模式测试---------------------")
    # --单构件单故障模式
    T, node_info1 = init(Gpath, T)
    # 选取测试节点
    test_node_info = singleFR(node_info1, T).loc[0:15, ['NodeID', 'NodeType', 'FailureTime',
                                                       'NodeFailMTBF', 'NodeFailMTTR']]
    # print(test_node_info)
    test_node_info1 = test_node_info.copy(deep=True)
    test_node_info1.insert(4, 'MTBF_cal', 0)

    def test_MTBF(x):
        try:
            timelist = x['FailureTime'][0]
            listlen = len(timelist)
            print(listlen)
        except:
            timelist = x['FailureTime']
            listlen = len(timelist)
            print(str(listlen) + '*')
        # timewidth = [timelist[i+1]-timelist[i] for i in range(listlen-1)]
        test_MTBF_val = T / listlen if listlen != 0 else T
        return str(round(test_MTBF_val / 24 / 365, 1)) + '年'

    # 计算输出生成的MTBF数值，理应接近给定值（50年）
    temp = test_node_info1.apply(lambda x: test_MTBF(x), axis=1)
    test_node_info1['MTBF_cal'] = temp
    print(test_node_info1)
    return test_node_info1

def test_single_componet_multi_failmode():
    print("-------------------------开始单构件多故障模式测试--------------------------")
    # --单构件多故障模式
    global new_fail_mode, node_info2, test_node_info2, temp
    # node_info1前两项复制，加到node_info2里，用node_info2做多模式验证
    new_fail_mode = node_info1.copy(deep=True).loc[0:1, :]
    # print(new_fail_mode)
    new_fail_mode['NodeFailMTBF'] = '50年'
    new_fail_mode['NodeFailType'] = 'TF2'
    node_info2 = pd.concat([new_fail_mode, node_info1], axis=0, ignore_index=True)
    test_node_info2 = singleFR(node_info2, T).loc[0:3, ['NodeID', 'NodeType', 'FailureTime', 'RepairTime',
                                                        'NodeFailMTBF', 'NodeFailMTTR']]
    # print(test_node_info2)
    # 构件多模式合并
    test_node_info2 = common_ex(test_node_info2)
    # 计算生成的MTBF数值
    test_node_info2.insert(5, 'MTBF_mode_cal', 0)
    temp = test_node_info2.apply(lambda x: test_MTBF(x), axis=1)
    # 输出MTBF_mode_cal结果，由于D1、T1的增加了重复的故障模式，MTBF理应是单模式的一半（25年）
    test_node_info2['MTBF_mode_cal'] = temp
    print(test_node_info2)
    return test_node_info2


def test_multi_component_multi_failmode():
    print("------------开始多构件多故障模式测试-------------------")
    global T, node_info, test_node_info, test_node_info1, new_fail_mode, node_info2, test_node_info2, time_set, evol
    # %% --多构件多故障模式
    T = 100
    # node_info_show = node_info
    T, node_info = init(Gpath, T)
    # node_info_show = node_info
    test_node_info = singleFR(node_info1, T).loc[0:3, ['NodeID', 'NodeType', 'FailureTime',
                                                       'NodeFailMTBF', 'NodeFailMTTR']]
    test_node_info1 = test_node_info.copy(deep=True)
    new_fail_mode = node_info1.copy(deep=True).loc[0:1, :]
    # print(new_fail_mode)
    new_fail_mode['NodeFailMTBF'] = '50年'
    new_fail_mode['NodeFailType'] = 'TF2'
    node_info2 = pd.concat([new_fail_mode, node_info1], axis=0, ignore_index=True)
    test_node_info2 = singleFR(node_info2, T).loc[0:3, ['NodeID', 'NodeType', 'FailureTime', 'RepairTime',
                                                        'NodeFailMTBF', 'NodeFailMTTR']]
    test_node_info2 = common_ex(test_node_info2)
    time_set = time_set_gen(test_node_info2)
    # evol = Con_gen()
    evol = Con_gen(test_node_info2, T, time_set)
    evol = formating_data(evol)
    print(evol)
    return evol


def test_different_T():
    print("-----------------------开始不同周期生成故障模式测试----------------------")
    global T, node_info, test_node_info, test_node_info1, new_fail_mode, node_info2, test_node_info2, time_set, evol
    # %% --T值的不同取值
    for i in range(100, 1000):
        T = i
        T, node_info = init(Gpath, T)
        # node_info_show = node_info
        test_node_info = singleFR(node_info1, T).loc[0:3, ['NodeID', 'NodeType', 'FailureTime',
                                                           'NodeFailMTBF', 'NodeFailMTTR']]
        test_node_info1 = test_node_info.copy(deep=True)
        new_fail_mode = node_info1.copy(deep=True).loc[0:1, :]
        # print(new_fail_mode)
        new_fail_mode['NodeFailMTBF'] = '50年'
        new_fail_mode['NodeFailType'] = 'TF2'
        node_info2 = pd.concat([new_fail_mode, node_info1], axis=0, ignore_index=True)

        test_node_info2 = singleFR(node_info2, T).loc[0:3, ['NodeID', 'NodeType', 'FailureTime', 'RepairTime',
                                                            'NodeFailMTBF', 'NodeFailMTTR']]

        test_node_info2 = common_ex(test_node_info2)
        time_set = time_set_gen(test_node_info2)
        # evol = Con_gen()
        evol = Con_gen(test_node_info2, T, time_set)
        evol = formating_data(evol)
        print(evol)
    return evol

if __name__ == '__main__':
    T = 1000
    Gpath = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'g.gpickle'

    # test_singe_componet_single_failmode(T,Gpath)
    # test_single_componet_multi_failmode()
    # test_multi_component_multi_failmode()
    # test_different_T()
    test_singe_componet_single_failmode_multiTimes(T, Gpath, 100)

