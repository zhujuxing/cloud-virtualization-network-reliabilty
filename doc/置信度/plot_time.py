import pandas as pd 
import numpy as np
import math
# import random
from scipy import stats
import matplotlib.pyplot as plt


T = [10,20,50,100,200]
time1 = [1903.308, 2477.007,2933.741,3065.553, 3389.464]

N = [10,50,100]
time2 = [362.1257,1743.53,3500.041]


plt.style.use('seaborn')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
f1 = plt.figure(figsize=(5,4))
ax1 = f1.add_subplot(1,1,1)
plt.plot(T,time1)

plt.legend()
ax1.set_xlabel('仿真周期T(仿真次数为100次)')
ax1.set_ylabel('仿真时间(s)')
f1.savefig('1.png',dpi = 100)

f2 = plt.figure(figsize=(5,4))
ax2 = f2.add_subplot(1,1,1)
plt.plot(N,time2)
plt.style.use('seaborn')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.legend()

ax2.set_xlabel('仿真次数N(仿真周期为200年)')
ax2.set_ylabel('仿真时间(s)')
f2.savefig('2.png',dpi = 100)