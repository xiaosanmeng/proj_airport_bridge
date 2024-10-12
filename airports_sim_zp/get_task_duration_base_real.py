import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import seaborn as sns
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from matplotlib import rcParams, gridspec
from scipy.stats import norm

import warnings
warnings.filterwarnings('ignore')

'''
处理数据
'''
In_Table = pd.read_excel('./dataset/机务维修中心进港2月.xlsx')
In_Table['航班号前两位'] = [In_Table.loc[m, '航班号'][0:2] for m in In_Table.index]
# Out_Table = pd.read_excel('./dataset/机务维修中心出港2月.xlsx')
# Out_Table['航班号前两位'] = [Out_Table.loc[m, '航班号'][0:2] for m in Out_Table.index]

'''
处理进港数据：In_Table
'''
In_Table['计达时间'] = pd.to_datetime(In_Table['计达时间'])
In_Table['实达时间'] = pd.to_datetime(In_Table['实达时间'])
In_Table['派工时间'] = pd.to_datetime(In_Table['派工时间'])
In_Table['任务确认时间'] = pd.to_datetime(In_Table['任务确认时间'])
In_Table['任务开始时间'] = pd.to_datetime(In_Table['任务开始时间'])
In_Table['任务结束时间'] = pd.to_datetime(In_Table['任务结束时间'])
In_Table['time'] = [(In_Table['任务结束时间'][m]-In_Table['任务开始时间'][m]).total_seconds()/60 for m in In_Table.index]
# '''
# 处理离港数据：Out_Table
# '''
# Out_Table['计飞时间'] = pd.to_datetime(Out_Table['计飞时间'])
# Out_Table['实飞时间'] = pd.to_datetime(Out_Table['实飞时间'])
# Out_Table['派工时间'] = pd.to_datetime(Out_Table['派工时间'])
# Out_Table['任务确认时间'] = pd.to_datetime(Out_Table['任务确认时间'])
# Out_Table['任务开始时间'] = pd.to_datetime(Out_Table['任务开始时间'])
# Out_Table['任务结束时间'] = pd.to_datetime(Out_Table['任务结束时间'])
# Out_Table['任务持续时间'] = [(Out_Table['任务结束时间'][m]-Out_Table['任务开始时间'][m]).total_seconds()/60 for m in Out_Table.index]

# 一般勤务
a = ['一般勤务1（进港）', '一般勤务2（进港）']
YiBanQinWu = In_Table[In_Table['任务名'].isin(a)]
# YiBanQinWu = YiBanQinWu.loc[5 < YiBanQinWu['time'] < 60]
YiBanQinWu = YiBanQinWu.drop(YiBanQinWu[(YiBanQinWu.time <5) | (YiBanQinWu.time >60)].index)

print('一般勤务（进港）——任务结束时间-任务开始时间：'+str(len(YiBanQinWu)))

DurationTime = YiBanQinWu[['time']]
mu =np.mean(DurationTime) #计算均值 
sigma =np.std(DurationTime) 
print(mu,sigma)

# 生成正态分布随机数
samples_normal = np.random.normal(mu, sigma, 10000)

# 绘制正态分布的概率密度函数图形
x_normal = np.linspace(0, 60, 500)  # x轴范围
y_normal = norm.pdf(x_normal, mu, sigma)  # 计算概率密度函数值

# 绘制直方图: 箱子数 概率密度 透明度
plt.hist(DurationTime, bins=50, density=True, alpha=0.5, label='Generated Samples')
plt.plot(x_normal, y_normal, color='red', label='Normal distribution')
plt.xlabel('x')
plt.ylabel('Probability Density')
plt.title('Normal Distribution')
plt.legend()
plt.savefig('./dataset/data_output/data_analysis_pic/2.jpg', dpi=600)
plt.show()



# # 正态分布估计
# num_bins = 30 #直方图柱子的数量 
# n, bins, patches = plt.hist(DurationTime, num_bins, facecolor='blue', alpha=0.5) 
# #直方图函数，x为x轴的值，normed=1表示为概率密度，即和为一，绿色方块，色深参数0.5.返回n个概率，直方块左边线的x值，及各个方块对象 
# y = mlab.normpdf(bins, mu, sigma) #拟合一条最佳正态分布曲线y 
# plt.plot(bins, y, 'r--') #绘制y的曲线 
# plt.xlabel('sepal-length') #绘制x轴 
# plt.ylabel('Probability') #绘制y轴 
# plt.title(r'Histogram : $\mu=5.8433$,$\sigma=0.8253$')#中文标题 u'xxx' 
# plt.subplots_adjust(left=0.15)#左边距 
# plt.savefig('./dataset/data_output/data_analysis_pic/2.jpg', dpi=600)
# plt.show()




# # 新代码
# index=list(range(1, len(YiBanQinWu)+1))
# YiBanQinWu['index'] = index
# # DurationTime = YiBanQinWu[['index', 'time']]
# DurationTime = YiBanQinWu[['time']]
# DurationTime = np.array(DurationTime)
# DurationTime=DurationTime.reshape(-1, 1)

# print(DurationTime)

# # KDE建模
# # 生成一些测试数据
# x = np.linspace(1, 60, 60)
 
# # 设置带宽参数
# bandwidth = 0.5
 
# # # 计算估计的概率密度函数
# # density_estimation = np.array([kde(xi, data, bandwidth, gaussian_kernel) for xi in x])

# model = KernelDensity(kernel='gaussian', bandwidth=bandwidth)
# model.fit(np.array(DurationTime).reshape(-1, 1))
 
# log_dens = model.score_samples(np.array(DurationTime).reshape(-1, 1))
# density_estimation = [dens for dens in np.exp(log_dens)]
# # 绘制概率密度函数图像
# plt.figure(1)
# plt.hist(DurationTime, bins=40, density=True)
# plt.plot(x, density_estimation, color='red', linestyle='-')
# plt.xlim(0, 60)
# plt.savefig('./dataset/data_output/data_analysis_pic/2.jpg', dpi=600)
# plt.show()

# 旧代码
# DurationTime = YiBanQinWu['任务持续时间']
# fig1 = plt.figure()
# grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
# ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
# ax1.spines['right'].set_color('none')
# ax1.spines['top'].set_color('none')

# n, bins, patches = plt.hist(YiBanQinWu['任务持续时间'],
#          edgecolor = 'k',
#          alpha=0.7,
#          color='steelblue',
#          density = True,
#          bins=30, range=(0, 60))

# # 绘制核密度曲线
# sns.distplot(YiBanQinWu['任务持续时间'],
#              hist=False,
#              kde=True,
#              label="核密度曲线",
#              kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
# plt.legend()
# plt.ylabel('频率')  # 设置x，y轴的标签
# plt.xlabel('一般勤务（离港）——任务结束时间-任务开始时间')
# plt.xlim(0, 60)
# plt.tight_layout()
# plt.savefig('./dataset/data_output/data_analysis_pic/1.jpg', dpi=600)
# plt.show()

