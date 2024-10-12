1. crew 中新增函数

# 170行

    def cover_people(self,name_dict,now):
        '''
        屏蔽当前人员的信息
        '''
        print(name_dict)
        for name in name_dict:
            self.dfCrew.loc[self.dfCrew['name'] == name, 'status'] = 2 # 将其状态设置为被占用
    
    def recover_people(self,name_dict,now):
        ''' 
        恢复当前人员的信息
        '''
        for  name in name_dict:
            self.dfCrew.loc[self.dfCrew['name'] == name, 'status'] = 0 # 将其状态设置为空闲

2. airports 新增 step_cover 函数，主要在匹配时候调用上述两个函数, 909行
    def step_cover(self,cover_name_list):
        '''
        每次仿真的前进步骤s
        '''
        data = {} # 想清楚 data 需要有什么数据
        # 1. time，当前时间
        self.now += pd.Timedelta('1min') # 每分钟仿真一次
        data['time'] = self.now
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
        ** self.crew.cover_people(cover_name_list,self.now)** 
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
        **self.crew.recover_people(cover_name_list,self.now)**
        data['name_list'] = name_list
        data['single_total'] = self.single_total
        data['single_null'] = self.single_null
        return data

3. visual demo 中新增 xy