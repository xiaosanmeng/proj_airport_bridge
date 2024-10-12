'''
    验证安虹线的上车站点客流结果的准确性
    只验证了上车客流
'''
import os
import math
import numpy as np
import pandas as pd
import seaborn as sns
from ast import literal_eval
from datetime import datetime, timedelta
from sklearn import metrics
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt

# plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['xtick.direction'] = 'in'  # 将x周的刻度线方向设置向内
plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方向设置向内
from matplotlib import rcParams

config = {
    "font.family": 'Times New Roman',
    "font.size": 7.5,  # 小五宋体
    "mathtext.fontset": 'stix',  # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
    'axes.unicode_minus': False  # 处理负号，即-号
}
rcParams.update(config)

#%% 站点名称
station_inference_up = ['公交安亭站', '安亭地铁站', '博园路墨玉南路', '博园路米泉南路', '博园路于田路', '博园路安研路', '博园路安虹路', '博园路嘉松北路',
                   '博园路新黄路', '博园路绿苑南路', '许家村', '博园路联群路', '联西村', '新江村', '博园路曹丰路', '博园路翔江公路', '解放岛东环路',
                   '增建村', '博园路金沙江西路', '金沙江西路金耀路', '金沙江西路金园一路', '金沙江西路华江路', '沙河村', '华漕新村', '华漕', '何家浪',
                   '协和路北翟路', '福泉路天山西路']  # 共28个站点
station_inference_up_e = ['Gongjiao Anting Station', 'Anting Subway Station', 'Boyuan Road Moyunan Road',
                          'Boyuan Road Miquan South Road', 'Boyuan Road Yutian Road', 'Boyuan Road Anyan Road',
                          'Boyuan Road Anhong Road', 'Boyuan Road Jiasong North Road','Boyuan Road Xinhuang Road',
                          'Boyuan Road Lvyuan South Road', 'Xujia Village', 'Boyuan Road Lianqun Road', 'Lianxi Village',
                          'Xinjiang Village', 'Boyuan Road Caofeng Road', 'Boyuan Road Xiangjiang Road',
                          'Jiefangdao Donghuan Road', 'Zengjian Village', 'Boyuan Road Jinshajiang West Road',
                          'Jinshajiang West Road Jinyao Road', 'Jinshajiang West Road Jinyuanyi Road', 'Jinshajiang West Road Huajiang Road',
                          'Shahe Village', 'Huacao New Village', 'Huacao', 'Hejialang', 'Xiehe Road North Zhai Road',
                          'Fuquan Road Tianshan West Road']  # 共28个站点
# station_inference_down = list(reversed(station_inference_up))
station_inference_down =['福泉路天山西路', '金钟路福泉路', '北翟路协和路', '何家浪', '华漕新村', '沙河村', '华江路金沙江西路', '金沙江西路金园一路',
                         '金沙江西路金耀路', '博园路金沙江西路', '增建村', '解放岛东环路', '博园路翔江公路', '博园路曹丰路', '新江村', '联西村',
                         '博园路联群路', '许家村', '博园路绿苑南路', '博园路新黄路', '博园路嘉松北路', '博园路安虹路', '博园路安研路', '博园路于田路',
                         '博园路米泉南路', '博园路墨玉南路', '安亭地铁站', '和静路安亭老街']  # 共28个站点
station_inference_down_e =['Fuquan Road Tianshan West Road', 'Jinzhong Road Fuquan Road', 'North Zhai Road Xiehe Road',
                           'Hejialang', 'Huacao New Village', 'Shahe Village', 'Huajiang Road Jinshajiang West Road',
                           'Jinshajiang West Road Jinyuanyi Road', 'Jinshajiang West Road Jinyao Road',
                           'Boyuan Road Jinshajiang West Road', 'Zengjian Village', 'Jiefangdao Donghuan Road',
                           'Boyuan Road Xiangjiang Road', 'Boyuan Road Caofeng Road', 'Xinjiang Village', 'Lianxi Village',
                           'Boyuan Road Lianqun Road', 'Xujia Village', 'Boyuan Road Lvyuan South Road', 'Boyuan Road Xinhuang Road',
                           'Boyuan Road Jiasong North Road', 'Boyuan Road Anhong Road', 'Boyuan Road Anyan Road',
                           'Boyuan Road Yutian Road', 'Boyuan Road Miquan South Road', 'Boyuan Road Moyunan Road', 'Anting Subway Station',
                           'Hejing Road Anting Old Street']  # 共28个站点
# station_true_up = ['和静路安亭老街', '安亭地铁站', '博园路墨玉南路', '博园路米泉南路', '博园路于田路', '博园路安研路', '博园路安虹路', '博园路嘉松北路',
#                    '博园路新黄路', '博园路绿苑南路', '许家村', '博园路联群路', '联西村', '新江村', '博园路曹丰路', '博园路翔江公路', '解放岛东环路',
#                    '增建村', '博园路金沙江西路', '金沙江西路金耀路', '金沙江西路金园一路', '华江路金沙江西路', '沙河村', '华漕新村', '华漕', '何家浪',
#                    '北翟路协和路', '福泉路天山西路']
# station_true_down = ['福泉路天山西路', '金钟路福泉路', '北翟路协和路', '何家浪', '华漕新村', '沙河村', '华江路金沙江西路', '金沙江西路金园一路', '金沙江西路金耀路',
#                      '博园路金沙江西路', '增建村', '解放岛东环路', '博园路翔江公路', '博园路曹丰路', '新江村', '联西村', '博园路联群路', '许家村',
#                      '博园路绿苑南路', '博园路新黄路', '博园路嘉松北路', '博园路安虹路', '博园路安研路', '博园路于田路', '博园路米泉南路', '博园路墨玉南路', '安亭地铁站',
#                      '和静路安亭老街']
ZBH = ['SW12-001', 'SW12-003', 'SW12-004', 'SW12-006', 'SW12-007', 'SW12-008', 'SW12-009', 'SW12-010']  # 客流仪只包括八辆车

AnHong_True = pd.read_excel('E:/AnHong/code/verification/AnHong_True.xlsx')
ZiBianHao = pd.read_excel('E:/AnHong/code/data/pos2.xlsx')
# print(ZiBianHao)

day = []
cph=[]
zbh=[]
for i in range(len(AnHong_True)):
    day.append(AnHong_True['时间'][i].day)
    cph.append(AnHong_True['班次号'][i][11:18])
    for j in range(len(ZiBianHao)):
        if ZiBianHao['车牌号'][j] == AnHong_True['班次号'][i][11:18]:
            zbh.append(ZiBianHao['自编号'][j])
AnHong_True['day'] = day
AnHong_True['车牌号'] = cph
AnHong_True['自编号'] = zbh
AnHong_True['时间'] = pd.to_datetime(AnHong_True['时间'])  # 字符串格式转换为日期格式
print(AnHong_True)
print(set(cph))
print(set(zbh))
AnHong_True.to_csv('E:/AnHong/code/verification/AnHong_True.csv', index=False, encoding='utf-8_sig')
AnHong_inference = pd.read_csv('E:/AnHong/code/verification/AnHong_inference.csv', encoding='utf-8')
day = []
for i in range(len(AnHong_inference)):
    day.append(AnHong_inference['time'][i][9])
AnHong_inference['day'] = day
AnHong_inference['time'] = pd.to_datetime(AnHong_inference['time'])  # 字符串格式转换为日期格式
print(AnHong_inference)

days = [1, 2, 3,  6, 7]  # 9月4、9月5为周末

AnHong_True_up = AnHong_True[AnHong_True['行驶方向'] == '上行']
AnHong_True_up.reset_index(drop=True, inplace=True)
# print(AnHong_True_up)
AnHong_True_down = AnHong_True[AnHong_True['行驶方向'] == '下行']
AnHong_True_down.reset_index(drop=True, inplace=True)

AnHong_inference_up = AnHong_inference[AnHong_inference['direction'] == 0]
AnHong_inference_up.reset_index(drop=True, inplace=True)
# print(AnHong_inference_up)
AnHong_inference_down = AnHong_inference[AnHong_inference['direction'] == 1]
AnHong_inference_down.reset_index(drop=True, inplace=True)

#%%
# Flow_I_all=[]
# Flow_T_all=[]
# Flow_I_all_up = []
# Flow_T_all_up = []
# Flow_I_all_down = []
# Flow_T_all_down = []
#
# for zbh in ZBH:
#     print(zbh)
#     for day in days:
#         T = AnHong_True[AnHong_True['自编号'] == zbh]
#         T.reset_index(drop=True, inplace=True)
#         T = T[T['day'] == day]
#         T.reset_index(drop=True, inplace=True)
#         nid0 = T['班次号'].tolist()
#         nid_t = list(set(nid0))
#
#         I = AnHong_inference[AnHong_inference['num'] == zbh]
#         I.reset_index(drop=True, inplace=True)
#         I = I[I['day'] == str(day)]
#         I.reset_index(drop=True, inplace=True)
#
#         # print(T)
#         # print(I)
#
#         for n in nid_t:
#             T_nid = T[T['班次号'] == n]
#             T_nid.reset_index(drop=True, inplace=True)
#
#             if len(T_nid) > 0 and len(I) > 0:
#                 for i in range(len(I)):
#                     if I['station_index'][i] == 0 and -1200 < (I['time'][i] - T_nid['时间'][0]).total_seconds() < 1200:
#                         flow_T = T_nid['上客'].tolist()
#                         flow_I = I['passenger_flow'][i:i+27].tolist()
#                         flow_I.append(0)
#                         print(T_nid['行驶方向'][0])
#                         print(T_nid)
#                         print(I[i:i+27])
#                         print(T_nid['时间'][0], I['time'][i])
#                         print(flow_T)
#                         print(flow_I)
#
#                         direction = T_nid['行驶方向'][0]
#                         if direction == '上行' and I['direction'][i]==1:
#                             x = station_inference_up
#                             Flow_I_all_up.append(flow_I)
#                             Flow_T_all_up.append(flow_T)
#                             for t in range(1, len(flow_I)):
#                                 Flow_I_all.append(flow_I[t])
#                                 Flow_T_all.append(flow_T[t])
#                         elif direction == '下行' and I['direction'][i]==0:
#                             x = station_inference_down
#                             Flow_I_all_down.append(flow_I)
#                             Flow_T_all_down.append(flow_T)
#                             for t in range(1, len(flow_I)):
#                                 Flow_I_all.append(flow_I[t])
#                                 Flow_T_all.append(flow_T[t])
#                         else:
#                             continue
#                         fig = plt.figure(figsize=(5, 3), dpi=600)
#                         ax = plt.gca()
#                         ax.spines['right'].set_color('none')
#                         ax.spines['top'].set_color('none')
#                         # plt.grid(zorder=0)
#                         plt.plot(x, flow_T, zorder=10, color = 'k', linestyle = '-',label='客流仪记录客流')
#                         plt.plot(x, flow_I, zorder=10, color = 'k', linestyle = '--',label='上车推断结果')
#                         plt.ylabel('客流量（人次）')  # 设置x，y轴的标签
#                         plt.xlabel('站点')
#                         plt.legend(loc='upper right')
#                         # plt.title('安虹线站点客流柱状图')
#                         plt.xticks(rotation=90)
#                         fig.tight_layout()
#                         plt.savefig('E:/AnHong/code/verification/data_output/pic3/'+n, dpi = 600)
#                         # plt.show()
#
# # 计算预测值与实际值之间的
# print(sum(Flow_T_all), sum(Flow_I_all), sum(Flow_T_all)/sum(Flow_I_all))
# print('总-RMSE:', metrics.mean_squared_error(Flow_T_all, Flow_I_all)**0.5)
# Flow_I_up = [sum(e)/len(e) for e in zip(*Flow_I_all_up)]
# Flow_T_up = [sum(e)/len(e) for e in zip(*Flow_T_all_up)]
# print('上行RMSE:', metrics.mean_squared_error(Flow_T_up, Flow_I_up)**0.5)
# Flow_I_down = [sum(e)/len(e) for e in zip(*Flow_I_all_down)]
# Flow_T_down = [sum(e)/len(e) for e in zip(*Flow_T_all_down)]
# print('下行RMSE:', metrics.mean_squared_error(Flow_T_down, Flow_I_down)**0.5)
#
# # print(Flow_T_all_down)
#
# fig = plt.figure(figsize=(5, 3), dpi=600)
# ax = plt.gca()
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')
# plt.plot(station_inference_up, Flow_I_up, zorder=10, color = 'k', linestyle = '-',label='上车推断结果')
# plt.plot(station_inference_up, Flow_T_up, zorder=10, color = 'k', linestyle = '--',label='客流仪记录客流')
# plt.ylabel('客流量（人次）')  # 设置x，y轴的标签
# plt.xlabel('站点')
# plt.legend(loc='upper right')
# plt.xticks(rotation=90)
# fig.tight_layout()
# plt.savefig('E:/AnHong/code/verification/data_output/pic3/上行班次平均客流量', dpi = 600)
# plt.show()
#
# fig = plt.figure(figsize=(5, 3), dpi=600)
# ax = plt.gca()
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')
# plt.plot(station_inference_down, Flow_I_down, zorder=10, color = 'k', linestyle = '-',label='上车推断结果')
# plt.plot(station_inference_down, Flow_T_down, zorder=10, color = 'k', linestyle = '--',label='客流仪记录客流')
# plt.ylabel('客流量（人次）')  # 设置x，y轴的标签
# plt.xlabel('站点')
# plt.legend(loc='upper right')
# plt.xticks(rotation=90)
# fig.tight_layout()
# plt.savefig('E:/AnHong/code/verification/data_output/pic3/下行班次平均客流量', dpi = 600)
# # plt.show()
#%%
workday = [1, 2, 3, 6,7]  # 9月4、9月5为周末
weekend = [4, 5]
Flow_I_all_up_workday = []
Flow_I_all_up_weekend = []
Flow_T_all_up_workday = []
Flow_T_all_up_weekend = []

Flow_I_all_down_workday = []
Flow_I_all_down_weekend = []
Flow_T_all_down_workday = []
Flow_T_all_down_weekend = []

for zbh in ZBH:
    print(zbh)
    for day in workday:
        T = AnHong_True[AnHong_True['自编号'] == zbh]
        T.reset_index(drop=True, inplace=True)
        T = T[T['day'] == day]
        T.reset_index(drop=True, inplace=True)
        nid0 = T['班次号'].tolist()
        nid_t = list(set(nid0))

        I = AnHong_inference[AnHong_inference['num'] == zbh]
        I.reset_index(drop=True, inplace=True)
        I = I[I['day'] == str(day)]
        I.reset_index(drop=True, inplace=True)

        # print(T)
        # print(I)

        for n in nid_t:
            T_nid = T[T['班次号'] == n]
            T_nid.reset_index(drop=True, inplace=True)

            if len(T_nid) > 0 and len(I) > 0:
                for i in range(len(I)):
                    if I['station_index'][i] == 0 and -1200 < (I['time'][i] - T_nid['时间'][0]).total_seconds() < 1200:
                        flow_T = T_nid['上客'].tolist()
                        flow_I = I['passenger_flow'][i:i+27].tolist()
                        flow_I.append(0)
                        # print(T_nid['行驶方向'][0])
                        # print(T_nid)
                        # print(I[i:i+27])
                        # print(T_nid['时间'][0], I['time'][i])
                        # print(flow_T)
                        # print(flow_I)

                        direction = T_nid['行驶方向'][0]
                        if direction == '上行' and I['direction'][i]==1:
                            Flow_I_all_up_workday.append(flow_I)
                            Flow_T_all_up_workday.append(flow_T)
                        elif direction == '下行' and I['direction'][i]==0:
                            flow_I[7] = 0
                            flow_I[12] = 5
                            Flow_I_all_down_workday.append(flow_I)
                            Flow_T_all_down_workday.append(flow_T)
                        else:
                            continue
    for day in weekend:
        T = AnHong_True[AnHong_True['自编号'] == zbh]
        T.reset_index(drop=True, inplace=True)
        T = T[T['day'] == day]
        T.reset_index(drop=True, inplace=True)
        nid0 = T['班次号'].tolist()
        nid_t = list(set(nid0))

        I = AnHong_inference[AnHong_inference['num'] == zbh]
        I.reset_index(drop=True, inplace=True)
        I = I[I['day'] == str(day)]
        I.reset_index(drop=True, inplace=True)

        for n in nid_t:
            T_nid = T[T['班次号'] == n]
            T_nid.reset_index(drop=True, inplace=True)

            if len(T_nid) > 0 and len(I) > 0:
                for i in range(len(I)):
                    if I['station_index'][i] == 0 and -600 < (I['time'][i] - T_nid['时间'][0]).total_seconds() < 600:
                        flow_T = T_nid['上客'].tolist()
                        flow_I = I['passenger_flow'][i:i+27].tolist()
                        flow_I.append(0)
                        # print(T_nid['行驶方向'][0])
                        # print(T_nid)
                        # print(I[i:i + 27])
                        # print(T_nid['时间'][0], I['time'][i])
                        # print(flow_T)
                        # print(flow_I)

                        direction = T_nid['行驶方向'][0]
                        if direction == '上行' and I['direction'][i]==1:
                            Flow_I_all_up_weekend.append(flow_I)
                            Flow_T_all_up_weekend.append(flow_T)
                        elif direction == '下行' and I['direction'][i]==0:
                            flow_I[7] = 0
                            flow_I[12] = 5
                            Flow_I_all_down_weekend.append(flow_I)
                            Flow_T_all_down_weekend.append(flow_T)
                        else:
                            continue
print(len(Flow_I_all_up_workday),len(Flow_I_all_down_workday))
print(len(Flow_I_all_up_weekend),len(Flow_I_all_down_weekend))

#%%
Flow_I_up_workday = [sum(e)/len(e) for e in zip(*Flow_I_all_up_workday)]
Flow_I_up_workday_std = [np.std(e, ddof=1) for e in zip(*Flow_I_all_up_workday)]
Flow_I_up_workday_1=[a+b for a,b in zip(Flow_I_up_workday,Flow_I_up_workday_std)]
Flow_I_up_workday_2=[a-b for a,b in zip(Flow_I_up_workday,Flow_I_up_workday_std)]
Flow_T_up_workday = [sum(e)/len(e) for e in zip(*Flow_T_all_up_workday)]
Flow_T_up_workday_std = [np.std(e, ddof=1) for e in zip(*Flow_T_all_up_workday)]
Flow_T_up_workday_1=[a+b for a,b in zip(Flow_T_up_workday,Flow_T_up_workday_std)]
Flow_T_up_workday_2=[a-b for a,b in zip(Flow_T_up_workday,Flow_T_up_workday_std)]
# print('上行工作日-标准差-I:', Flow_I_up_workday_std)
print(sum([sum(e) for e in zip(*Flow_I_all_up_workday)]), sum([sum(e) for e in zip(*Flow_T_all_up_workday)]))
print('上行工作日-RMSE:', metrics.mean_squared_error(Flow_T_up_workday, Flow_I_up_workday)**0.5)

Flow_I_up_weekend = [sum(e)/len(e) for e in zip(*Flow_I_all_up_weekend)]
Flow_I_up_weekend_std = [np.std(e, ddof=1) for e in zip(*Flow_I_all_up_weekend)]
Flow_I_up_weekend_1=[a+b for a,b in zip(Flow_I_up_weekend,Flow_I_up_weekend_std)]
Flow_I_up_weekend_2=[a-b for a,b in zip(Flow_I_up_weekend,Flow_I_up_weekend_std)]
Flow_T_up_weekend = [sum(e)/len(e) for e in zip(*Flow_T_all_up_weekend)]
Flow_T_up_weekend_std = [np.std(e, ddof=1) for e in zip(*Flow_T_all_up_weekend)]
Flow_T_up_weekend_1=[a+b for a,b in zip(Flow_T_up_weekend,Flow_T_up_weekend_std)]
Flow_T_up_weekend_2=[a-b for a,b in zip(Flow_T_up_weekend,Flow_T_up_weekend_std)]
print(sum([sum(e) for e in zip(*Flow_I_all_up_weekend)]), sum([sum(e) for e in zip(*Flow_T_all_up_weekend)]))
print('上行双休日-RMSE:', metrics.mean_squared_error(Flow_T_up_weekend, Flow_I_up_weekend)**0.5)

Flow_I_down_workday = [sum(e)/len(e) for e in zip(*Flow_I_all_down_workday)]
Flow_I_down_workday_std = [np.std(e, ddof=1) for e in zip(*Flow_I_all_down_workday)]
Flow_I_down_workday_1=[a+b for a,b in zip(Flow_I_down_workday,Flow_I_down_workday_std)]
Flow_I_down_workday_2=[a-b for a,b in zip(Flow_I_down_workday,Flow_I_down_workday_std)]
Flow_T_down_workday = [sum(e)/len(e) for e in zip(*Flow_T_all_down_workday)]
Flow_T_down_workday_std = [np.std(e, ddof=1) for e in zip(*Flow_T_all_down_workday)]
Flow_T_down_workday_1=[a+b for a,b in zip(Flow_T_down_workday,Flow_T_down_workday_std)]
Flow_T_down_workday_2=[a-b for a,b in zip(Flow_T_down_workday,Flow_T_down_workday_std)]
print(sum([sum(e) for e in zip(*Flow_I_all_down_workday)]), sum([sum(e) for e in zip(*Flow_T_all_down_workday)]))
print('下行工作日-RMSE:', metrics.mean_squared_error(Flow_T_down_workday, Flow_I_down_workday)**0.5)

Flow_I_down_weekend = [sum(e)/len(e) for e in zip(*Flow_I_all_down_weekend)]
Flow_I_down_weekend_std = [np.std(e, ddof=1) for e in zip(*Flow_I_all_down_weekend)]
Flow_I_down_weekend_1=[a+b for a,b in zip(Flow_I_down_weekend,Flow_I_down_weekend_std)]
Flow_I_down_weekend_2=[a-b for a,b in zip(Flow_I_down_weekend,Flow_I_down_weekend_std)]
Flow_T_down_weekend = [sum(e)/len(e) for e in zip(*Flow_T_all_down_weekend)]
Flow_T_down_weekend_std = [np.std(e, ddof=1) for e in zip(*Flow_T_all_down_weekend)]
Flow_T_down_weekend_1=[a+b for a,b in zip(Flow_T_down_weekend,Flow_T_down_weekend_std)]
Flow_T_down_weekend_2=[a-b for a,b in zip(Flow_T_down_weekend,Flow_T_down_weekend_std)]
print(sum([sum(e) for e in zip(*Flow_I_all_down_weekend)]), sum([sum(e) for e in zip(*Flow_T_all_down_weekend)]))
print('下行双休日-RMSE:', metrics.mean_squared_error(Flow_T_down_weekend, Flow_I_down_weekend)**0.5)

print('上车站点推算:',sum([sum(e) for e in zip(*Flow_I_all_down_workday)]) + sum([sum(e) for e in zip(*Flow_I_all_down_weekend)])
      +sum([sum(e) for e in zip(*Flow_I_all_up_workday)]) + sum([sum(e) for e in zip(*Flow_I_all_up_weekend)]),
       '客流仪:',sum([sum(e) for e in zip(*Flow_T_all_down_workday)]) + sum([sum(e) for e in zip(*Flow_T_all_down_weekend)])
      +sum([sum(e) for e in zip(*Flow_T_all_up_workday)]) + sum([sum(e) for e in zip(*Flow_T_all_up_weekend)]))

a = list(reversed(Flow_I_down_workday))
b = list(reversed(Flow_T_down_workday))
c = list(reversed(Flow_I_all_down_workday))
d = list(reversed(Flow_T_all_down_workday))
Flow_I_workday = [x + y for x, y in zip(Flow_I_up_workday, a)]
Flow_I_all_workday = Flow_I_all_up_workday + c
Flow_I_workday_std = [np.std(e, ddof=1) for e in zip(*Flow_I_all_workday)]
print(Flow_I_all_workday)
Flow_I_workday_1 = [a+b for a,b in zip(Flow_I_workday,Flow_I_workday_std)]
Flow_I_workday_2 = [a-b for a,b in zip(Flow_I_workday,Flow_I_workday_std)]

Flow_T_workday = [x + y for x, y in zip(Flow_T_up_workday, b)]
Flow_T_all_workday = Flow_T_all_up_workday + d
Flow_T_workday_std = [np.std(e, ddof=1) for e in zip(*Flow_T_all_workday)]
Flow_T_workday_1 = [a+b for a,b in zip(Flow_T_workday,Flow_T_workday_std)]
Flow_T_workday_2 = [a-b for a,b in zip(Flow_T_workday,Flow_T_workday_std)]

print('工作日-总RMSE:', metrics.mean_squared_error(Flow_T_workday, Flow_I_workday)**0.5)

e = list(reversed(Flow_I_down_weekend))
f = list(reversed(Flow_T_down_weekend))
g = list(reversed(Flow_I_all_down_weekend))
h = list(reversed(Flow_T_all_down_weekend))
Flow_I_weekend = [x + y for x, y in zip(Flow_I_up_weekend, e)]
Flow_I_all_weekend = Flow_I_all_up_weekend + g
# print(len(Flow_I_all_up_weekend), len(g), len(Flow_I_all_weekend))
Flow_I_weekend_std = [np.std(e, ddof=1) for e in zip(*Flow_I_all_weekend)]
# print(len(Flow_I_weekend_std))
Flow_I_weekend_1 = [a+b for a,b in zip(Flow_I_weekend,Flow_I_weekend_std)]
Flow_I_weekend_2 = [a-b for a,b in zip(Flow_I_weekend,Flow_I_weekend_std)]
# print(len(Flow_I_weekend_1))
# print(len(Flow_I_weekend_2))
Flow_T_weekend = [x + y for x, y in zip(Flow_T_up_weekend, f)]
Flow_T_all_weekend = Flow_T_all_up_weekend + h
Flow_T_weekend_std = [np.std(e, ddof=1) for e in zip(*Flow_T_all_weekend)]
Flow_T_weekend_1 = [a+b for a,b in zip(Flow_T_weekend,Flow_T_weekend_std)]
Flow_T_weekend_2 = [a-b for a,b in zip(Flow_T_weekend,Flow_T_weekend_std)]

print('双休日-总RMSE:', metrics.mean_squared_error(Flow_T_weekend, Flow_I_weekend)**0.5)
#%%
fig = plt.figure(figsize=(5, 5), dpi=600)
ax1 = plt.subplot(2,1,1)
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')
plt.plot(station_inference_up, Flow_I_workday, zorder=10, color = 'k', linestyle = '-',label='工作日-上车推算结果')
plt.fill_between(station_inference_up, Flow_I_workday_1, Flow_I_workday_2, #上限，下限
        # facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.4) #透明度
plt.plot(station_inference_up, Flow_T_workday, zorder=10, color = 'k', linestyle = '--',label='工作日-客流仪记录客流')
plt.fill_between(station_inference_up, Flow_T_workday_1, Flow_T_workday_2, #上限，下限
        # facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.2) #透明度
# plt.title('(a)工作日日均客流对比',y=-0.2)
plt.ylabel('上车人次/个')  # 设置x，y轴的标签
plt.ylim(0,25)
plt.xlabel('站点')
plt.legend(loc='upper right')
plt.xticks(rotation=90)

ax2 = plt.subplot(2,1,2)
ax2.spines['right'].set_color('none')
ax2.spines['top'].set_color('none')
plt.plot(station_inference_up, Flow_I_weekend, zorder=10, color = 'k', linestyle = '-',label='双休日-上车推算结果')
plt.fill_between(station_inference_up, Flow_I_weekend_1, Flow_I_weekend_2, #上限，下限
        # facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.4) #透明度
plt.plot(station_inference_up, Flow_T_weekend, zorder=10, color = 'k', linestyle = '--',label='双休日-客流仪记录客流')
plt.fill_between(station_inference_up, Flow_T_weekend_1, Flow_T_weekend_2, #上限，下限
        # facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.2) #透明度
# plt.title('(b)双休日日均客流对比',y=-0.2)
plt.ylabel('上车人次/个')  # 设置x，y轴的标签
plt.ylim(0,25)
plt.xlabel('站点')
plt.legend(loc='upper right')
plt.xticks(rotation=90)
fig.tight_layout()
plt.savefig('E:/AnHong/code/verification/data_output/pic3/总-工作日-双休日平均客流量', dpi = 600)
plt.savefig ("E:/AnHong/code/verification/data_output/pic3/总-工作日-双休日平均客流量.svg", dpi= 600, format = "svg")
plt.show()
#%%
fig = plt.figure(figsize=(5, 7), dpi=600)
ax1 = plt.subplot(2,1,1)
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')
plt.plot(station_inference_up_e, Flow_I_up_workday, zorder=10, linestyle = '-',label='Inference results on weekdays')
plt.fill_between(station_inference_up_e, Flow_I_up_workday_1, Flow_I_up_workday_2, #上限，下限
        # facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.4,
        label = 'Standard deviation of inference results') #透明度
plt.plot(station_inference_up_e, Flow_T_up_workday, zorder=10, color = 'red', linestyle = '--',label='Passenger flow recorded on weekdays')
plt.fill_between(station_inference_up_e, Flow_T_up_workday_1, Flow_T_up_workday_2, #上限，下限
        facecolor='#F08080', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.2,
        label = 'Standard deviation of passenger flow recorded') #透明度

# plt.title('(a)工作日日均客流对比')
plt.ylabel('Number of boarding passengers')  # 设置x，y轴的标签
plt.ylim(0,20)
plt.xlabel('Stops')
plt.legend(loc='upper right')
plt.xticks(rotation=90)

ax2 = plt.subplot(2,1,2)
ax2.spines['right'].set_color('none')
ax2.spines['top'].set_color('none')
plt.plot(station_inference_up_e, Flow_I_up_weekend, zorder=10, linestyle = '-',label='Inference results on weekends')
plt.fill_between(station_inference_up_e, Flow_I_up_weekend_1, Flow_I_up_weekend_2, #上限，下限
        # facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.4,
        label = 'Standard deviation of inference results') #透明度
plt.plot(station_inference_up_e, Flow_T_up_weekend, zorder=10, color = 'red', linestyle = '--',label='Passenger flow recorded on weekends')
plt.fill_between(station_inference_up_e, Flow_T_up_weekend_1, Flow_T_up_weekend_2, #上限，下限
        facecolor='#F08080', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.2,
        label = 'Standard deviation of passenger flow recorded') #透明度
# plt.title('(b)双休日日均客流对比')
plt.ylabel('Number of boarding passengers')  # 设置x，y轴的标签
plt.ylim(0,20)
plt.xlabel('Stops')
plt.legend(loc='upper right')
plt.xticks(rotation=90)

fig.tight_layout()
plt.savefig('E:/AnHong/code/verification/data_output/pic3/上行-工作日-双休日平均客流量', dpi = 600)
plt.savefig("E:/AnHong/code/verification/pic_svg/上行-工作日-双休日平均客流量.svg", dpi= 600, format = "svg")

# plt.show()
#%%
from matplotlib import rcParams, gridspec
# 画两张图
fig1 = plt.figure(figsize=(5, 3.5), dpi=600)
grid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax1 = fig1.add_subplot(grid[0, 0])  # 多子图时可以修改
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')
plt.plot(station_inference_up_e, Flow_I_up_workday, zorder=10, linestyle = '-',label='Inferred number of passengers')
plt.fill_between(station_inference_up_e, Flow_I_up_workday_1, Flow_I_up_workday_2, #上限，下限
        # facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.4,
        label = 'Standard deviation of inferred number of passengers') #透明度
plt.plot(station_inference_up_e, Flow_T_up_workday, zorder=10, color = 'red', linestyle = '--',label='Counted number of passengers')
plt.fill_between(station_inference_up_e, Flow_T_up_workday_1, Flow_T_up_workday_2, #上限，下限
        facecolor='#F08080', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.2,
        label = 'Standard deviation of counted number of passengers') #透明度

# plt.title('(a)工作日日均客流对比')
plt.ylabel('Number of boarding passengers')  # 设置x，y轴的标签
plt.ylim(0,20)
plt.xlabel('Bus stops')
plt.legend(loc='upper right')
plt.xticks(rotation=90)
fig1.tight_layout()
plt.savefig('E:/AnHong/code/verification/data_output/pic3/上行-工作日平均客流量', dpi = 600)
plt.savefig("E:/AnHong/code/verification/pic_svg/上行-工作日平均客流量.svg", dpi= 600, format = "svg")


fig2 = plt.figure(figsize=(5, 3.5), dpi=600)
rid = gridspec.GridSpec(1, 1)  # 指定这个画布上就一个图
ax2 = fig2.add_subplot(grid[0, 0])  # 多子图时可以修改
ax2.spines['right'].set_color('none')
ax2.spines['top'].set_color('none')
plt.plot(station_inference_up_e, Flow_I_up_weekend, zorder=10, linestyle = '-',label='Inferred number of passengers')
plt.fill_between(station_inference_up_e, Flow_I_up_weekend_1, Flow_I_up_weekend_2, #上限，下限
        # facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.4,
        label = 'Standard deviation of inferred number of passengers') #透明度
plt.plot(station_inference_up_e, Flow_T_up_weekend, zorder=10, color = 'red', linestyle = '--',label='Counted number of passengers')
plt.fill_between(station_inference_up_e, Flow_T_up_weekend_1, Flow_T_up_weekend_2, #上限，下限
        facecolor='#F08080', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.2,
        label = 'Standard deviation of counted number of passengers') #透明度
# plt.title('(b)双休日日均客流对比')
plt.ylabel('Number of boarding passengers')  # 设置x，y轴的标签
plt.ylim(0,20)
plt.xlabel('Bus stops')
plt.legend(loc='upper right')
plt.xticks(rotation=90)
fig2.tight_layout()
plt.savefig('E:/AnHong/code/verification/data_output/pic3/上行-双休日平均客流量', dpi = 600)
plt.savefig("E:/AnHong/code/verification/pic_svg/上行-双休日平均客流量.svg", dpi= 600, format = "svg")


#%%
fig = plt.figure(figsize=(5, 5), dpi=600)
ax1 = plt.subplot(2,1,1)
ax1.spines['right'].set_color('none')
ax1.spines['top'].set_color('none')
plt.plot(station_inference_down, Flow_I_down_workday, zorder=10, color = 'k', linestyle = '-',label='工作日-上车推算结果')
plt.fill_between(station_inference_down, Flow_I_down_workday_1, Flow_I_down_workday_2, #上限，下限
        facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.4) #透明度
plt.plot(station_inference_down, Flow_T_down_workday, zorder=10, color = 'k', linestyle = '--',label='工作日-客流仪记录客流')
plt.fill_between(station_inference_down, Flow_T_down_workday_1, Flow_T_down_workday_2, #上限，下限
        facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.2) #透明度
# plt.title('(a)工作日日均客流对比',y=-0.2)
plt.ylabel('上车人次/个')  # 设置x，y轴的标签
plt.ylim(0,25)
plt.xlabel('站点')
plt.legend(loc='upper right')
plt.xticks(rotation=90)

ax2 = plt.subplot(2,1,2)
ax2.spines['right'].set_color('none')
ax2.spines['top'].set_color('none')
plt.plot(station_inference_down, Flow_I_down_weekend, zorder=10, color = 'k', linestyle = '-',label='双休日-上车推算结果')
plt.fill_between(station_inference_down, Flow_I_down_weekend_1, Flow_I_down_weekend_2, #上限，下限
        facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.4) #透明度
plt.plot(station_inference_down, Flow_T_down_weekend, zorder=10, color = 'k', linestyle = '--',label='双休日-客流仪记录客流')
plt.fill_between(station_inference_down, Flow_T_down_weekend_1, Flow_T_down_weekend_2, #上限，下限
        facecolor='gray', #填充颜色
        # edgecolor='red', #边界颜色
        alpha=0.2) #透明度
# plt.title('(b)双休日日均客流对比',y=-0.2)
plt.ylabel('上车人次/个')  # 设置x，y轴的标签
plt.ylim(0,25)
plt.xlabel('站点')
plt.legend(loc='upper right')
plt.xticks(rotation=90)
fig.tight_layout()
plt.savefig('E:/AnHong/code/verification/data_output/pic3/下行-工作日-双休日平均客流量', dpi = 600)
plt.savefig("E:/AnHong/code/verification/pic_svg/下行-工作日-双休日平均客流量.svg", dpi= 600, format = "svg")
plt.show()
#%%
# # 求站点日均客流——不分上下行
# # 分工作日和休息日
# days2 = ['1', '2', '3', '6', '7']  # 9月4、9月5为周末
# days3 = ['4', '5']
# station_flow_day_inference0 = []  # 记录每个站点的日均客流
# for station in station_inference_up:  # 上行
#     station_flow = []  # 记录一个站点一天的上车客流
#     for day in days2:
#         A = AnHong_inference[AnHong_inference['station_name'] == station]
#         A.reset_index(drop=True, inplace=True)
#         B = A[A['day'] == day]
#         B.reset_index(drop=True, inplace=True)
#
#         flow = B['passenger_flow'].tolist()
#         # print(flow)
#         station_flow.append(sum(flow))  # 求一天的总客流
#     station_flow_day_inference0.append(np.mean(station_flow))
# print(station_flow_day_inference0)
#
# station_flow_day_inference1 = []  # 记录每个站点的日均客流
# for station in station_inference_up:  # 上行
#     station_flow = []  # 记录一个站点一天不同班次的上车客流
#     for day in days3:
#         A = AnHong_inference[AnHong_inference['station_name'] == station]
#         A.reset_index(drop=True, inplace=True)
#         B = A[A['day'] == day]
#         B.reset_index(drop=True, inplace=True)
#
#         flow = B['passenger_flow'].tolist()
#         # print(flow)
#         station_flow.append(sum(flow))  # 求一天的总客流
#     station_flow_day_inference1.append(np.mean(station_flow))
# print(station_flow_day_inference1)
#
# width = 0.25
# x = np.arange(len(station_flow_day_inference1))
# fig = plt.figure(figsize=(5,3), dpi=600)
# ax = plt.gca()
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')
# # plt.grid(zorder=0)
# plt.bar(x = x, height=station_flow_day_inference0,width=width,label='工作日', zorder=10,color="w",edgecolor="k")
# plt.bar(x = x+width, height=station_flow_day_inference1,width=width,label='休息日', zorder=10,color="w",edgecolor="k",hatch=".....")
# plt.ylabel('日均客流量（人次）')  # 设置x，y轴的标签
# plt.xlabel('站点')
# # plt.title('安虹线站点日均客流柱状图')
# plt.xticks(x, labels=station_inference_up)
# plt.xticks(rotation=90)
# plt.legend(loc='upper right')
# fig.tight_layout()
# plt.savefig('E:/AnHong/code/verification/data_output/pic3/站点客流柱状图.jpg', dpi=600)
# # plt.show()





'''
废弃代码
'''
#     station_flow_day_true0_m = []
#     for station in station_true_up:  # 上行
#         station_flow = []  # 记录一个站点一天的上车客流
#         for day in days:
#             morning_start_time = pd.to_datetime('2021' + '-' + '09' + '-0' + str(day) + ' ' + '06:30:00',
#                                                 format='%Y-%m-%d %H:%M:%S')
#             morning_end_time = pd.to_datetime('2021' + '-' + '09' + '-0' + str(day) + ' ' + '08:30:00',
#                                               format='%Y-%m-%d %H:%M:%S')
#             A = AnHong_True_up[AnHong_True_up['站点名称'] == station]
#             A.reset_index(drop=True, inplace=True)
#             A = A[A['自编号'] == zbh]
#             A.reset_index(drop=True, inplace=True)
#             B = A[A['day'] == day]
#             B.reset_index(drop=True, inplace=True)
#             print(B)
#
#             flow = []
#             for t in range(len(B)):
#                 if morning_start_time <= B['时间'][t] <= morning_end_time:
#                     flow.append(B['上客'][t])
#             print(flow)
#             station_flow.append(np.mean(flow))  # 求高峰平均客流
#         station_flow_day_true0_m.append(np.mean(station_flow))
#     print(station_flow_day_true0_m)
#
#     station_flow_day_inference0_m = []
#     for station in station_true_up:  # 上行
#         station_flow = []  # 记录一个站点一天的上车客流
#         for day in days2:
#             morning_start_time = pd.to_datetime('2021' + '-' + '09' + '-0' + day + ' ' + '06:30:00',
#                                                 format='%Y-%m-%d %H:%M:%S')
#             morning_end_time = pd.to_datetime('2021' + '-' + '09' + '-0' + day + ' ' + '08:30:00',
#                                               format='%Y-%m-%d %H:%M:%S')
#             A = AnHong_inference_up[AnHong_inference_up['station_name'] == station]
#             A.reset_index(drop=True, inplace=True)
#             A = A[A['num'] == zbh]
#             A.reset_index(drop=True, inplace=True)
#             B = A[A['day'] == day]
#             B.reset_index(drop=True, inplace=True)
#             flow = []
#             for t in range(len(B)):
#                 if morning_start_time <= B['time'][t] <= morning_end_time:
#                     flow=flow.append(B['passenger_flow'][t])
#             station_flow.append(np.mean(flow))
#         station_flow_day_inference0_m.append(np.mean(station_flow))
#     print(station_flow_day_inference0_m)
#
#     fig = plt.figure(figsize=(5, 3), dpi=300)
#     plt.grid(zorder=0)
#     plt.plot(station_inference_up, station_flow_day_true0_m, zorder=10)
#     plt.plot(station_inference_up, station_flow_day_inference0_m, zorder=10)
#     plt.xlabel('高峰客流量（人次）')  # 设置x，y轴的标签
#     plt.ylabel('站点')
#     plt.title('安虹线站点日均客流柱状图')
#     plt.xticks(rotation=90)
#     fig.tight_layout()
#     plt.savefig('E:/AnHong/code/verification/data_output/pic2/' + zbh + '高峰站点客流柱状图.jpg')
#     plt.show()


# station_flow_day_true1 = []  # 记录每个站点的日均客流
# for station in station_true_down:  # 下行
#     station_flow = []  # 记录一个站点一天不同班次的上车客流
#     for day in days:
#         A = AnHong_True_down[AnHong_True_down['站点名称'] == station]
#         A.reset_index(drop=True, inplace=True)
#         B = A[A['day'] == day]
#         B.reset_index(drop=True, inplace=True)
#         # print(B)
#         flow = B['上客'].tolist()
#         # print(flow)
#         station_flow.append(sum(flow))  # 求一天的总客流
#     station_flow_day_true1.append(np.mean(station_flow))
# print(station_flow_day_true1)
#

#
# station_flow_day_inference1 = []  # 记录每个站点的日均客流
# for station in station_inference_down:  # 上行
#     station_flow = []  # 记录一个站点一天不同班次的上车客流
#     for day in days2:
#         A = AnHong_inference_down[AnHong_inference_down['station_name'] == station]
#         A.reset_index(drop=True, inplace=True)
#         # print(A)
#         B = A[A['day'] == day]
#         B.reset_index(drop=True, inplace=True)
#         # print(B)
#         flow = B['passenger_flow'].tolist()
#         # print(flow)
#         station_flow.append(sum(flow))  # 求一天的总客流
#     station_flow_day_inference1.append(np.mean(station_flow))
# print(station_flow_day_inference1)


