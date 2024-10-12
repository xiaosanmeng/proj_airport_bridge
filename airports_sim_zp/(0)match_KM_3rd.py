'''
使用KM算法对车辆和IC卡数据匹配
添加一个时间判断：
'''
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False
from copy import deepcopy

def find_path(graph, i, visited_left, visited_right, slack_right, num, pos, label_left, label_right,S, T):
    visited_left[i] = True
    for j, match_weight in enumerate(graph[i]):
        if visited_right[j]:
            continue
        gap = label_left[i] + label_right[j] - match_weight
        if gap == 0:
            visited_right[j] = True
            if j not in T or find_path(graph, T[j], visited_left, visited_right, slack_right, num, pos, label_left, label_right,S, T):
                T[j] = i
                if type(pos[j])==type([1]):
                    S[num[i]] = pos[j]
                else:
                    S[num[i]] = [pos[j]]
                print(num[i],pos[j])
                return True
        else:
            slack_right[j] = min(slack_right[j], gap)
    return False

def KM(graph, num0, pos0):
    S, T = {}, {}
    label_left, label_right = [max(g) for g in graph], [0 for _ in graph]
    num = num0
    pos = pos0
    m = len(graph)
    for i in range(m):
        # 重置辅助变量
        slack_right = [float('inf') for _ in range(m)]
        while True:
            visited_left = [False for _ in graph]
            visited_right = [False for _ in graph]
            if find_path(graph, i, visited_left, visited_right, slack_right, num, pos, label_left, label_right, S, T):
                break
            d = float('inf')
            for j, slack in enumerate(slack_right):
                if not visited_right[j] and slack < d:
                    d = slack
            for k in range(m):
                if visited_left[k]:
                    label_left[k] -= d
                if visited_right[k]:
                    label_right[k] += d
    return S

# 计算一天的总的匹配率
def get_match_rate_day(graph, result_day, num0, pos):
    rate=0
    x=0
    for i in range(len(num0)):
        match_pos=result_day[num0[i]]
        if len(match_pos)==1:
            index = pos.index(match_pos[0])
        else:
            index = pos.index(match_pos)
        match_rate = graph[i][index]
        if match_rate > 0:
            rate = rate+match_rate
            x=x+1

    match_rate_day = rate/x

    return match_rate_day

a = -float('inf')
# 读取pos机数据
POS1 = pd.read_excel(r"E:\AnHong\code\data\pos.xlsx")  # 车载pos机数据
POS2 = pd.read_excel(r"E:\AnHong\code\data\pos2.xlsx")  # 手持pos机数据
# 读取和处理路单数据
way_bill = pd.read_csv(r"E:\AnHong\code\data\way_bill\way_bill.csv", encoding='gbk')
way_bill=way_bill[way_bill['线路名']=='安虹线']
way_bill.drop(way_bill.columns[[1,4,6,8,9,10,11,12,16,18,19,20]], axis=1, inplace=True)
way_bill=way_bill.dropna(axis=0, how='any')
way_bill.reset_index(drop=True, inplace=True)

# 筛选掉停车场的数据
drop=[]
for i in way_bill.index:
    if '停车场' in way_bill['起点'][i] or '停车场' in way_bill['终点'][i]:
        drop.append(i)
way_bill.drop(index=drop, inplace=True)
way_bill.reset_index(drop=True, inplace=True)

nums=[]
poses1=[]
for i in range(len(way_bill)):
    num=way_bill['车号'][i][:-10]
    nums.append(num)
    x1 = POS1[POS1['自编号'] == num]
    x1.reset_index(drop=True, inplace=True)
    pos1 = x1['车载POS机号'][0]
    poses1.append(pos1)
way_bill['num']=nums
way_bill['车载pos机']=poses1

# ic卡数据不包括2021年9月13号的数据
IC=pd.read_csv('E:/AnHong/code/data_output/csv/IC/IC.csv')
IC['business_date'] = pd.to_datetime(IC['business_date'])

# 删除车载pos机的IC卡数据
drop=[]
for i in IC.index:
    if IC['pos_no'][i] > 11700000:
        drop.append(i)
IC.drop(index=drop, inplace=True)
IC.reset_index(drop=True, inplace=True)

match_num_pos=pd.DataFrame(columns=['num'])
num = list(set(way_bill['num']))
num.sort()
match_num_pos['num'] = num
result_all = {}  # 记录所有的匹配结果
match_rate_all={}  # 记录匹配率

# pos机大于车辆的情况：6，8，15，20，24，25，26，27，28
# pos机小于车辆的情况：1，10，14，18，23
for i in range(1,31):
# for i in range(24, 25):
    if i == 13:
        continue
    way_bill_day=way_bill[way_bill['日']==i]  # 这一天的公交时刻表
    way_bill_day.reset_index(drop=True, inplace=True)
    num0 = list(set(way_bill_day['num']))
    num0.sort()
    IC_month = IC[IC['month'] == 9]
    IC_day = IC_month[IC_month['day'] == i]
    IC_day.reset_index(drop=True, inplace=True)  # 这一天的IC卡数据
    pos = list(set(IC_day['pos_no']))
    pos = [int(pos[i]) for i in range(len(pos))]
    pos.sort()  # pos为pos机号的列表
    print('9月', i, '日：有', len(num0), '辆车运营过，有', len(pos), '个手持pos机使用过。')
    x = len(num0)

    # 对班次少的车辆进行班次拼接
    splicing=[]
    remove=[]
    num1 = num0
    for j in num1:
        way_bill_num = way_bill_day[way_bill_day['num'] == j]
        way_bill_num.reset_index(drop=True, inplace=True)
        if 0<len(way_bill_num)<8:
            splicing.append(j)
            remove.append(j)
        if len(way_bill_num)==0:
            remove.append(j)
    for j in remove:
        num1.remove(j)
    print(splicing,'需要进行班次拼接')

    # if len(splicing)==2:
    #     # 如果只有两辆车需要拼接，则拼接
    #     num1.append(splicing[0]+','+splicing[1])
    #     print('进行一次拼接')
    # elif len(splicing)>2:
    if len(splicing)>0:
        # 如果有车辆需要拼接
        while len(splicing)>=2:
            # print('有超过两辆车需要拼接')
            way_bill_num_0 = way_bill_day[way_bill_day['num'] == splicing[0]]
            way_bill_num_0.reset_index(drop=True, inplace=True)
            for j in range(1,len(splicing)):
                way_bill_num_1 = way_bill_day[way_bill_day['num'] == splicing[j]]
                way_bill_num_1.reset_index(drop=True, inplace=True)
                # 首先要判断班次数量是否符合要求
                if 6<=len(way_bill_num_0)+len(way_bill_num_1)<=8:
                    # 其次判断班次时间是否符合要求，即时间上不能有重合
                    way_bill_num_splicing=way_bill_num_0
                    way_bill_num_splicing=pd.concat([way_bill_num_splicing, way_bill_num_1], axis=0, ignore_index=True)
                    # 按照时间升序排序
                    way_bill_num_splicing.sort_values(by="实发", inplace=True, ascending=True, ignore_index=True)
                    # print(way_bill_num_splicing)
                    t=True
                    for k in range(len(way_bill_num_splicing)-1):
                        end_time = pd.to_datetime(
                            str(way_bill_num_splicing['年'][k]) + '-' + str(way_bill_num_splicing['月'][k]) + '-' + str(
                                way_bill_num_splicing['日'][k]) + ' ' + str(way_bill_num_splicing['实到'][k]) + ':00',
                            format='%Y-%m-%d %H:%M:%S')
                        start_time = pd.to_datetime(
                            str(way_bill_num_splicing['年'][k+1]) + '-' + str(way_bill_num_splicing['月'][k+1]) + '-' + str(
                                way_bill_num_splicing['日'][k+1]) + ' ' + str(way_bill_num_splicing['实发'][k+1]) + ':00',
                            format='%Y-%m-%d %H:%M:%S')
                        if end_time > start_time:
                            # 如果有时间重合
                            t = False
                            # print(end_time,start_time)
                            break
                    if t:
                        s=splicing[0]+','+splicing[j]
                        num1.append(s)
                        splicing.remove(splicing[j])
                        splicing.remove(splicing[0])
                        print('进行一次拼接')
                        break
                    # 如果所有车辆拼接后都不符合时间要求，则该车辆不需要拼接
                    if j == len(splicing) - 1:
                        s = splicing[0]
                        num1.append(s)
                        splicing.remove(s)
                        print('班次时间要求不符合，该车不需要拼接')
                        break
                else:
                    # 如果所有车辆班次拼接后都不符合数量要求，则该车辆不需要拼接
                    if j==len(splicing)-1:
                        s=splicing[0]
                        num1.append(s)
                        splicing.remove(s)
                        print('班次数量要求不符合，该车不需要拼接')
                        break

        # 拼接之后，最后只剩一辆车
        if len(splicing)==1:
            s = splicing[0]
            num1.append(s)
            print('最后剩一辆车，该车不需要拼接')

    print('拼接后的车辆数：',len(num1))
    print(num1)

    pos_len = []
    for j in pos:
        IC_pos = IC_day[IC_day['pos_no'] == j]
        IC_pos.reset_index(drop=True, inplace=True)  # 这一天的IC卡数据
        if len(IC_pos) < 50 and \
            (IC_pos['business_date'][len(IC_pos) - 1]-IC_pos['business_date'][0]).total_seconds()>3*3600:
            # 如果一个pos机的数据量较少，同时它收集的刷卡数据的时间跨度又很大、
            # 将这种pos机的数据作为异常数据删除掉，因为它会对整体的匹配造成不好的影响
            print(IC_pos['pos_no'][0], '包括', len(IC_pos), '条IC卡数据；数据少且时间跨度大，作为异常数据删除。')
            pos.remove(IC_pos['pos_no'][0])
        elif len(IC_pos) < 10:
            # 如果一个pos机的数据量非常少
            # 将这种pos机的数据作为异常数据删除掉，因为它会对整体的匹配造成不好的影响
            print(IC_pos['pos_no'][0], '包括', len(IC_pos), '条IC卡数据；数据非常少，作为异常数据删除。')
            pos.remove(IC_pos['pos_no'][0])
        else:
            pos_len.append(len(IC_pos))
            print(IC_pos['pos_no'][0], '包括', len(IC_pos), '条IC卡数据；')


    # 添加虚拟车辆
    num0_new = deepcopy(num1)
    surplus = len(pos) - len(num1)
    if surplus>0:
        for j in range(surplus):
            num0_new.append(str(j))

    pos_new = deepcopy(pos)
    # 对每一辆车找一个匹配率最好的手持pos机
    match_rate0 = []  # 记录每个车辆的每个pos机的匹配率
    for j in num0_new:
        if len(j) > 10:
            s = j.split(',')
            way_bill_num0 = way_bill_day[way_bill_day['num'] == s[0]]
            way_bill_num0.reset_index(drop=True, inplace=True)
            way_bill_num1 = way_bill_day[way_bill_day['num'] == s[1]]
            way_bill_num1.reset_index(drop=True, inplace=True)
            way_bill_num = way_bill_num0
            way_bill_num = pd.concat([way_bill_num, way_bill_num1], axis=0, ignore_index=True)
            # 按照时间升序排序
            way_bill_num.sort_values(by="实发", inplace=True, ascending=True, ignore_index=True)
        else:
            way_bill_num = way_bill_day[way_bill_day['num'] == j]
            way_bill_num.reset_index(drop=True, inplace=True)

        if len(way_bill_num) > 0:
            m = len(way_bill_num) - 1
            # 最早的发车时间
            start_time = pd.to_datetime(
                str(way_bill_num['年'][0]) + '-' + str(way_bill_num['月'][0]) + '-' + str(
                    way_bill_num['日'][0]) + ' ' + str(way_bill_num['实发'][0]) + ':00',
                format='%Y-%m-%d %H:%M:%S')
            # 最晚的到车时间
            end_time = pd.to_datetime(
                str(way_bill_num['年'][m]) + '-' + str(way_bill_num['月'][m]) + '-' + str(
                    way_bill_num['日'][m]) + ' ' + str(way_bill_num['实到'][m]) + ':00',
                format='%Y-%m-%d %H:%M:%S')
            # 遍历这一天所有的手持pos机的数据，筛选出一个与当前车辆时刻表匹配度最高的手持pos机
            match_rate = []  # 记录每个pos机的匹配率
            for k in pos_new:
                IC_pos = IC_day[IC_day['pos_no'] == k]
                IC_pos.reset_index(drop=True, inplace=True)
                match = []  # 记录有多少IC卡数据在时刻表范围内

                if ((start_time - IC_pos['business_date'][0]).total_seconds() > 600 or
                    (start_time - IC_pos['business_date'][0]).total_seconds() < -1800) or \
                        ((IC_pos['business_date'][len(IC_pos) - 1] - end_time).total_seconds() > 600):
                    match_rate.append(0)
                    # print((IC_pos['business_date'][0] - start_time).total_seconds())
                else:
                    # 判断每一个IC刷卡数据
                    for l in IC_pos.index:
                        for n in way_bill_num.index:
                            timeo = pd.to_datetime(
                                str(way_bill_num['年'][n]) + '-' + str(way_bill_num['月'][n]) + '-' + str(
                                    way_bill_num['日'][n]) + ' ' + str(way_bill_num['实发'][n]) + ':00',
                                format='%Y-%m-%d %H:%M:%S')
                            timed = pd.to_datetime(
                                str(way_bill_num['年'][n]) + '-' + str(way_bill_num['月'][n]) + '-' + str(
                                    way_bill_num['日'][n]) + ' ' + str(way_bill_num['实到'][n]) + ':00',
                                format='%Y-%m-%d %H:%M:%S')
                            if timeo < IC_pos['business_date'][l] < timed:
                                match.append(1)
                            else:
                                match.append(0)
                    # 计算匹配率
                    if round(float(sum(match)) / len(IC_pos), 3) > 0.5:
                        match_rate.append(round(float(sum(match)) / len(IC_pos), 3))
                    else:
                        match_rate.append(0)

            if len(num0_new) > len(pos_new):
                # 添加空pos机，所有车辆对其的匹配率都为0
                for t in range(len(num0_new) - len(pos_new)):
                    match_rate.append(0)

            match_rate0.append(match_rate)
            print('车辆自编号：', j, '；匹配率最高的pos机：', pos_new[match_rate.index(max(match_rate))], '；匹配率：', max(match_rate))
        else:
            match_rate = []  # 记录每个pos机的匹配率
            # 所有pos机对于虚拟车辆的匹配率为-1
            for k in range(len(pos)):
                match_rate.append(-1)
            match_rate0.append(match_rate)

    graph = match_rate0
    result_day = KM(graph, num0_new, pos_new)  # 使用KM算法进行匹配
    # R0 = pd.DataFrame(result_day)
    # print(R0)

    # 对多余的pos机进行匹配：计算匹配率，进行匹配
    if surplus > 0:
        match_rate_day1 = get_match_rate_day(graph, result_day, num0_new, pos_new) * x
        pos_surplus=[]
        for j in range(surplus):
            pos_surplus.append(result_day[str(j)][0])
            result_day.pop(str(j))
        print('多余的pos机：',pos_surplus)

        # 对每一辆车找一个匹配率最好的手持pos机
        for j in pos_surplus:
            IC_pos = IC_day[IC_day['pos_no'] == j]
            IC_pos.reset_index(drop=True, inplace=True)
            # print(IC_pos)
            match_rate0 = []  # 记录pos机的每个车辆的匹配率

            for k in num0_new:
                way_bill_num = way_bill_day[way_bill_day['num'] == k]
                way_bill_num.reset_index(drop=True, inplace=True)

                match = []  # 记录有多少IC卡数据在时刻表范围内
                if len(way_bill_num) > 0:
                    IC_pos_now = IC_day[IC_day['pos_no'] == result_day[k][0]]
                    IC_pos_now.reset_index(drop=True, inplace=True)

                    if IC_pos['business_date'][len(IC_pos) - 1] < IC_pos_now['business_date'][0] or \
                            IC_pos['business_date'][0] > IC_pos_now['business_date'][len(IC_pos_now) - 1]:
                        # 判断每一个IC刷卡数据
                        for l in IC_pos.index:
                            for n in way_bill_num.index:
                                timeo = pd.to_datetime(
                                    str(way_bill_num['年'][n]) + '-' + str(way_bill_num['月'][n]) + '-' + str(
                                        way_bill_num['日'][n]) + ' ' + str(way_bill_num['实发'][n]) + ':00',
                                    format='%Y-%m-%d %H:%M:%S')
                                timed = pd.to_datetime(
                                    str(way_bill_num['年'][n]) + '-' + str(way_bill_num['月'][n]) + '-' + str(
                                        way_bill_num['日'][n]) + ' ' + str(way_bill_num['实到'][n]) + ':00',
                                    format='%Y-%m-%d %H:%M:%S')
                                if timeo < IC_pos['business_date'][l] < timed:
                                    match.append(1)
                                else:
                                    match.append(0)
                        # 计算匹配率
                        match_rate = float(sum(match)) / len(IC_pos)
                        match_rate0.append(match_rate)
                    else:
                        match_rate0.append(0)
                else:
                    match_rate0.append(-1)
            bus_num = num0_new[match_rate0.index(max(match_rate0))]  # 记录匹配率最高的车辆自编号

            print('多余的pos机：', j, '；车辆自编号：', bus_num, '；匹配率：', max(match_rate0))
            match_rate_day1 = match_rate_day1 + max(match_rate0)
            past_pos = result_day[bus_num]
            past_pos.append(j)
            result_day[bus_num] = past_pos

        # 计算匹配率
        match_rate_day = match_rate_day1 / (x + len(pos_surplus))
        print('这一天的总匹配率为：', match_rate_day)
        match_rate_all[i] = match_rate_day

        # 再将之前拼接的车辆拆分开
        result_day0 = result_day
        for key in list(result_day.keys()):
            if len(key) > 10:
                s = key.split(',')
                result_day0[s[0]] = result_day[key]
                result_day0[s[1]] = result_day[key]
                del result_day0[key]

        if i < 10:
            result_all['0' + str(i)] = result_day0
        else:
            result_all[str(i)] = result_day0
        R0 = pd.DataFrame(result_all)
        print(R0)

    else:
        match_rate_day = get_match_rate_day(graph, result_day, num0_new, pos_new)
        print('这一天的总匹配率为：', match_rate_day)
        match_rate_all[i] = match_rate_day

        #再将之前拼接的车辆拆分开
        result_day0 = result_day
        for key in list(result_day.keys()):
            if len(key) > 10:
                s = key.split(',')
                result_day0[s[0]] = result_day[key]
                result_day0[s[1]] = result_day[key]
                del result_day0[key]

        if i < 10:
            result_all['0' + str(i)] = result_day0
        else:
            result_all[str(i)] = result_day0
        R0 = pd.DataFrame(result_all)
        print(R0)

R = pd.DataFrame(result_all)
print(R)
R.to_csv('E:/AnHong/code/data_output/csv/pos_bus_match/车辆和IC卡匹配结果.csv', encoding='utf-8_sig')
M={}
M['rate']=match_rate_all
M = pd.DataFrame(M)
print(M)
M.to_csv('E:/AnHong/code/data_output/csv/pos_bus_match/车辆和IC卡匹配率.csv', encoding='utf-8_sig')