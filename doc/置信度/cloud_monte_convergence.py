# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 19:28:45 2020

@author: zhujuxing
"""

import pandas as pd
import numpy as np
import math
# import random
from scipy import stats
import matplotlib.pyplot as plt


# from extendFuncs import extend_to_N200
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
# plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
# 

def cal_convergency(series, alpha=0.95):
    '''
    

    Parameters
    ----------
    series : 可迭代对象
        表示要统计的序列
    alpha : float, optional
        置信水平. The default is 1.96.

    Returns
    -------
    beta_upper : TYPE
        DESCRIPTION.
    beta_lower : TYPE
        DESCRIPTION.
    beta : TYPE
        DESCRIPTION.
    std : TYPE
        DESCRIPTION.
    mean_val : TYPE
        DESCRIPTION.

    '''
    t_alpha = stats.norm.interval(alpha)[1]  # 置信水平下的标准正态置信区间长度
    mean_val = np.mean(series)
    n = len(series)
    # stand_devia = np.std(series)
    # stand_devia = math.sqrt(sum(series.apply(lambda x:x**2))/n -(sum(series) / n)**2 )
    stand_devia = np.std(series, ddof=1)
    beta = (stand_devia / math.sqrt(n)) / mean_val
    if stand_devia == 0:
        beta_lower = 0
        beta_upper = 0
    else:
        beta_lower = 1 / (t_alpha + math.sqrt(n) / (stand_devia / mean_val))
        beta_upper = 1 / (-t_alpha + math.sqrt(n) / (stand_devia / mean_val))
    error = t_alpha * stand_devia / math.sqrt(n)
    return (beta_upper, beta_lower, beta, mean_val, error)


# plt.plot(x,beta)

def plot_beta(series, period, filename):
    fig = plt.figure(figsize=(5, 3))
    ax = fig.add_subplot(1, 1, 1)
    x = np.linspace(2, len(series), len(series) - 1) * (period / 365)
    y_beta = []
    y_beta_lower = []
    y_beta_upper = []

    for i in np.linspace(2, len(series), len(series) - 1, dtype=int):
        (beta_upper, beta_lower, beta, _, _) = cal_convergency(series[:i])
        y_beta.append(beta)
        y_beta_lower.append(beta_lower)
        y_beta_upper.append(beta_upper)

    plt.plot(x, y_beta, label='beta')
    plt.plot(x, y_beta_lower, label='lower bound')
    plt.plot(x, y_beta_upper, label='upper bound')
    # plt.plot(x,y_error,label = 'error')
    plt.legend()
    # plt.show()
    ax.set_yscale('log')
    ax.set_ylabel('year')
    ax.set_ylabel('beta')
    ax.set_xlim([60, 100])
    # ax.set_ylim([3.89771e-07,3.89772e-07])
    fig.savefig(filename, dpi=100)


def plot_app_beta_mean_error(avail, period=365, T=100):
    error_threshold = 0.0001  # 收敛渐进线

    avail = avail.iloc[:, :T]

    series = [avail.iloc[5], avail.iloc[10], avail.iloc[15], avail.iloc[25], avail.iloc[30]]
    x = np.linspace(2, len(series[0]), len(series[0]) - 1) * (period / 365)  # x轴数组
    y_beta = [[], [], [], [], []]
    y_mean = [[], [], [], [], []]
    y_error = [[] for i in series]
    for i in np.linspace(2, len(series[0]), len(series[0]) - 1, dtype=int):
        for j in range(5):
            (_, _, beta, mean, error) = cal_convergency(series[j][:i])
            y_beta[j].append(beta)
            y_mean[j].append(mean)
            y_error[j].append(error)

    plt.style.use('classic')

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示
    plt.rcParams['axes.unicode_minus'] = False  # 解决符号无法显示

    fig1 = plt.figure(figsize=(5, 3))
    ax1 = fig1.add_subplot(1, 1, 1)
    for i in range(5):
        plt.plot(x, y_beta[i], label=series[i].name)
    plt.legend()
    ax1.set_xlabel('仿真次数')
    ax1.set_ylabel('beta值')
    fig1.savefig('app_beta.png', dpi=100)

    fig2 = plt.figure(figsize=(5, 4))
    ax2 = fig2.add_subplot(1, 1, 1)
    for i in range(5):
        plt.plot(x, y_mean[i], label=series[i].name)
    plt.legend()
    ax2.set_xlabel('仿真次数')
    ax2.set_ylabel('可用度均值')
    fig2.savefig('app_mean.png', dpi=100)

    fig3 = plt.figure(figsize=(6, 4))
    ax3 = fig3.add_subplot(1, 1, 1)
    plt.hlines(error_threshold, 0, T, colors='r', linestyle="--")
    for i in range(5):
        plt.plot(x, y_error[i], label=series[i].name)
        # 寻找阈值下的最后一个点
        # length = len(y_error[i])
        # x_error_note = length-1
        # y_error_note = y_error[i][x_error_note]
        #
        # for j in range(length):
        #     if (y_error[i][length-(j+1)-1] > error_threshold) & (y_error[i][length-j-1] <= error_threshold):
        #         x_error_note = length-j-1
        #         y_error_note = y_error[i][x_error_note]
        #         break
        y_error_temp = pd.Series(y_error[i])
        # for j in len(y_error_temp):
        #     # if

        x_error_note = y_error_temp[y_error_temp < error_threshold].index[0]
        y_error_note = y_error_temp[y_error_temp < error_threshold].iloc[0]

        plt.annotate("%d" % x_error_note, (x_error_note, y_error_note),
                     xycoords='data',
                     xytext=(x_error_note + 20, y_error_note + (i * max(y_error[i]) / 10)),
                     arrowprops=dict(arrowstyle='->'))
    plt.legend()
    ax3.set_xlabel('仿真次数')
    ax3.set_ylabel('误差值')
    fig3.savefig('app_error.png', dpi=100)

    fig4 = plt.figure(figsize=(5, 4))
    ax4 = fig4.add_subplot(1, 1, 1)
    x = np.linspace(0, T - 1, num=T)
    for i in range(5):
        plt.plot(x, series[i], label=series[i].name)
    plt.legend()
    ax4.set_xlabel('仿真次数')
    ax4.set_ylabel('可用度')
    fig4.savefig('app.png', dpi=100)

    writer = pd.ExcelWriter('画图计算结果保存%d.xlsx' % T)
    pd.DataFrame(y_mean, index=[i.name for i in series]).to_excel(writer, sheet_name='mean')
    pd.DataFrame(y_beta, index=[i.name for i in series]).to_excel(writer, sheet_name='beta')
    pd.DataFrame(y_error, index=[i.name for i in series]).to_excel(writer, sheet_name='error')
    writer.save()


def app_convergency(filename):
    avail = pd.read_excel(filename, index_col=0)
    # result = cal_convergency(avail.iloc[0])
    tot_app = avail.apply(np.mean)
    tot_app.name = 'tot_app'
    avail = avail.append(tot_app)
    cal_result = avail.apply(cal_convergency, axis=1)

    avail.insert(len(avail.columns), 'beta', '')
    avail.insert(len(avail.columns), 'beta下界', '')
    avail.insert(len(avail.columns), 'beta上界', '')
    avail.insert(len(avail.columns), '均值', '')
    avail.insert(len(avail.columns), '误差', '')

    avail['beta'] = cal_result.apply(lambda x: x[2])
    avail['beta下界'] = cal_result.apply(lambda x: x[1])
    avail['beta上界'] = cal_result.apply(lambda x: x[0])
    avail['均值'] = cal_result.apply(lambda x: x[3])
    avail['误差'] = cal_result.apply(lambda x: x[4])
    avail.to_excel(filename, sheet_name='avail')


def plot_app_nyears(avail, period=365, T=100, Appname='App1'):
    # 表格为同一app,不同仿真时长（行）下的100次仿真
    error_threshold = 0.0001  # 收敛渐进线
    avail = avail.iloc[:, :T]
    # 选取5个app进行分析
    series = [avail.iloc[0], avail.iloc[1], avail.iloc[2], avail.iloc[3], avail.iloc[4]]
    # 样式设定
    plt.style.use('seaborn')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    x = np.linspace(2, len(series[0]), len(series[0]) - 1) * (period / 365)  # x轴数组
    # y_beta = [[],[],[],[],[]]
    # y_mean = [[],[],[],[],[]]
    y_error = [[] for i in series]
    for i in np.linspace(2, len(series[0]), len(series[0]) - 1, dtype=int):
        for j in range(5):
            (_, _, beta, mean, error) = cal_convergency(series[j][:i])
            # y_beta[j].append(beta)
            # y_mean[j].append(mean)
            y_error[j].append(error)

    fig3 = plt.figure(figsize=(6, 4))
    ax3 = fig3.add_subplot(1, 1, 1)
    plt.hlines(error_threshold, 0, T, colors='r', linestyle="--")
    for i in range(5):
        plt.plot(x, y_error[i], label=series[i].name)
        # y_error_temp = pd.Series(y_error[i])[3:]
        # x_error_note = y_error_temp[y_error_temp < error_threshold].index[0]
        # y_error_note = y_error_temp[y_error_temp < error_threshold].iloc[0]
        # plt.annotate("%d"%x_error_note, (x_error_note,y_error_note),
        #              xycoords='data',
        #              xytext=(x_error_note+20, y_error_note+(i*max(y_error[i])/10)), 
        #      arrowprops=dict(arrowstyle='->')) 
    plt.legend()
    ax3.set_xlabel('仿真次数')
    ax3.set_ylabel(f'{Appname}误差值')
    fig3.savefig('app_years_error.png', dpi=100)


def app_avail_merge(ApplicationID='App1', *filenames):
    '''
    Parameters
    ----------
    ApplicationID : 
    *filenames : 

    Returns dataframe
    -------
    合并单个app的10年，20年，……200年

    '''
    avail_line = []
    for file in filenames:
        avail_temp = pd.read_excel(file, index_col=0)
        avail_line.append(avail_temp.loc[[ApplicationID, ]])
    avail = pd.concat(avail_line, ignore_index=True)
    # ！增加曲线时需要手动修改
    avail.rename(index={0: '10年', 1: '20年', 2: '50年', 3: '100年', 4: '200年'}, inplace=True)
    return avail, ApplicationID


if __name__ == '__main__':
    # =============================================================================
    #     画方差、均值和误差图
    # =============================================================================
    avail = pd.read_excel('128server_result_(N100T100)2.xlsx', index_col=0)
    plot_app_beta_mean_error(avail, T=100)

    # 两种方式“avail=”进行单业务10年到200年的合并，手工、自动
    # avail = pd.read_excel('avai_app1_N100(T10-T200).xlsx', index_col=0)

    # 选定需要观测的App名字，同时可以增加"n年曲线"的个数(注意修改app_avail_merge函数)
    # avail, Appname = app_avail_merge('App15',
    #                         '128server_result_(N100T10).xlsx',
    #                         '128server_result_(N100T20).xlsx',
    #                         '128server_result_(N100T50).xlsx',
    #                         '128server_result_(N100T100)2.xlsx',
    #                         '128server_result_(N100T200).xlsx',)
    # plot_app_nyears(avail, period=365, T=100, Appname=Appname)

# plot_app_beta_mean(avail)
# period = 365

# b = avail.iloc[0]
# import seaborn
# import scipy.stats
# seaborn.distplot(b,kde=False,fit=scipy.stats.gamma)
# fig = plt.figure(num=1, figsize=(15, 8),dpi=80)
# #直接用plt.plot画图，第一个参数是表示横轴的序列，第二个参数是表示纵轴的序列
# plt.plot(np.arange(0,1,0.1),range(0,10,1))
# plt.plot(np.arange(0,1,0.1),range(0,20,2))
# #显示绘图结果
# plt.show()

# result = cal_convergency(avail.iloc[0])
# tot_app = avail.apply(np.mean)
# tot_app.name = 'tot_app'
# avail.append(tot_app)
# cal_result = avail.apply(cal_convergency, axis=1)

# avail.insert(len(avail.columns),'beta','')
# avail.insert(len(avail.columns),'beta下界','')
# avail.insert(len(avail.columns),'beta上界','')
# avail.insert(len(avail.columns),'均值','')

# avail['beta'] = cal_result.apply(lambda x: x[2])
# avail['beta下界'] = cal_result.apply(lambda x: x[1])
# avail['beta上界'] = cal_result.apply(lambda x: x[0])
# avail['均值'] = cal_result.apply(lambda x: x[3])
# avail.to_excel('ason网络业务可用度计算结果_周期365天_共100周期.xlsx',sheet_name='avail')

# plot_beta(avail.iloc[0],365,'app0beta.png')


# ASON_app_aval_monte = pd.read_excel('10000次1年时长业务可靠度计算结构.xlsx',encoding='UTF-8')
# ASON_app_aval_monte.set_index('Unnamed: 0',inplace=True)
# ASON_app_aval_monte = ASON_app_aval_monte.sort_index(ascending=False)

# ASON_app_aval_mean = ASON_app_aval_monte.apply(np.mean)
# ASON_app_aval_mean_list = ASON_app_aval_mean.to_list()

# N = 10000
# sigma_result = np.zeros(N)
# a_result = np.zeros(N)
# b_result = np.zeros(N)
# for i in range(N):
#     x_n = random.sample(ASON_app_aval_mean_list,i+1)
#     # x_n = ASON_app_aval_mean_list[:i]
#     sigma = np.std(x_n, ddof=1)
#     # I = sum(all_ASON_availability) / len(all_ASON_availability) #求样本均值
#     I = np.mean(x_n)
#     a = 1/(ta + math.sqrt(i)/(sigma/I))
#     b = 1/(-ta + math.sqrt(i)/(sigma/I))
#     sigma_result[i] = sigma
#     a_result[i] = a
#     b_result[i] = b
#     print(i,sigma,a,b)
#     if (1/(ta + math.sqrt(i)/(sigma/I)) <= beta) and (1/(-ta + math.sqrt(i)/(sigma/I)) >= beta):
#         print('满足仿真条件需要的仿真次数n为'+str(i))  #输出仿真年数
#         print('n的置信区间为：[' + str((sigma/I)**2 * (1/beta-ta)**2) + ',' + str((sigma/I)**2 * (1/beta+ta)**2) + ']' )
#         break

# plt.plot(sigma_result)


# x = np.array([i for i in range(N)])
# plt.plot(x,a_result,color="#F08080")
# plt.plot(x,b_result,color="#DB7093",linestyle="--")
