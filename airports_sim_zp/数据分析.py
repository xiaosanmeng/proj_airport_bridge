#%%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
from matplotlib import rcParams, gridspec, mlab

config = {
    "font.family": 'Times New Roman, SimSun', # 衬线字体
    "font.size": 12, # 相当于小四大小
    "mathtext.fontset": 'stix', # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
    'axes.unicode_minus': False # 处理负号，即-号
}

#%%
'''
处理数据
'''
Out_Table_1 = pd.read_excel(r'机务维修中心出港1月.xlsx')
Out_Table_2 = pd.read_excel(r'机务维修中心出港2月.xlsx')
Out_Table_all = pd.concat([Out_Table_1, Out_Table_2], ignore_index=True)
Out_Table_all['航班号前两位'] = [Out_Table_all.loc[m, '航班号'][0:2] for m in Out_Table_all.index]
# Out_Table_all.loc[Out_Table_all['设备名'].isna(), ['设备名']] = '残疾人升降车'
print(Out_Table_all)
Out_Table_all.to_excel(r'机务维修中心出港1-2月.xlsx', index=False)

In_Table_1 = pd.read_excel(r'机务维修中心进港1月.xlsx')
In_Table_2 = pd.read_excel(r'机务维修中心进港2月.xlsx')
In_Table_all = pd.concat([In_Table_1, In_Table_2], ignore_index=True)
In_Table_all['航班号前两位'] = [In_Table_all.loc[m, '航班号'][0:2] for m in In_Table_all.index]
# In_Table_all.loc[In_Table_all['设备名'].isna(), ['设备名']] = '残疾人升降车'
print(In_Table_all)
In_Table_all.to_excel(r'机务维修中心进港1-2月.xlsx', index=False)

#%%
'''
处理进港数据：In_Table_all
'''
In_Table_all['计达时间'] = pd.to_datetime(In_Table_all['计达时间'])
In_Table_all['实达时间'] = pd.to_datetime(In_Table_all['实达时间'])
In_Table_all['派工时间'] = pd.to_datetime(In_Table_all['派工时间'])
In_Table_all['任务确认时间'] = pd.to_datetime(In_Table_all['任务确认时间'])
In_Table_all['任务开始时间'] = pd.to_datetime(In_Table_all['任务开始时间'])
In_Table_all['任务结束时间'] = pd.to_datetime(In_Table_all['任务结束时间'])
In_Table_all['任务持续时间'] = [(In_Table_all['任务结束时间'][m]-In_Table_all['任务开始时间'][m]).total_seconds()/60 for m in In_Table_all.index]

'''
处理离港数据：In_Table_all
'''
Out_Table_all['计飞时间'] = pd.to_datetime(Out_Table_all['计飞时间'])
Out_Table_all['实飞时间'] = pd.to_datetime(Out_Table_all['实飞时间'])
Out_Table_all['派工时间'] = pd.to_datetime(Out_Table_all['派工时间'])
Out_Table_all['任务确认时间'] = pd.to_datetime(Out_Table_all['任务确认时间'])
Out_Table_all['任务开始时间'] = pd.to_datetime(Out_Table_all['任务开始时间'])
Out_Table_all['任务结束时间'] = pd.to_datetime(Out_Table_all['任务结束时间'])
Out_Table_all['任务持续时间'] = [(Out_Table_all['任务结束时间'][m]-Out_Table_all['任务开始时间'][m]).total_seconds()/60 for m in Out_Table_all.index]

#%% 1
# 进港-登机桥靠接——派工时间-实达时间-直方图
dispatchTime = []
for i in In_Table_all.index:
    if In_Table_all.loc[i, '任务名'][0:5] == '登机桥靠接':
        dispatchTime.append((In_Table_all['派工时间'][i]-In_Table_all['实达时间'][i]).total_seconds()/60)
print('登机桥靠接（进港）——派工时间-实达时间：'+str(len(dispatchTime)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')
n, bins, patches = plt.hist(dispatchTime,
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=60, range=(0, 60))
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('登机桥靠接（进港）——派工时间-实达时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\登机桥靠接（进港）——派工时间-实达时间.jpg', dpi=600)
plt.show()

#%% 2
# 离港-登机桥靠接——派工时间-实达时间-直方图
dispatchTime2 = []
for i in Out_Table_all.index:
    if Out_Table_all.loc[i, '任务名'][0:5] == '登机桥靠接':
        dispatchTime2.append((Out_Table_all['实飞时间'][i]-Out_Table_all['派工时间'][i]).total_seconds()/60)
print('登机桥靠接（离港）——实飞时间-派工时间：'+str(len(dispatchTime2)))
fig2 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax2 = fig2.add_subplot(grid[0, 0])  # 多子图时可以修改
ax2.spines['right'].set_color('none')
ax2.spines['top'].set_color('none')
n, bins, patches = plt.hist(dispatchTime2,
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=60, range=(0, 240))
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('登机桥靠接（离港）——实飞时间-派工时间')
plt.xlim(0, 240)
plt.tight_layout()
plt.savefig('picture\登机桥靠接（离港）——实飞时间-派工时间.jpg', dpi=600)
plt.show()

dispatchTime2 = []
for i in Out_Table_all.index:
    if Out_Table_all.loc[i, '任务名'][0:5] == '登机桥靠接':
        dispatchTime2.append((Out_Table_all['计飞时间'][i]-Out_Table_all['派工时间'][i]).total_seconds()/60)
print('登机桥靠接（离港）——计飞时间-派工时间：'+str(len(dispatchTime2)))
fig2 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax2 = fig2.add_subplot(grid[0, 0])  # 多子图时可以修改
ax2.spines['right'].set_color('none')
ax2.spines['top'].set_color('none')
n, bins, patches = plt.hist(dispatchTime2,
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=60, range=(0, 240))
# 绘制正态分布曲线
print(np.nanmean(dispatchTime2), np.nanstd(dispatchTime2))
normal = norm.pdf(bins, np.nanmean(dispatchTime2), np.nanstd(dispatchTime2))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(dispatchTime2,
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('登机桥靠接（离港）——计飞时间-派工时间')
plt.xlim(0, 240)
plt.tight_layout()
plt.savefig('picture\登机桥靠接（离港）——计飞时间-派工时间.jpg', dpi=600)
plt.show()

#%% 3
# 进港-登机桥靠接——任务持续时间
a = ['登机桥靠接1（进）', '登机桥靠接2（进）']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('登机桥靠接（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('登机桥靠接（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\登机桥靠接（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 4
# 离港-登机桥靠接——任务持续时间
a = ['登机桥靠接1（出）', '登机桥靠接2（出）']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('登机桥靠接（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('登机桥靠接（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\登机桥靠接（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 5
# 进港-登机桥撤离——派工时间-实达时间-直方图
dispatchTime = []
for i in In_Table_all.index:
    if In_Table_all.loc[i, '任务名'][0:5] == '登机桥撤离':
        dispatchTime.append((In_Table_all['派工时间'][i]-In_Table_all['实达时间'][i]).total_seconds()/60)
print('登机桥撤离（进港）——派工时间-实达时间：'+str(len(dispatchTime)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')
n, bins, patches = plt.hist(dispatchTime,
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=60, range=(0, 60))
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('登机桥撤离（进港）——派工时间-实达时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\登机桥撤离（进港）——派工时间-实达时间.jpg', dpi=600)
plt.show()

# 进港-登机桥撤离——任务持续时间
a = ['登机桥撤离1（进）', '登机桥撤离2（进）']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('登机桥撤离（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=60, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('登机桥撤离（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\登机桥撤离（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 6
# 离港-登机桥撤离——任务持续时间
a = ['登机桥撤离1（出）', '登机桥撤离2（出）']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('登机桥撤离（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('登机桥撤离（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\登机桥撤离（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 7
# 接电、撤电、接空、撤空
# 接电——任务持续时间
a = ['接电1(出)', '接电2(出)']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('接电（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('接电（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\接电（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

a = ['接电1(进)', '接电2(进)']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('接电（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('接电（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\接电（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 8
# 撤电——任务持续时间
a = ['撤电1(出)', '撤电2(出)']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('撤电（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('撤电（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\撤电（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

a = ['撤电1(进)', '撤电2(进)']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('撤电（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 30))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('撤电（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 30)
plt.tight_layout()
plt.savefig('picture\撤电（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 9
# 接空——任务持续时间
a = ['接空1(出)', '接空2(出)']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('撤电（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('接空（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\接空（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

a = ['接空1(进)', '接空2(进)']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('接空（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('接空（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\接空（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 10
# 撤空——任务持续时间
a = ['撤空1(出)', '撤空2(出)']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('撤空（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('撤空（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\撤空（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

a = ['撤空1(进)', '撤空2(进)']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('撤空（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 30))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('撤空（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 30)
plt.tight_layout()
plt.savefig('picture\撤空（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 11
# 一般勤务
a = ['一般勤务1（出港）', '一般勤务2（出港）']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('一般勤务（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('一般勤务（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\一般勤务（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

a = ['一般勤务1（进港）', '一般勤务2（进港）']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('一般勤务（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('一般勤务（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\一般勤务（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

#%% 12
# 中文耳机
a = ['中文耳机（出港）']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('中文耳机（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('中文耳机（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\中文耳机（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

a = ['中文耳机（进港）']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('中文耳机（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('中文耳机（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\中文耳机（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()
#%% 13
# 英文耳机
a = ['英文耳机（出港）']
Out_bridgeConnection = Out_Table_all[Out_Table_all['任务名'].isin(a)]

print('英文耳机（离港）——任务结束时间-任务开始时间：'+str(len(Out_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(Out_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 90))
# 绘制正态分布曲线
print(np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(Out_bridgeConnection['任务持续时间']), np.nanstd(Out_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(Out_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('英文耳机（离港）——任务结束时间-任务开始时间')
plt.xlim(0, 90)
plt.tight_layout()
plt.savefig('picture\英文耳机（离港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()

a = ['英文耳机（进港）']
In_bridgeConnection = In_Table_all[In_Table_all['任务名'].isin(a)]

print('英文耳机（进港）——任务结束时间-任务开始时间：'+str(len(In_bridgeConnection)))
fig1 = plt.figure()
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')

n, bins, patches = plt.hist(In_bridgeConnection['任务持续时间'],
         edgecolor = 'k',
         alpha=0.7,
         color='steelblue',
         density = True,
         bins=30, range=(0, 60))
# 绘制正态分布曲线
print(np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
normal = norm.pdf(bins, np.nanmean(In_bridgeConnection['任务持续时间']), np.nanstd(In_bridgeConnection['任务持续时间']))
line1, = plt.plot(bins, normal, 'r--', linewidth = 2, label='正态分布曲线')
# 绘制核密度曲线
sns.distplot(In_bridgeConnection['任务持续时间'],
             hist=False,
             kde=True,
             label="核密度曲线",
             kde_kws={"color": "g", 'linestyle': '--', "linewidth": 2})
plt.legend()
plt.ylabel('频率')  # 设置x，y轴的标签
plt.xlabel('英文耳机（进港）——任务结束时间-任务开始时间')
plt.xlim(0, 60)
plt.tight_layout()
plt.savefig('picture\英文耳机（进港）——任务结束时间-任务开始时间.jpg', dpi=600)
plt.show()



