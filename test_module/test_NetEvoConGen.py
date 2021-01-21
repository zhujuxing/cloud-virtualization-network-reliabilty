# -*- coding: utf-8 -*-
'''
本文档用于测试演化条件生成结果。

分成4部分(代码块)：
--单构件单故障模式|
--单构件多故障模式| ->等价类划分,T取 年
--多构件多故障模式|
--T值的不同取值  

'''
from NetEvoObjMod import CloudVritualizedNetwork
from NetEvoConGen import *
import os
import pandas as pd

# 测试T取值
T = 2000
Gpath = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".")+os.sep+'test'+os.sep+'g.gpickle'

#%% --单构件单故障模式

T, node_info1 = init(Gpath, T)
test_node_info = singleFR(node_info1, T).loc[0:3, ['NodeID', 'NodeType', 'FailureTime',
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
        print(str(listlen)+'*')
    # timewidth = [timelist[i+1]-timelist[i] for i in range(listlen-1)]
    test_MTBF_val = T/listlen if listlen!=0 else T
    return str(round(test_MTBF_val/24/365, 1))+'年'

# 计算输出生成的MTBF数值，理应接近给定值（50年）
temp = test_node_info1.apply(lambda x:test_MTBF(x), axis=1)
test_node_info1['MTBF_cal'] = temp
# print(test_node_info1)

#%% --单构件多故障模式

# node_info1前两项复制，加到node_info2里，用node_info2做多模式验证
new_fail_mode = node_info1.loc[0:1, :]
# print(new_fail_mode)
new_fail_mode['NodeFailMTBF'] = '50年'
node_info2 = pd.concat([new_fail_mode, node_info1], axis=0, ignore_index=True)

test_node_info2 = singleFR(node_info2, T).loc[0:3, ['NodeID', 'NodeType', 'FailureTime', 'RepairTime',
                                                    'NodeFailMTBF', 'NodeFailMTTR']]
# print(test_node_info2)

# 构件多模式合并
test_node_info2 = common_ex(test_node_info2)

# 计算生成的MTBF数值
test_node_info2.insert(5, 'MTBF_mode_cal', 0)
temp = test_node_info2.apply(lambda x:test_MTBF(x), axis=1)

# 输出MTBF_mode_cal结果，由于D1、T1的增加了重复的故障模式，MTBF理应是单模式的一半（25年）
test_node_info2['MTBF_mode_cal'] = temp


#%% --多构件多故障模式


#%% --T值的不同取值
