import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import numpy as np
from task import *
from aviation import *
from ADSB import *
from copy import deepcopy


class Flights:
    ''' 
    单个航班类
    '''
    def __init__(self) -> None:
        '''
        gate: d登机口
        planDate: 计划日期
        planTime: 计划时间
        actualDate: 实际日期
        actualTime: 实际时间
        ac: 航司信息
        boundType: 类型
        '''
        self.gate = 0 # 位置
        self.plan__datetime = 0
        self.actual_datetime = 0 # 实际时间
        self.ac = None # 航司信息
        self.boundType = None # 类型,inbound or outbound
        self.airType = None # 机型
        self.flightnum = 0 # 航班号
        self.lon = 0  # 经度
        self.lat = 0  # 纬度
        self.he = 0  # 高度

    def update(self,**kwargs):
        for key,value in kwargs.items():
            if hasattr(self,key):
                # hasattr(self,key) 判断是否有这个属性
                # setattr(self,key,value) 设置属性
                setattr(self,key,value)
            else:
                print('No such attribute')

    def update_from_row(self,row):
        '''
        从行中更新航班信息
        '''
        self.gate = row['机位']
        self.plan_datetime = row['plan_datetime']
        self.actual_datetime = row['actual_datetime']
        self.ac = row['航空公司']
        self.boundType = row['type']
        self.airType = row['机型']
        self.flightnum = row['机号']

    def update_from_row_ADSB(self, row, time, lon, lat, he):
        '''
        从行中更新航班信息
        '''
        self.gate = row['机位']
        self.plan_datetime = row['plan_datetime']
        self.actual_datetime = time  # 实际到达时间是根据ADSB获得的
        self.ac = row['航空公司']
        self.boundType = row['type']
        self.airType = row['机型']
        self.flightnum = row['机号']
        self.lon = lon
        self.lat = lat
        self.he = he

    def to_row(self):
        '''
        转换成行
        '''
        return pd.DataFrame([self.__dict__])

class FlightsSet:
    ''' 
    航班集合类

    方法
    ----
    login: 注册航班信息
    filter_by_id: 根据航司信息筛选航班
    get_begin_time: 获取最早出发时间
    get_near_flights: 按照规则获取可观察的航班, 用于生成任务
    is_done: 判断所有航班是否完全排列
    '''
    def __init__(self) -> None:
        '''
        ----
        df_flights: 所有的航班信息 pandas.DataFrame
        Margin: 时间间隔
        index: 索引
        '''
        self.df_flights = None  # 所有的航班信息
        self.df_flights_left = None # 未完成的航班信息
        self.ADSB_data = None # 所有ADSB数据
        self.Margin = 15 # TODO 时间间隔
        self.index = 0 # 索引
        self.ADSB = ADSB()  # 航班信息

    def _fileter_from_origin(self, df_flights):
        '''
        内部方法
        '''
        df_flights['actual_time'] = pd.to_timedelta(df_flights['actual_time'])
        df_flights['actual_datetime'] = df_flights['actual_date'] + df_flights['actual_time']
        df_flights.sort_values(by='actual_datetime', inplace=True)
        df_flights.reset_index(drop=True, inplace=True)
        df_flights.drop(['actual_time', 'actual_date'], axis=1, inplace=True)

        df_flights['plan_time'] = pd.to_timedelta(df_flights['plan_time'])
        df_flights['plan_datetime'] = df_flights['plan_date'] + df_flights['plan_time']
        # df_flights.sort_values(by='plan_datetime', inplace=True)
        df_flights.reset_index(drop=True, inplace=True)
        df_flights.drop(['plan_time', 'plan_date'], axis=1, inplace=True)

        df_flights.dropna(inplace=True)
        return df_flights

    def login(self, path):
        ''' 
        根据历史观察数据, 注册航班信息
        '''
        flights = pd.read_excel(path)
        flights['index'] = flights.index
        # flights['actual_datetime_new'] = ''
        self.df_flights = self._fileter_from_origin(flights)
        # print(self.df_flights)
        self.df_flights_left = deepcopy(self.df_flights)  # 深拷贝

    def filter_by_id(self, codingId):
        ''' 
        根据航司信息筛选航班
        '''
        self.df_flights = self.df_flights[self.df_flights['航空公司'].isin(codingId)]
        self.df_flights.reset_index(drop=True, inplace=True)

    def get_begin_time(self):
        ''' 
        获取最早出发时间
        '''
        return self.df_flights['actual_datetime'][0]

    def get_begin_time_ADSB(self):
        '''
        获取最早出发时间
        '''
        time_earliest = self.df_flights['plan_datetime'][0]  # TODO
        previous_hour = time_earliest.replace(minute=0, second=0) - timedelta(minutes=1)

        return previous_hour
    
    def get_near_flights(self, time, margin):
        ''' 
        按照规则获取可观察的航班, 用于生成任务
        '''
        res = []
        # print('全部任务是否完成：',self.is_done())
        # print('航班时间：',self.df_flights['actual_datetime'][self.index])
        # print(self.index)
        while not self.is_done() and self.df_flights['actual_datetime'][self.index] <= time + margin:
            flight = Flights()
            # print(self.df_flights.iloc[self.index])
            flight.update_from_row(self.df_flights.iloc[self.index]) # 从行中转换成为航班
            res.append(flight)
            self.index += 1
        return res

    def get_near_flights_from_ADSB(self, time):
        '''
            读取ADSB数据文件
        '''
        # folder_path = '../dataset/ADS-B/' + time.strftime('%Y-%m-%d')  # TODO 仿真的可视化路径
        folder_path = './dataset/ADS-B/' + time.strftime('%Y-%m-%d')  # TODO 可视化平台的路径

        current_hour = time.strftime('%H')
        current_minute = time.strftime('%M')
        file_name = f"{time.strftime('%Y-%m-%d')}_{current_hour}.csv"
        file_path = os.path.join(folder_path, file_name)

        # 检查文件是否存在，存在则读取
        if current_minute == '00':
            if os.path.exists(file_path):
                print(f"Reading file: {file_name}")
                self.ADSB_data = pd.read_csv(file_path)
            else:
                print(time)
                print(file_path)
                print(f"File {file_name} not found.")

            self.ADSB_data.drop(['ID', 'HX', 'GV', 'CO', 'FN', 'FN2', 'TE', 'ETA', 'SR'], inplace=True, axis=1)
            # 筛选浦东机场的航班数据
            self.ADSB_data = self.ADSB_data[(self.ADSB_data['OA'] == 'PVG') | (self.ADSB_data['DA'] == 'PVG')]
            self.ADSB_data['UPDATE_TIME'] = pd.to_datetime(self.ADSB_data['UPDATE_TIME'])
            print(self.ADSB_data.head())  # 打印数据的前几行
        # else:
        #     print(current_minute)

        '''
            按照ADSB数据获取可观察航班
        '''
        # 获取可观测到的数据
        ADSB_data_one_minute = self.ADSB_data[self.ADSB_data['UPDATE_TIME'] <= time]

        res = []
        # 按照ADSB数据获取的可观察航班，包括
        flight_ADSB = self.ADSB.monitor_flight_data(ADSB_data_one_minute, time)   # 区域判断
        # flight_ADSB = self.ADSB.monitor_flight_data_2(ADSB_data_one_minute, time)   # 距离判断

        if flight_ADSB:
            # 提取航班号列表
            flight_ADSB_nums = [flight['flightnum'] for flight in flight_ADSB]
            # print("观测到的所有航班", flight_ADSB_nums)
            flight_ADSB_times = {flight['flightnum']: flight['time'] for flight in flight_ADSB}
            flight_ADSB_types = {flight['flightnum']: flight['type'] for flight in flight_ADSB}
            flight_ADSB_lon  = {flight['flightnum']: flight['LO'] for flight in flight_ADSB}
            flight_ADSB_lat = {flight['flightnum']: flight['LA'] for flight in flight_ADSB}
            flight_ADSB_he = {flight['flightnum']: flight['HE'] for flight in flight_ADSB}

            # 筛选计划航班号在ADSB观测列表中的数据
            # flights_in_A_df = self.df_flights[self.df_flights['机号'].isin(flight_ADSB_nums)]

            # 筛选计划航班和ADSB对应的数据
            selected_indices = []
            for flightnum in flight_ADSB_nums:
                if flightnum in self.df_flights_left['机号'].values:
                    flight_plan_ADSB = self.df_flights_left[self.df_flights_left['机号'] == flightnum]  # 航班号要对应
                    flight_plan_ADSB = flight_plan_ADSB[flight_plan_ADSB['type'] == flight_ADSB_types[flightnum]]  # 进出港类型要对应
                    flight_row = flight_plan_ADSB.copy()
                    # 对每个航班号，选择一条时间最接近的记录
                    if len(flight_row) > 0:
                        flight = Flights()
                        flight_row['time_diff'] = (pd.to_datetime(flight_row['plan_datetime']) - pd.to_datetime(flight_ADSB_times[flightnum])).abs()
                        closest_row = flight_row.loc[flight_row['time_diff'].idxmin()]
                        # 时间要小于24个小时
                        if closest_row['time_diff'] > timedelta(hours=24):
                            continue
                        index = closest_row['index']
                        # print(index, self.df_flights[self.df_flights['index'] == index])
                        flight.update_from_row_ADSB(self.df_flights_left[self.df_flights_left['index'] == index].iloc[0], pd.to_datetime(flight_ADSB_times[flightnum]),
                                                    flight_ADSB_lon[flightnum], flight_ADSB_lat[flightnum], flight_ADSB_he[flightnum],)  # 从行中转换成为航班
                        # print(flight)
                        res.append(flight)
                        selected_indices.append(index)  # 获取行索引
                        self.index += 1

            # 删除选中的行
            if selected_indices:
                index_to_drop = self.df_flights_left[self.df_flights_left['index'].isin(selected_indices)].index
                self.df_flights_left.drop(index_to_drop, inplace=True)
        return res

    
    def is_done(self):
        ''' 
        判断所有航班是否完成
        '''
        return self.index >= len(self.df_flights)

    def is_done_ADSB(self, now):
        '''
        判断所有航班是否完成
        '''
        time_latest = self.df_flights['actual_datetime'][0]  # TODO
        # time_latest = self.df_flights['plan_datetime'][0]
        endtime = time_latest + timedelta(minutes=1)

        return now == endtime
    
    def add_flight(self,flight):
        ''' 
        暂时未开发
        '''
        self.flights.append(flight)
    
    def get_flights(self,idx):
        ''' 
        暂时未开发
        '''
        return Flights().from_row(self.df_flights.iloc[idx])
    