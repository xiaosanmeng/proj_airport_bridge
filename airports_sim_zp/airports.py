import warnings
warnings.filterwarnings("ignore")


from flights import *
from task import *
from aviation import *
from crew import *
import copy

from func_timeout import func_set_timeout, FunctionTimedOut
import time
from datetime import datetime

class operator():
    ''' 
    调度人员类抽象
    '''
    # def __init__(self) -> None:
    #     pass 

    def __init__(self):
        self.crew = Crew() # 地勤人员信息

    def match_algorithm(self, task, df_can, df_can2, df_can3):
        ''' 
        匹配算法，按照沈老师整理的过程撰写匹配逻辑
        1. 宽窄机型
        2. 进港、离港
        3. 勤务保障需求
        taskList: 任务列表
        candidate: 候选人员

        return: 匹配的人员名单
        name_task_dict 的类型是什么？

        贪心选择，空闲时间最长排序的人员，第一具有 task 的人员
        '''

        taskList = task.taskList # 保障需求列表
        taskMinNum = task.minNum # 任务最小人数

        # print(f'boundType: {task.type}, airType: {task.airtype},minNum: {taskMinNum}')

        name_task_dict = {}
        trans = ['isYiBan','isFangXing','isWeiXiu','isZhongWen','isYingWen']
        # taskList 代表的是五种任务的属性，[self.isYiBan,self.isFangXing,self.isWeiXiu,self.isZhongwen,self.isYingwen]
        for i in range(len(taskList)):
            if taskList[i] == 1:
                print(i)
                findStaff = False
                # 选择第一个具有该属性的人员
                if df_can.shape[0] != 0:
                    for index,row in df_can.iterrows():
                        if row[trans[i]] == 1 and row['name'] not in name_task_dict:
                            name_task_dict[row['name']] = trans[i]
                            taskMinNum -= 1
                            findStaff = True
                            break
                
                # 如果在1/4区域没找到人，在1/2区域找人
                if not findStaff:
                    print('No enough people, try to find the near2 people')
                    if df_can2.shape[0] != 0:
                        for index,row in df_can2.iterrows():
                            if row[trans[i]] == 1 and row['name'] not in name_task_dict:
                                name_task_dict[row['name']] = trans[i]
                                taskMinNum -= 1
                                findStaff = True
                                break
                
                # 如果在1/2区域没找到人，在全部区域找人
                if not findStaff:
                    print('No enough people, try to find the near3 people')
                    if df_can3.shape[0] != 0:
                        for index,row in df_can3.iterrows():
                            if row[trans[i]] == 1 and row['name'] not in name_task_dict:
                                name_task_dict[row['name']] = trans[i]
                                taskMinNum -= 1
                                findStaff = True
                                break
                # 如果还是找不到人
                if not findStaff:
                    taskMinNum -= 1
                    name_task_dict['虚拟人' + str(i)] = trans[i]
                
        # 如果选择的人数不满足最小人数，再补充人数
        max_loop = 0
        while taskMinNum > 0:
            # 选择 free 时间长的人
            i = 0
            for index,row in df_can.iterrows():
                # risky: 找不到空闲的人员
                if row['name'] not in name_task_dict:
                    name = row['name']
                    name_task_dict[name] = 'default'
                    # for j in range(len(taskList)):
                    #     if row[trans[j]] == 1:
                    #         name_task_dict[name].add(trans[j])
                    #         taskList[j] -= row[trans[j]]
                    taskMinNum -= 1
                    break
            max_loop += 1
            if max_loop > 10:
                return None
                # return name_task_dict
        return name_task_dict

    def find_path(self, graph, i, visited_left, visited_right, slack_right, num, pos, label_left, label_right,S, T):
        visited_left[i] = True
        for j, match_weight in enumerate(graph[i]):
            if visited_right[j]:
                continue
            gap = label_left[i] + label_right[j] - match_weight
            if gap == 0:
                visited_right[j] = True
                if j not in T or self.find_path(graph, T[j], visited_left, visited_right, slack_right, num, pos, label_left, label_right,S, T):
                    T[j] = i
                    if type(pos[j])==type([1]):
                        S[num[i]] = pos[j]
                    else:
                        S[num[i]] = [pos[j]]
                    # print(num[i],pos[j])
                    return True
            else:
                slack_right[j] = min(slack_right[j], gap)
        return False

    @func_set_timeout(1)
    def match_algorithm_KM(self, graph, num0, pos0):
        '''
        二分图匹配算法：距离优先＋空闲优先，距离一样的选择空闲时间长的
        '''
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
                if self.find_path(graph, i, visited_left, visited_right, slack_right, num, pos, label_left, label_right, S, T):
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

class airports():
    ''' 
    机场仿真过程类
    '''
    def __init__(self):
        super().__init__()
        # Fixed datatype
        self.aviationSet = ACsets()  # 航司信息
        self.flightSet = FlightsSet() # 航班信息
        self.crew = Crew() # 地勤人员信息
        self.operator = operator() # 调度算法
        self.gate_lounge = None

        self.single_total = -1 # 累计任务计数
        self.single_null = -1 # 断档任务计数

        # Dynamic datatype
        self.taskSet = TaskSet() # 任务集合

        self.margin = pd.Timedelta('15 min') # 可观察未来航班的时间间隔

        self.begin = None
        self.now = None
        self.days = 0
        self.df_task_exec = pd.DataFrame(columns=['Time',
                                                  'Lounge',
                                                  'Gate',
                                                  'Duration',
                                                  'People']) # 任务执行记录
    
    def record_process(self,gate,time,terminals,duration,name_list):
        '''
        记录每次任务和对应的人员名单
        task_list: 任务列表
        name_list: 人员名单
        '''
        print('======   Record the process   =======')
        duration = duration[0]
        if name_list:
            name_list = ''.join(list(name_list.keys()))
        # 为 df_task_exec 添加一行记录
        new_row = {'Time':time,'Gate':gate,'Lounge':terminals,'Duration':duration,'People':name_list}
        # 没有 row
        df_new_row = pd.DataFrame(new_row,index=[0])
        # 合并 df
        self.df_task_exec = pd.concat([self.df_task_exec,df_new_row],ignore_index=True)

    def record_process_KM(self, task_i, gate,time,terminals,duration,name, distance, wait_time):
        '''
        记录二分图匹配后的结果
        每次任务和对应的人员名单
        task_list: 任务列表
        name_list: 人员名单
        '''
        print('======   Record the process   =======')
        duration = duration[0]

        # 为 df_task_exec 添加一行记录
        new_row = {'Task': task_i, 'Time':time,'Gate':gate,'Lounge':terminals,'Duration':duration,'People':name, 'Distance': distance, 'WaitTime': wait_time}
        # 没有 row
        df_new_row = pd.DataFrame(new_row,index=[0])
        # 合并 df
        self.df_task_exec = pd.concat([self.df_task_exec,df_new_row],ignore_index=True)
    
    def save_result(self):
        ''' 
        保存完整运行结果
        '''
        self.df_task_exec.to_excel('../dataset/task_exec.xlsx',index=False)
        # self.flightSet.df_flights.to_excel('../dataset/flights_new.xlsx', index=False)
        self.flightSet.df_flights_left.to_excel('../dataset/flights_left.xlsx',index=False)

    def login(self,aviation_path,flights_path,crew_zizhi_path,crew_group_path,gate_lounge_path,type_minNum_path):
        '''
        注册静态数据
        aviation_path: 航司信息路径
        flights_path: 航班信息路径
        crew_zizhi_path: 人员资质证明路径
        crew_group_path: 人员组别路径
        gate_lounge_path: 休息室路径
        '''
        self.aviationSet.login(aviation_path)
        self.flightSet.login(flights_path)
        print('Flights login success,len is ',self.flightSet.df_flights.shape[0])
        # self.flightSet.filter_by_id(self.aviationSet.get_company_codingID()) # 06-15 取消航司过滤
        self.crew.login(crew_zizhi_path,crew_group_path)
        self.gate_terminal = pd.read_excel(gate_lounge_path) # ./dataset/Gate_lounge.xlsx'
        self.gate_terminal.rename(columns={'停机口':'gate',
                                           '休息室':'lounge',
                                           'X坐标':'x',
                                           'Y坐标':'y'}, inplace=True)
        self.begin = self.flightSet.get_begin_time()

        self.df_type_minNum = pd.read_excel(type_minNum_path) # 机型最小人数
        self.now = self.begin # 初始化最早时间

    def login_ADSB(self, aviation_path, flights_path, crew_zizhi_path, crew_group_path, gate_lounge_path,
                  type_minNum_path):
        '''
        注册静态数据
        aviation_path: 航司信息路径
        flights_path: 航班信息路径
        crew_zizhi_path: 人员资质证明路径
        crew_group_path: 人员组别路径
        gate_lounge_path: 休息室路径
        '''
        self.aviationSet.login(aviation_path)
        self.flightSet.login(flights_path)
        print('Flights login success,len is ', self.flightSet.df_flights.shape[0])
        # self.flightSet.filter_by_id(self.aviationSet.get_company_codingID()) # 06-15 取消航司过滤
        self.crew.login(crew_zizhi_path, crew_group_path)
        self.gate_terminal = pd.read_excel(gate_lounge_path)  # ./dataset/Gate_lounge.xlsx'
        self.gate_terminal.rename(columns={'停机口': 'gate',
                                           '休息室': 'lounge',
                                           'X坐标': 'x',
                                           'Y坐标': 'y'}, inplace=True)
        self.begin = self.flightSet.get_begin_time_ADSB()

        self.df_type_minNum = pd.read_excel(type_minNum_path)  # 机型最小人数
        self.now = self.begin  # 初始化最早时间

    def get_margin_flights(self):
        '''
        获取可观察的航班的集合
        '''
        return self.flightSet.get_near_flights(self.now,self.margin)

    def get_margin_flights_ADSB(self):
        '''
        获取可观察的航班的集合
        '''
        return self.flightSet.get_near_flights_from_ADSB(self.now)
    
    def get_minNum(self,airType,boundType,taskFlag):
        '''
        获取最小航班数,这里完全根据历史经验来的
        airType: 机型
        boundType: 进出港类型
        taskFlag: 是否有任务需求
        '''
        res = 1
        try:
            flag = self.df_type_minNum[self.df_type_minNum['机型'] == airType]['min'].values[0]
        except:
            print('No such airType or boundType')
        
        if flag == 1:
            # 说明是窄体机
            if taskFlag != 0:
                res = 2
        else:
            # 说明是宽体机
            if boundType == 'inbound':
                res = 2
            else:
                res = 3
        return res
        
    def generation_task(self,flight):
        ''' 
        从航班中生成任务,任务的时间和地点与航班一致
        '''
        newTask = self.aviationSet.create_task(flight.ac) # 1. 根据航司信息生成初始任务

        newTask.time = flight.actual_datetime  # 任务执行时刻
        newTask.lounge = self.get_lounge(flight.gate) # 任务执行休息室
        newTask.gate = flight.gate # 任务执行登机口
        newTask.type = flight.boundType # 任务类型
        newTask.airtype = flight.airType # 任务飞机类型

        newTask.minNum = self.get_minNum(flight.airType,flight.boundType,sum(newTask.taskList)) # 任务最小人数

        newTask.taskDuration = [newTask.get_task_duration_base_real() for _ in range(len(newTask.taskList))] # 任务持续时间,这部分需要做数据分析

        return newTask
    
    def get_lounge(self,gate):
        '''
        根据停机口获取休息室,根据 gate 明确对应的 terminal
        '''
        gate = int(gate)
        try:
            return self.gate_lounge[self.gate_lounge['gate'] == gate]['lounge'].values[0]
        except:
            lounges = [187,153,60,88]
            # 返回最近的休息室
            fix = [abs(gate - i) for i in lounges]
            return lounges[fix.index(min(fix))]
    
    def step(self):
        '''
        每次仿真的前进步骤s
        '''
        data = {} # 想清楚 data 需要有什么数据
        # 1. time，当前时间
        self.now += pd.Timedelta('1min') # 每分钟仿真一次
        data['time'] = self.now
        # 2. crew，人员信息
        self.crew.update_status(self.now) # 更新人员的 status 状态
        data['crew'] = self.crew.dfCrew
        # 3. task，任务信息
        flights_list = self.get_margin_flights() # 获取能够观察到的航班
        data['flights'] = flights_list

        if flights_list: 
            for flight in flights_list:
                task = self.generation_task(flight) # 根据航班信息生成任务
                self.taskSet.add_task(task) # 向任务集合中添加任务
        data['tasks'] = self.taskSet.tasks
        group = (self.now - self.begin).days % 4 + 1 # 每一天同时只有一个 Group 工作
        data['group'] = group
        name_list = None
        data['lounge'] = -1 # lounge 默认为 -1
        if self.taskSet.isnotnull():   # 这里应该是获取所有需要解决的任务列表，然后匹配所有的任务
            for task in self.taskSet:
                data['lounge'] = self.get_lounge(task.gate)
                df_can =self.crew.get_near1_people(self.get_lounge(task.gate),group) # 获取附近 1/4 的人员
                lounge = self.get_lounge(task.gate)
                name_list = self.operator.match_algorithm(task, lounge, group)
                if not name_list: # 第一次找不到人
                    print('No enough people, try to find the near2 people')
                    df_can = self.crew.get_near2_people(self.get_lounge(task.gate), group,self.now,df_can) # 第二次任务匹配
                    name_list = self.operator.match_algorithm(task,df_can)
                if not name_list:
                    # 除非没有人员，否则不会执行
                    print('No enough people, try to find the near3 people')
                    df_can = self.crew.get_near3_people(self.get_lounge(task.gate),group,df_can) # 第三次任务匹配
                    name_list = self.operator.match_algorithm(task,df_can)
    
                # 保存 namelist
                if name_list:
                    self.taskSet.tasks.remove(task)
                    self.record_process(task.gate,task.time,task.lounge,task.taskDuration,name_list)
                    self.crew._update_people_status(name_list,task,self.now)
                    self.taskSet.update_task_status(name_list,task)
                    self.single_total += 1
                else:
                    if task.isdead():
                        self.taskSet.tasks.remove(task)
                        name_list = None
                        self.single_null += 1
                        self.record_process(task.gate,task.time,task.lounge,task.taskDuration,name_list)
                task.update_status()
        data['name_list'] = name_list

        # 每增加一天
        if (self.now-self.begin).days != self.days:
            self.crew.record_single_day(str(self.now.month)+'-'+str(self.now.day))
            self.days = (self.now-self.begin).days # 更新天数
            self.single_null = -1
            self.single_total = -1

        data['single_total'] = self.single_total
        data['single_null'] = self.single_null
        return data

    def step_sim(self):
        '''
        每次仿真的前进步骤s
        '''
        data = {} # 想清楚 data 需要有什么数据
        # 1. time，当前时间
        self.now += pd.Timedelta('1min') # 每分钟仿真一次
        data['time'] = self.now
        print('仿真时间：', data['time'])
        self.crew.update_status(self.now) # 更新人员的 status 状态

        # 每增加一天
        # if (self.now+pd.Timedelta('14min')).day != (self.now+pd.Timedelta('15min')).day:
        if (self.now).day != (self.now+pd.Timedelta('1min')).day:
            print('---------next day---------')
            self.crew.record_single_day(str(self.now.month)+'-'+str(self.now.day))
        
        data['crew'] = self.crew.dfCrew
        # 3. task，任务信息
        flights_list = self.get_margin_flights() # 获取能够观察到的航班
        data['flights'] = flights_list
        print('观察到航班：', data['flights'])

        if flights_list: 
            for flight in flights_list:
                task = self.generation_task(flight) # 根据航班信息生成任务
                self.taskSet.add_task(task) # 向任务集合中添加任务
        
        data['tasks'] = self.taskSet.tasks
        group = (self.now - self.begin).days % 4 + 1 # 每一天同时只有一个 Group 工作
        Crews_obj = self.crew.dfCrew[self.crew.dfCrew['group'] == group]

        data['group'] = group
        name_list = None
        data['lounge'] = -1 # lounge 默认为 -1

        gate_terminal = self.gate_terminal

        if self.taskSet.isnotnull():   # 这里应该是获取所有需要解决的任务列表，然后匹配所有的任务
            for task in self.taskSet:
                data['lounge'] = self.get_lounge(task.gate)
                lounge = self.get_lounge(task.gate)

                df_can = self.crew.get_near1_people_sim(lounge, group, self.now) # 获取附近 1/4 的人员
                df_can = df_can.sort_values(by='free',ascending=False)

                df_can2 = self.crew.get_near2_people_sim(lounge, group, self.now)  # 获取附近 1/2 的空闲人员
                df_can2 = df_can2.sort_values(by='free',ascending=False)

                df_can3 = self.crew.get_near3_people_sim(lounge, group, self.now)  # 获取附近全部的空闲人员
                df_can3 = df_can3.sort_values(by='free',ascending=False)
 
                name_list = self.operator.match_algorithm(task, df_can, df_can2, df_can3)

                # 保存 namelist
                if name_list:
                    name_list_keys = list(name_list.keys())
                    print(name_list_keys)
                    name_list_copy = copy.deepcopy(name_list_keys)  # 这里是否要用deepcopy
                    task.get_taskPlus()

                    # 移除任务
                    print('移除任务前', self.taskSet.tasks)
                    
                    # while self.taskSet.tasks:
                        
                    print(task.taskPlus)
                    self.taskSet.tasks.remove(task)
                    print(task.get_task_description())

                    x2=gate_terminal[gate_terminal['gate'] == task.gate]['x'].tolist()[0]
                    y2=gate_terminal[gate_terminal['gate'] == task.gate]['y'].tolist()[0]

                    # 更新工作人员状态
                    for task_i in task.taskPlus:
                        name = name_list_copy[0]
                        print(task_i)
                        # 计算员工移动距离
                        if name in ['虚拟人0','虚拟人1','虚拟人2','虚拟人3','虚拟人4']:
                            distance=0
                            wait_time=0
                            self.single_null += 1
                        else:
                            self.single_total += 1  # 表示任务完成一个
                            crew_location = Crews_obj[Crews_obj['name']==name]['location'].tolist()[0]
                            x1=gate_terminal[gate_terminal['gate'] == crew_location]['x'].tolist()[0]
                            y1=gate_terminal[gate_terminal['gate'] == crew_location]['y'].tolist()[0]
                            distance = abs(x1 - x2) + abs(y1 - y2) 
                            # 计算任务等待时间
                            if Crews_obj[Crews_obj['name']==name]['status'].tolist()[0] == 0:
                                wait_time = 0
                            else:
                                crew__end_time = Crews_obj[Crews_obj['name']==name]['end_time'].tolist()[0]
                                wait_time = (crew__end_time - task.time) / np.timedelta64(1, 'm')  # 计算等待时间，单位：分钟
                                if wait_time < 0:
                                    wait_time=0
                            self.crew._update_people_status_KM(distance, name, task, self.now)
                        
                        self.taskSet.update_task_status_KM(name, task_i)  # 输出 "xx员工完成xx任务"
                        self.record_process_KM(task_i, task.gate, task.time, task.lounge, task.taskDuration, name, distance, wait_time)
                        name_list_copy.remove(name)
                    
                    print('移除任务后', self.taskSet.tasks)
                # else:
                #     if task.isdead():
                #         self.taskSet.tasks.remove(task)
                #         name_list = None
                #         self.single_null += 1
                #         self.record_process(task.gate,task.time,task.lounge,task.taskDuration,name_list)
                #
                # task.update_status()

        data['name_list'] = name_list
        print('人员名单', data['name_list'])
        data['single_total'] = self.single_total
        data['single_null'] = self.single_null
        return data

    def step_KM(self):
        '''
        每次仿真的前进步骤s 使用KM匹配算法
        '''
        data = {} # 想清楚 data 需要有什么数据

        for i in range(1, 16):  # 每15分钟匹配一次,但是每1分钟都更新人员信息
            # 1. time，当前时间
            self.now += pd.Timedelta('1min')

            if (self.now + pd.Timedelta('14min')).day != (self.now+pd.Timedelta('15min')).day:
                print('---------next day---------')
                break

            data['time'] = self.now
            self.crew.update_status_KM(self.now) # 更新人员的 status 状态

        # # 1. time，当前时间
        # self.now += pd.Timedelta('15min') # 每分钟仿真一次
        # data['time'] = self.now

        # # 2. crew，人员信息
        # self.crew.update_status_KM(self.now) # 更新人员的 status 状态

        
        data['crew'] = self.crew.dfCrew
        # 3. task，任务信息
        flights_list = self.get_margin_flights() # 获取能够观察到的航班
        # print(flights_list)
        data['flights'] = flights_list

        if flights_list: 
            for flight in flights_list:
                task = self.generation_task(flight) # 根据航班信息生成任务
                self.taskSet.add_task(task) # 向任务集合中添加任务
        
        data['tasks'] = self.taskSet.tasks

        group = (self.now - self.begin).days % 4 + 1 # 每一天同时只有一个 Group 工作
        data['group'] = group
        data['lounge'] = -1 # lounge 默认为 -1

        # 二分图的左顶点
        name_list = None
        Crews_obj = self.crew.dfCrew[self.crew.dfCrew['group'] == group]
        Crews = Crews_obj['name'].tolist()
        # print(Crews_obj)

        # 二分图的右顶点
        Tasks=[]

        Tasks_fail=[]

        # 二分图的权重
        match_rate=[]

        trans = ['isYiBan','isFangXing','isWeiXiu','isZhongWen','isYingWen']
        gate_terminal=self.gate_terminal

        if self.taskSet.isnotnull():   # 这里应该是获取所有需要解决的任务列表，然后匹配所有的任务
            for task in self.taskSet:
                gate = task.gate
                lounge = self.get_lounge(task.gate)
                taskList = task.taskList
                print('gate:', gate, 'taskList:', taskList)

                task.get_taskPlus()
                for task_i in task.taskPlus:
                    Tasks.append(task_i)
                    # print(task_i)
                    i = int(task_i[-4])
                    # 计算权重
                    match=[]
                    for index, c in Crews_obj.iterrows():
                        # print(c)
                        if i==5:  # 如果没有资质约束-随便匹配一个人
                            # x1=gate_terminal[gate_terminal['gate'] == c['location']]['x'].tolist()[0]
                            # y1=gate_terminal[gate_terminal['gate'] == c['location']]['y'].tolist()[0]
                            # x2=gate_terminal[gate_terminal['gate'] == gate]['x'].tolist()[0]
                            # y2=gate_terminal[gate_terminal['gate'] == gate]['y'].tolist()[0]
                            # distance = abs(x1 - x2) + abs(y1 - y2)
                            # movetime = distance/5.56/60
                            if ((c['status'] == 0) or (c['status'] == 1 and c['lounge'] == lounge and c['end_time']<=(task.time) + pd.Timedelta('15 min'))):
                            # if ((c['status'] == 0) or (c['status'] == 1 and c['end_time']<=(task.time) + pd.Timedelta('15 min'))):

                                # 空闲优先
                                freetime = c['free']
                                rate = freetime

                                # # 工作量少的优先（工作量均衡）
                                # count = c['count']
                                # if count == 0:
                                #     rate = 1000
                                # else:
                                #     rate = (round(1000/count, 3))

                                # if distance != 0:
                                #     # rate = (round(10000/distance, 3)) # 距离优先
                                #     rate = freetime  # 空闲优先
                                #     # rate = (round(10000/distance, 3))*1000 + freetime  # 距离优先
                                # else:
                                #     # rate = (round(10000/distance, 3)) # 距离优先
                                #     rate = freetime  # 空闲优先
                                #     # rate = 10000 + freetime  # 距离优先
                                

                            else:
                                rate = -float('inf')
                        elif i!=5 and c[trans[i]] == 1:  # 技能资质约束-硬约束
                            # x1=gate_terminal[gate_terminal['gate'] == c['location']]['x'].tolist()[0]
                            # y1=gate_terminal[gate_terminal['gate'] == c['location']]['y'].tolist()[0]
                            # x2=gate_terminal[gate_terminal['gate'] == gate]['x'].tolist()[0]
                            # y2=gate_terminal[gate_terminal['gate'] == gate]['y'].tolist()[0]
                            # # print(x1,y1,x2,y2)
                            # distance = abs(x1 - x2) + abs(y1 - y2)
                            # movetime = distance/5.56/60

                            # if ((c['status'] == 0) or ( c['status'] == 1 and c['end_time']<=(task.time)  + pd.Timedelta('15 min'))): 
                            if ((c['status'] == 0) or (c['status'] == 1 and c['lounge'] == lounge and c['end_time']<=(task.time) + pd.Timedelta('15 min'))):
                                
                               # 空闲优先
                                freetime = c['free']
                                rate = freetime

                                # # 工作量少的优先（工作量均衡）
                                # count = c['count']
                                # if count == 0:
                                #     rate = 1000
                                # else:
                                #     rate = (round(1000/count, 3))

                                # if distance != 0:
                                #     rate = freetime  # 空闲优先
                                #     # rate =  (round(10000/distance, 3))*1000 + freetime  # 距离优先
                                # else:
                                #     rate = freetime  # 空闲优先
                                #     # rate =  10000 + freetime  # 距离优先
                            else:
                                rate = -float('inf')
                        else:
                            rate = -float('inf')  # 不满足技能约束

                        match.append(rate)
                    print('match:', match)
                    if any(_ >= 0 for _ in match):
                        match_rate.append(match)
                    else:
                        Tasks_fail.append(task_i)
                        Tasks.remove(task_i)
                        print(task_i, '该任务无法完成')
            
            print('需要解决的任务数:', len(Tasks))
            print('工作人员总数:', len(Crews))
            print('正在空闲人员数:', len(Crews_obj[Crews_obj['status'] == 0]))
            # # print('即将空闲人员数:', len(Crews_obj[Crews_obj['status'] == 1 & Crews_obj['end_time']<=(self.now)]))
            # print('match_rate:',match_rate)

            # 添加虚拟任务：
            surplus = len(Crews) - len(Tasks)
            if surplus > 0:
                for j in range(surplus):
                    Tasks.insert(0, str(0)+'-'+str(j))
                    match_rate.insert(0, [0] * (len(Crews)+1) )  # 注意这里的权重
                    # print('添加虚拟任务：', str(0)+'-'+str(j))

            # KM匹配
            for l in range(10):
                try:
                    match_result = self.operator.match_algorithm_KM(match_rate, Tasks, Crews)
                    break

                except FunctionTimedOut as e:
                    Tasks.remove(Tasks[-1])
                    match_rate.remove(match_rate[-1])
                    Tasks_fail.append(Tasks[-1])
                    print(Tasks[0], '该任务无法完成')
                    # 添加虚拟顶点
                    Tasks.insert(0, str(00)+'-'+str(l))
                    match_rate.insert(0, [0] * (len(Crews)+1) )

            print(match_result)
            trans = ['isYiBan', 'isFangXing', 'isWeiXiu', 'isZhongWen', 'isYingWen']
            name_list={}
            for key in match_result:
                if int(key[0])>0:
                    name = match_result[key][0]
                    zizhi = key.split("-")
                    name_list[name] = trans[int(zizhi[1])]  # TODO 修改
            
            print(name_list)

            # 保存 namelist
            if name_list:
                name_list_keys = list(name_list.keys())
                name_list_copy = copy.deepcopy(name_list_keys)  # 这里是否要用deepcopy

                # 移除任务
                print('移除任务前', self.taskSet.tasks)

                # for task in t:
                while self.taskSet.tasks:
                    task = self.taskSet.tasks[0]
                    self.single_total += 1  # 表示任务完成一个
                    self.taskSet.tasks.remove(task)
                    print(task.get_task_description())

                    
                    x2=gate_terminal[gate_terminal['gate'] == task.gate]['x'].tolist()[0]
                    y2=gate_terminal[gate_terminal['gate'] == task.gate]['y'].tolist()[0]
                    # print(x1,y1,x2,y2)
                
                    # 更新工作人员状态
                    for task_i in task.taskPlus:
                        if not task_i in Tasks_fail:
                            name = name_list_copy[0]
                            # 计算员工移动距离
                            crew_location = Crews_obj[Crews_obj['name']==name]['location'].tolist()[0]
                            x1=gate_terminal[gate_terminal['gate'] == crew_location]['x'].tolist()[0]
                            y1=gate_terminal[gate_terminal['gate'] == crew_location]['y'].tolist()[0]
                            distance = abs(x1 - x2) + abs(y1 - y2) 
                            # 计算任务等待时间
                            if Crews_obj[Crews_obj['name']==name]['status'].tolist()[0] == 0:
                                wait_time = 0
                            else:
                                crew__end_time = Crews_obj[Crews_obj['name']==name]['end_time'].tolist()[0]
                                wait_time = (crew__end_time - task.time) / np.timedelta64(1, 'm')  # 计算等待时间，单位：分钟
                                if wait_time < 0:
                                    wait_time=0

                            self.crew._update_people_status_KM(distance, name ,task, self.now)
                            self.taskSet.update_task_status_KM(name, task_i)  # 输出 "xx员工完成xx任务"
                            self.record_process_KM(task_i, task.gate, task.time, task.lounge, task.taskDuration, name, distance, wait_time)
                            name_list_copy.remove(name)
                        else:
                            name = '虚拟人'
                            distance=0
                            wait_time=0
                            self.taskSet.update_task_status_KM(name, task_i)  # 输出 "xx员工完成xx任务"
                            self.record_process_KM(task_i, task.gate, task.time, task.lounge, task.taskDuration, name, distance, wait_time)
                print('移除任务后', self.taskSet.tasks)
                
            # else:
            #     # 任务未完成, 这里没有修改，假设任务不会完不成
            #     if task.isdead():
            #         self.taskSet.tasks.remove(task)
            #         name_list = None
            #         self.single_null += 1  # 表示任务未完成一个
            #         self.record_process(task.gate,task.time,task.lounge,task.taskDuration,name_list)
            # task.update_status()

        data['name_list'] = name_list

        # 每增加一天
        if (self.now+pd.Timedelta('14min')).day != (self.now+pd.Timedelta('15min')).day:
        # if (self.now-self.begin).day != self.days:
            self.crew.record_single_day(str(self.now.month)+'-'+str(self.now.day))
            # self.days = (self.now-self.begin).days # 更新天数
            self.single_null = -1
            self.single_total = -1

        data['single_total'] = self.single_total
        data['single_null'] = self.single_null
    
        return data

    def step_ADSB(self,cover_name_list = None,enable_cover=False):
        '''
        每次仿真的前进步骤s
        '''
        data = {}  # 想清楚 data 需要有什么数据
        # 1. time，当前时间
        self.now += pd.Timedelta('1min')  # 每分钟仿真一次
        data['time'] = self.now
        self.crew.update_status(self.now)  # 更新人员的 status 状态

        # 每增加一天
        # if (self.now+pd.Timedelta('14min')).day != (self.now+pd.Timedelta('15min')).day:
        if (self.now).day != (self.now + pd.Timedelta('1min')).day:
            print('---------next day---------')
            self.crew.record_single_day(str(self.now.month) + '-' + str(self.now.day))

        data['crew'] = self.crew.dfCrew
        # 3. task，任务信息
        flights_list = self.get_margin_flights_ADSB()  # 获取能够观察到的航班
        if flights_list:
            print("时间：", self.now, " 观察到的航班flights_list：", [flight.flightnum for flight in flights_list])
        data['flights'] = flights_list

        if flights_list:
            for flight in flights_list:
                task = self.generation_task(flight)  # 根据航班信息生成任务
                self.taskSet.add_task(task)  # 向任务集合中添加任务

        data['tasks'] = self.taskSet.tasks
        group = (self.now - self.begin).days % 4 + 1  # 每一天同时只有一个 Group 工作
        Crews_obj = self.crew.dfCrew[self.crew.dfCrew['group'] == group]

        data['group'] = group
        name_list = None
        data['lounge'] = -1  # lounge 默认为 -1

        gate_terminal = self.gate_terminal

        if enable_cover:
            self.crew.cover_people(cover_name_list,self.now)

        if self.taskSet.isnotnull():  # 这里应该是获取所有需要解决的任务列表，然后匹配所有的任务
            for task in self.taskSet:
                data['lounge'] = self.get_lounge(task.gate)
                lounge = self.get_lounge(task.gate)

                df_can = self.crew.get_near1_people_sim(lounge, group, self.now)  # 获取附近 1/4 的人员
                df_can = df_can.sort_values(by='free', ascending=False)

                df_can2 = self.crew.get_near2_people_sim(lounge, group, self.now)  # 获取附近 1/2 的空闲人员
                df_can2 = df_can2.sort_values(by='free', ascending=False)

                df_can3 = self.crew.get_near3_people_sim(lounge, group, self.now)  # 获取附近全部的空闲人员
                df_can3 = df_can3.sort_values(by='free', ascending=False)

                name_list = self.operator.match_algorithm(task, df_can, df_can2, df_can3)

                # 保存 namelist
                if name_list:
                    name_list_keys = list(name_list.keys())
                    print(name_list_keys)
                    name_list_copy = copy.deepcopy(name_list_keys)  # 这里是否要用deepcopy
                    task.get_taskPlus()

                    # 移除任务
                    print('移除任务前', self.taskSet.tasks)

                    # while self.taskSet.tasks:

                    print(task.taskPlus)
                    self.taskSet.tasks.remove(task)
                    print(task.get_task_description())

                    x2 = gate_terminal[gate_terminal['gate'] == task.gate]['x'].tolist()[0]
                    y2 = gate_terminal[gate_terminal['gate'] == task.gate]['y'].tolist()[0]

                    # 更新工作人员状态
                    for task_i in task.taskPlus:
                        name = name_list_copy[0]
                        print(task_i)
                        # 计算员工移动距离
                        if name in ['虚拟人0', '虚拟人1', '虚拟人2', '虚拟人3', '虚拟人4']:
                            distance = 0
                            wait_time = 0
                            self.single_null += 1
                        else:
                            self.single_total += 1  # 表示任务完成一个
                            crew_location = Crews_obj[Crews_obj['name'] == name]['location'].tolist()[0]
                            x1 = gate_terminal[gate_terminal['gate'] == crew_location]['x'].tolist()[0]
                            y1 = gate_terminal[gate_terminal['gate'] == crew_location]['y'].tolist()[0]
                            distance = abs(x1 - x2) + abs(y1 - y2)
                            # 计算任务等待时间
                            if Crews_obj[Crews_obj['name'] == name]['status'].tolist()[0] == 0:
                                wait_time = 0
                            else:
                                crew__end_time = Crews_obj[Crews_obj['name'] == name]['end_time'].tolist()[0]
                                wait_time = (crew__end_time - task.time) / np.timedelta64(1, 'm')  # 计算等待时间，单位：分钟
                                if wait_time < 0:
                                    wait_time = 0
                            self.crew._update_people_status_KM(distance, name, task, self.now)

                        self.taskSet.update_task_status_KM(name, task_i)  # 输出 "xx员工完成xx任务"
                        self.record_process_KM(task_i, task.gate, task.time, task.lounge, task.taskDuration, name,
                                               distance, wait_time)
                        name_list_copy.remove(name)

                    print('移除任务后', self.taskSet.tasks)
                # else:
                #     if task.isdead():
                #         self.taskSet.tasks.remove(task)
                #         name_list = None
                #         self.single_null += 1
                #         self.record_process(task.gate,task.time,task.lounge,task.taskDuration,name_list)
                #
                # task.update_status()
        if enable_cover:
            self.crew.recover_people(cover_name_list,self.now)
        data['name_list'] = name_list
        data['single_total'] = self.single_total
        data['single_null'] = self.single_null
        return data

    def step_ADSB_KM(self,cover_name_list = None,enable_cover=False):
        '''
        每次仿真的前进步骤s
        '''
        data = {}  # 想清楚 data 需要有什么数据
        # 1. time，当前时间
        self.now += pd.Timedelta('1min')  # 每分钟仿真一次
        data['time'] = self.now
        self.crew.update_status(self.now)  # 更新人员的 status 状态

        # 每增加一天
        # if (self.now+pd.Timedelta('14min')).day != (self.now+pd.Timedelta('15min')).day:
        if (self.now).day != (self.now + pd.Timedelta('1min')).day:
            print('---------next day---------')
            self.crew.record_single_day(str(self.now.month) + '-' + str(self.now.day))

        data['crew'] = self.crew.dfCrew
        # 3. task，任务信息
        flights_list = self.get_margin_flights_ADSB()  # 获取能够观察到的航班
        if flights_list:
            print("时间：", self.now, " 观察到的航班flights_list：", [flight.flightnum for flight in flights_list])
        data['flights'] = flights_list

        if flights_list:
            for flight in flights_list:
                task = self.generation_task(flight)  # 根据航班信息生成任务
                self.taskSet.add_task(task)  # 向任务集合中添加任务

        data['tasks'] = self.taskSet.tasks
        group = (self.now - self.begin).days % 4 + 1  # 每一天同时只有一个 Group 工作
        Crews_obj = self.crew.dfCrew[self.crew.dfCrew['group'] == group]

        data['group'] = group
        name_list = None
        data['lounge'] = -1  # lounge 默认为 -1

        # 二分图的左顶点
        name_list = None
        Crews_obj = self.crew.dfCrew[self.crew.dfCrew['group'] == group]
        Crews = Crews_obj['name'].tolist()
        # print(Crews_obj)

        # 二分图的右顶点
        Tasks = []

        Tasks_fail = []

        # 二分图的权重
        match_rate = []

        trans = ['isYiBan', 'isFangXing', 'isWeiXiu', 'isZhongWen', 'isYingWen']
        gate_terminal = self.gate_terminal

        if self.taskSet.isnotnull():  # 这里应该是获取所有需要解决的任务列表，然后匹配所有的任务
            for task in self.taskSet:
                gate = task.gate
                lounge = self.get_lounge(task.gate)
                taskList = task.taskList
                print('gate:', gate, 'taskList:', taskList)

                task.get_taskPlus()
                for task_i in task.taskPlus:
                    Tasks.append(task_i)
                    # print(task_i)
                    i = int(task_i[-4])
                    # 计算权重
                    match = []
                    for index, c in Crews_obj.iterrows():
                        # print(c)
                        if i == 5:  # 如果没有资质约束-随便匹配一个人
                            # x1=gate_terminal[gate_terminal['gate'] == c['location']]['x'].tolist()[0]
                            # y1=gate_terminal[gate_terminal['gate'] == c['location']]['y'].tolist()[0]
                            # x2=gate_terminal[gate_terminal['gate'] == gate]['x'].tolist()[0]
                            # y2=gate_terminal[gate_terminal['gate'] == gate]['y'].tolist()[0]
                            # distance = abs(x1 - x2) + abs(y1 - y2)
                            # movetime = distance/5.56/60
                            if ((c['status'] == 0) or (c['status'] == 1 and c['lounge'] == lounge and c['end_time'] <= (
                            task.time) + pd.Timedelta('15 min'))):
                                # if ((c['status'] == 0) or (c['status'] == 1 and c['end_time']<=(task.time) + pd.Timedelta('15 min'))):

                                # 空闲优先
                                freetime = c['free']
                                rate = freetime

                                # # 工作量少的优先（工作量均衡）
                                # count = c['count']
                                # if count == 0:
                                #     rate = 1000
                                # else:
                                #     rate = (round(1000/count, 3))

                                # if distance != 0:
                                #     # rate = (round(10000/distance, 3)) # 距离优先
                                #     rate = freetime  # 空闲优先
                                #     # rate = (round(10000/distance, 3))*1000 + freetime  # 距离优先
                                # else:
                                #     # rate = (round(10000/distance, 3)) # 距离优先
                                #     rate = freetime  # 空闲优先
                                #     # rate = 10000 + freetime  # 距离优先


                            else:
                                rate = -float('inf')
                        elif i != 5 and c[trans[i]] == 1:  # 技能资质约束-硬约束
                            # x1=gate_terminal[gate_terminal['gate'] == c['location']]['x'].tolist()[0]
                            # y1=gate_terminal[gate_terminal['gate'] == c['location']]['y'].tolist()[0]
                            # x2=gate_terminal[gate_terminal['gate'] == gate]['x'].tolist()[0]
                            # y2=gate_terminal[gate_terminal['gate'] == gate]['y'].tolist()[0]
                            # # print(x1,y1,x2,y2)
                            # distance = abs(x1 - x2) + abs(y1 - y2)
                            # movetime = distance/5.56/60

                            # if ((c['status'] == 0) or ( c['status'] == 1 and c['end_time']<=(task.time)  + pd.Timedelta('15 min'))):
                            if ((c['status'] == 0) or (c['status'] == 1 and c['lounge'] == lounge and c['end_time'] <= (
                            task.time) + pd.Timedelta('15 min'))):

                                # 空闲优先
                                freetime = c['free']
                                rate = freetime

                                # # 工作量少的优先（工作量均衡）
                                # count = c['count']
                                # if count == 0:
                                #     rate = 1000
                                # else:
                                #     rate = (round(1000/count, 3))

                                # if distance != 0:
                                #     rate = freetime  # 空闲优先
                                #     # rate =  (round(10000/distance, 3))*1000 + freetime  # 距离优先
                                # else:
                                #     rate = freetime  # 空闲优先
                                #     # rate =  10000 + freetime  # 距离优先
                            else:
                                rate = -float('inf')
                        else:
                            rate = -float('inf')  # 不满足技能约束

                        match.append(rate)
                    print('match:', match)
                    if any(_ >= 0 for _ in match):
                        match_rate.append(match)
                    else:
                        Tasks_fail.append(task_i)
                        Tasks.remove(task_i)
                        print(task_i, '该任务无法完成')


            print('需要解决的任务数:', len(Tasks))
            print('工作人员总数:', len(Crews))
            print('正在空闲人员数:', len(Crews_obj[Crews_obj['status'] == 0]))
            # # print('即将空闲人员数:', len(Crews_obj[Crews_obj['status'] == 1 & Crews_obj['end_time']<=(self.now)]))
            # print('match_rate:',match_rate)

            # 添加虚拟任务：
            surplus = len(Crews) - len(Tasks)
            if surplus > 0:
                for j in range(surplus):
                    Tasks.insert(0, str(0) + '-' + str(j))
                    match_rate.insert(0, [0] * (len(Crews) + 1))  # 注意这里的权重
                    # print('添加虚拟任务：', str(0)+'-'+str(j))

            # KM匹配
            for l in range(10):
                try:
                    match_result = self.operator.match_algorithm_KM(match_rate, Tasks, Crews)
                    break

                except FunctionTimedOut as e:
                    Tasks.remove(Tasks[-1])
                    match_rate.remove(match_rate[-1])
                    Tasks_fail.append(Tasks[-1])
                    print(Tasks[0], '该任务无法完成')
                    # 添加虚拟顶点
                    Tasks.insert(0, str(00) + '-' + str(l))
                    match_rate.insert(0, [0] * (len(Crews) + 1))

            print(match_result)
            trans = ['isYiBan', 'isFangXing', 'isWeiXiu', 'isZhongWen', 'isYingWen']
            name_list = {}
            for key in match_result:
                if int(key[0]) > 0:
                    name = match_result[key][0]
                    zizhi = key.split("-")
                    name_list[name] = trans[int(zizhi[1])]  # TODO 修改

            print(match_result)
            trans = ['isYiBan', 'isFangXing', 'isWeiXiu', 'isZhongWen', 'isYingWen']
            name_list = {}
            for key in match_result:
                if int(key[0]) > 0:
                    name = match_result[key][0]
                    zizhi = key.split("-")
                    if len(zizhi) == 3:
                        name_list[name] = trans[int(zizhi[1])]  # TODO 修改
                    elif len(zizhi) == 4:
                        name_list[name] = 'default'
            print(name_list)

            # 保存 namelist
            if name_list:
                name_list_keys = list(name_list.keys())
                name_list_copy = copy.deepcopy(name_list_keys)  # 这里是否要用deepcopy

                # 移除任务
                print('移除任务前', self.taskSet.tasks)

                # for task in t:
                while self.taskSet.tasks:
                    task = self.taskSet.tasks[0]
                    self.single_total += 1  # 表示任务完成一个
                    self.taskSet.tasks.remove(task)
                    print(task.get_task_description())

                    x2 = gate_terminal[gate_terminal['gate'] == task.gate]['x'].tolist()[0]
                    y2 = gate_terminal[gate_terminal['gate'] == task.gate]['y'].tolist()[0]
                    # print(x1,y1,x2,y2)

                    # 更新工作人员状态
                    for task_i in task.taskPlus:
                        if not task_i in Tasks_fail:
                            name = name_list_copy[0]
                            # 计算员工移动距离
                            crew_location = Crews_obj[Crews_obj['name'] == name]['location'].tolist()[0]
                            x1 = gate_terminal[gate_terminal['gate'] == crew_location]['x'].tolist()[0]
                            y1 = gate_terminal[gate_terminal['gate'] == crew_location]['y'].tolist()[0]
                            distance = abs(x1 - x2) + abs(y1 - y2)
                            # 计算任务等待时间
                            if Crews_obj[Crews_obj['name'] == name]['status'].tolist()[0] == 0:
                                wait_time = 0
                            else:
                                crew__end_time = Crews_obj[Crews_obj['name'] == name]['end_time'].tolist()[0]
                                wait_time = (crew__end_time - task.time) / np.timedelta64(1, 'm')  # 计算等待时间，单位：分钟
                                if wait_time < 0:
                                    wait_time = 0

                            self.crew._update_people_status_KM(distance, name, task, self.now)
                            self.taskSet.update_task_status_KM(name, task_i)  # 输出 "xx员工完成xx任务"
                            self.record_process_KM(task_i, task.gate, task.time, task.lounge, task.taskDuration, name,
                                                   distance, wait_time)
                            name_list_copy.remove(name)
                        else:
                            name = '虚拟人'
                            distance = 0
                            wait_time = 0
                            self.taskSet.update_task_status_KM(name, task_i)  # 输出 "xx员工完成xx任务"
                            self.record_process_KM(task_i, task.gate, task.time, task.lounge, task.taskDuration, name,
                                                   distance, wait_time)
                print('移除任务后', self.taskSet.tasks)
        if enable_cover:
            self.crew.recover_people(cover_name_list,self.now)
            # else:
            #     # 任务未完成, 这里没有修改，假设任务不会完不成
            #     if task.isdead():
            #         self.taskSet.tasks.remove(task)
            #         name_list = None
            #         self.single_null += 1  # 表示任务未完成一个
            #         self.record_process(task.gate,task.time,task.lounge,task.taskDuration,name_list)
            # task.update_status()

        data['name_list'] = name_list

        # 每增加一天
        if (self.now + pd.Timedelta('14min')).day != (self.now + pd.Timedelta('15min')).day:
            # if (self.now-self.begin).day != self.days:
            self.crew.record_single_day(str(self.now.month) + '-' + str(self.now.day))
            # self.days = (self.now-self.begin).days # 更新天数
            self.single_null = -1
            self.single_total = -1

        data['single_total'] = self.single_total
        data['single_null'] = self.single_null

        return data
    
    def step_cover(self, cover_name_list, cover_type = 'random'):
        '''
        每次仿真的前进步骤s
        '''
        if cover_type == 'random':
            print('cover for random')
            return self.step_ADSB(cover_name_list,enable_cover=True)
        elif cover_type == 'KM':
            print('cover for KM')
            return self.step_ADSB_KM(cover_name_list,enable_cover=True)
    
    def is_done(self):
        # return self.flightSet.index == 10
        return self.flightSet.is_done()

    def is_done_ADSB(self):
        now = self.now
        return self.flightSet.is_done_ADSB(now)

    
