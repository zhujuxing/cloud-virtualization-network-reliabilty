# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 05:36:15 2020

@author: zhujuxing
"""

import networkx as nx
import pickle
import pandas as pd
import random
import math
import re



def init(Gpath, Tset):
    '''
    读取gpickle.Gpath表示gpickle路径，Tset表示演化时长
    '''
    global T
    T = Tset*365*24
    # gpickle转换成DataFrame
    with open(Gpath, 'rb') as fo:
        G = pickle.load(fo, encoding='bytes')
    global df, node_info, u_asp, u_chk
    df = pd.DataFrame([turple[1] for turple in G.nodes(data=True)])
    df.insert(0, 'NodeID', [turple[0] for turple in G.nodes(data=True)])
    
    node_info = df.copy(deep=True)
    node_info.insert(3, 'FailureTime', 0)
    node_info.insert(4, 'RepairTime', 0)
    
    u_asp = node_info.loc[1, 'Tasp']
    u_chk = node_info.loc[1, 'Tchk']


def convert(x):
    '''
    转换数据格式，年、min-->小时

    '''
    if isinstance(x, str):
        s = re.findall("\d+", x)[0]
        dig = int(s)
        if '年' in x:
            return 365*24*dig
        if 'min' in x:
            return dig/60
        if 's' in x:
            return dig/3600
        if 'h' in x:
            return dig
    else:
        return x


def fail_state(x):
    '''
    单个构件、单个模式生成状态
    Parameters
    ----------
    x : df行值     
    
    Returns
    -------
    fail_time : 单个构件单个模式失效列表
    reco_time : 单个构件单个模式恢复列表

    '''
    t = 0 
    fail_time = []
    reco_time = []

    fail_dt = df[df['NodeID'] == x['NodeID']]
    fail_time = [[] for i in range(len(fail_dt))]
    reco_time = [[] for i in range(len(fail_dt))]
    i = 0
    for row in fail_dt.iterrows():
        MTBF = convert(row[1]['NodeFailMTBF'])
        FDR = convert(row[1]['NodeFailFDR'])
        FDT = convert(row[1]['NodeFailFDT'])
        AFRR = convert(row[1]['NodeFailAFDR'])
        AFRT = convert(row[1]['NodeFailAFDT'])
        MTTR = convert(row[1]['NodeFailMTTR'])
        while True:
            if t>T:
                break
            else:
                delta = random.random()
                t_f  = -math.log(delta) * MTBF
                t_hr = -math.log(delta) * MTTR
                if random.random() < FDR:
                    t_r = FDT
                    if row[1]['NodeType'] == 'Server'or'DCGW'or'TOR':
                        t_r += u_asp + t_hr
                    else:
                        if random.random() < AFRR:
                            t_r += AFRT
                        else:
                            t_r += u_asp + t_hr
                            if (t_r + t) <= T:
                               fail_time[i].append(t+t_f)
                               break
                            else:
                               break
                            if (t + t_f + t_r) <= T:
                               reco_time[i].append(t + t_f + t_r)
                               t = t + t_f + t_r
                               break
                            else:
                               break
                else:
                    if row[1]['NodeType'] == 'Server'or'DCGW'or'TOR':
                       t_r = u_chk
                    else:
                       t_r = u_chk
                       if (t_r + t) <= T:
                          fail_time[i].append(t+t_f)
                          break
                       else:
                          break
                       if (t + t_f + t_r) <= T:
                          reco_time[i].append(t + t_f + t_r)
                          t = t + t_f + t_r
                          break
                       else:
                          break
                    
                if (t + t_f) <= T:
                    fail_time[i].append(t+t_f)
                else:
                    break
                if (t + t_f + t_r) <= T:
                    reco_time[i].append(t + t_f + t_r)
                else:
                    break
                t = t + t_f + t_r
        i += 1
    return fail_time, reco_time


def singleFR():
    '''
    生成单个构件单个故障
    '''
    temp = node_info.apply(fail_state, axis=1)
    
    node_info['FailureTime'] = temp.apply(lambda x: x[0]) 
    node_info['RepairTime'] = temp.apply(lambda x: x[1]) 

    global node_info1
    # 节点列属性添加失效、修复时间，属性值为[时间点列表]。
    node_info1 = node_info.copy()


def common_failure(x):
    '''
    合并单个构件所有模式的时间点。
    '''
    fail_time = []
    reco_time = []
    for i in x['FailureTime']:
        fail_time.extend(i)
    fail_time.sort()
    for i in x['RepairTime']:
        reco_time.extend(i)
    reco_time.sort()
    return fail_time, reco_time


def common_ex():
    '''
    合并单个构件时间点
    '''
    # temp不断被extend
    temp = node_info1.apply(common_failure,axis=1)
    # 拆分temp
    node_info1['FailureTime'] = temp.apply(lambda x: x[0]) 
    node_info1['RepairTime'] = temp.apply(lambda x: x[1]) 


def time_set_gen():
    '''
    生成time_set

    '''
    global time_set
    time_set = set([])
    for i in node_info1['FailureTime']: time_set = time_set | set(i)
    for i in node_info1['RepairTime']: time_set = time_set | set(i)
    time_set = [i for i in time_set]
    time_set.sort()

    print('演化态共有个%d'%len(time_set))



def Con_gen():
    '''
    生成演化态
    '''
    global evol
    t = 0
    a = node_info1['FailureTime'].to_list()
    b = node_info1['RepairTime'].to_list()
    all_fall_edge_set = []
    all_recover_edge_set = []
    while t < time_set[-1]:
        fail_time_list = [i[0] if i != [] else T for i in a]
                                                # 记录当前边状态改变(故障)的最先时间
        recover_time_list = [i[0] if i != [] else T for i in b]
                                                # 记录当前边状态改变(修复)的最先时间
        fail_time = min(fail_time_list)
        recover_time = min(recover_time_list)
        fail_node_index = fail_time_list.index(fail_time)
        recover_node_index = recover_time_list.index(recover_time)
        fail_set = []
        recover_set = []
        if fail_time < recover_time:
            fail_set.append(node_info1.loc[fail_node_index, 'NodeID'])
            t = fail_time
            a[fail_node_index] = a[fail_node_index][1:]
        elif fail_time > recover_time:
            recover_set.append(node_info1.loc[recover_node_index, 'NodeID'])
            t = recover_time
            b[recover_node_index] = b[recover_node_index][1:]
            # edges_info1.loc[recover_edge,'维修开始时间'] = edges_info1.loc[recover_edge,'维修开始时间'][1:]
        all_fall_edge_set.append(fail_set)
        all_recover_edge_set.append(recover_set)
    evol = pd.DataFrame([all_fall_edge_set,all_recover_edge_set])
    evol = evol.T
    
    EvolTime = [time_set[i+1]-time_set[i] for i in range(len(time_set)-1)]
    EvolTime.append(T-time_set[-1])
    evol.columns=['EvolFailNodesSet', 'EvolRecoNodesSet']
    evol.insert(0, 'EvolTime' ,EvolTime)
    return evol

def net_evo_con_gen(Gpath, T):
    """
    Parameters
    ----------
    Gpath : string
        演化对象数据gpickle路径，如'g.gpickle',
    T : TYPE
        演化周期，单位年

    Returns
    -------
    evol : TYPE
        DESCRIPTION.

    """
    init(Gpath, T)
    singleFR()
    common_ex()
    time_set_gen()
    evol = Con_gen()
    return evol

if __name__ == '__main__':
    # 仿真时间100年，单位小时
    T = 100
    Gpath = 'g.gpickle'
    
    print(net_evo_con_gen(Gpath, T))
    evol.to_excel('evol.xls')
