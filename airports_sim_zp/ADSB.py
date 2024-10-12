import pandas as pd
import math
import time
from datetime import datetime, timedelta
from geopy.distance import geodesic

class ADSB:
    def __init__(self) -> None:
        # 地球半径，单位：千米
        self.EARTH_RADIUS_KM = 6371.0

        # 上海浦东国际机场的经纬度
        self.CENTER_LON  = 121.808603
        self.CENTER_LAT  = 31.142363

        # 圆的半径，单位：千米
        # self.CIRCLE_RADIUS_KM = 30.0
        self.CIRCLE_RADIUS_KM = 20.0


    # 定义一个函数，将经纬度转换为以中心点为原点的平面坐标（单位：千米）
    def latlon_to_xy(self, lon, lat, center_lon, center_lat):
        """
        将经纬度转换为以中心点为原点的平面坐标（单位：千米）
        """
        x = (lon - center_lon) * 111 * math.cos(math.radians(center_lat))
        y = (lat - center_lat) * 111
        return x, y

    # 定义Haversine公式计算两点之间的距离
    def haversine(self, lon1, lat1, lon2, lat2):
        """
        计算两点之间的Haversine距离，单位：千米
        """
        # 将角度转换为弧度
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

        # 计算经纬度差值
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        # Haversine公式
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # 返回两点之间的距离，单位：千米
        distance_km = self.EARTH_RADIUS_KM * c
        return distance_km

    # 定义函数，判断线段AB是否与圆相交
    def line_circle_intersect(self, A, B, C, R):
        """
        判断线段AB是否与以C为中心、R为半径的圆相交
        A, B, C为平面坐标（x, y），R为半径
        """
        x1, y1 = A
        x2, y2 = B
        x0, y0 = C

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            # A和B是同一个点，检查该点是否在圆内
            distance = math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
            return distance <= R

        # 计算参数t，使得P = A + t*(B - A)是AB线上到C点最近的点
        t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)

        # 限制t在[0,1]之间，保证P在线段AB上
        t = max(0, min(1, t))

        # 最近点P的坐标
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # 计算C到P的距离
        distance = math.sqrt((x0 - closest_x) ** 2 + (y0 - closest_y) ** 2)

        return distance <= R

    # 划定区域
    def monitor_flight_data(self, ADSB_data, time):
        """
            读取数据，筛选并判断航班连线是否与指定圆相交
        """
        # 初始化一个空的DataFrame来保存累积数据
        # 使用多列索引以便于后续操作
        accumulated_data = pd.DataFrame(columns=['LO', 'LA', 'HE', 'RE', 'FT', 'OA', 'DA', 'UPDATE_TIME'])

        # 设置'UPDATE_TIME'列为datetime类型
        accumulated_data['UPDATE_TIME'] = pd.to_datetime(accumulated_data['UPDATE_TIME'])

        # 每分钟执行一次
        now = time
        one_minute_ago = now - timedelta(minutes=1)

        # 读取CSV文件数据
        df = ADSB_data

        # 转换'time'列为datetime类型
        df['UPDATE_TIME'] = pd.to_datetime(df['UPDATE_TIME'])

        # 筛选出时间在过去1分钟的数据
        recent_data = df[df['UPDATE_TIME'] >= one_minute_ago]

        # 如果没有新数据，跳过本次循环
        if recent_data.empty:
            print(f"[{now}] 没有新数据。")
        else:
            # 合并累积数据和新数据
            combined_data = pd.concat([accumulated_data, recent_data])
            combined_data = combined_data.sort_values(by=['RE', 'UPDATE_TIME'], ascending=[True, False])

            # 将结果拼接为一个包含最早和最晚数据的表
            df_first = combined_data.groupby('RE').first().reset_index()
            df_last = combined_data.groupby('RE').last().reset_index()
            # 合并最早和最晚数据
            final_result = pd.concat([df_first, df_last]).drop_duplicates().reset_index(drop=True)

            # 按航班'RE'和'UPDATE_TIME'排序
            combined_data = final_result.sort_values(by=['RE', 'UPDATE_TIME'], ascending=[True, False])

            # 对每个航班'RE'保留最新的两条记录
            accumulated_data = combined_data.groupby('RE').head(2).reset_index(drop=True)

            # print(f"[{now}] 已更新累积数据，共有 {accumulated_data['RE'].nunique()} 个航班。")

        # 创建一个空的列表来存储符合条件的航班号
        intersecting_flights = []

        # 获取所有具有至少两条记录的航班号
        flights_with_two_records = accumulated_data['RE'].value_counts()
        flights_with_two_records = flights_with_two_records[flights_with_two_records >= 2].index.tolist()

        # 遍历这些航班号
        for flight in flights_with_two_records:
            # 获取该航班号的最新两条记录
            flight_records = accumulated_data[accumulated_data['RE'] == flight].sort_values(by='UPDATE_TIME', ascending=False).head(2)

            # 提取经纬度
            lon1, lat1, he1 = flight_records.iloc[0][['LO', 'LA', 'HE']]
            lon2, lat2, he2 = flight_records.iloc[1][['LO', 'LA', 'HE']]

            # 将经纬度转换为平面坐标
            A = self.latlon_to_xy(lon1, lat1, self.CENTER_LON, self.CENTER_LAT)
            B = self.latlon_to_xy(lon2, lat2, self.CENTER_LON, self.CENTER_LAT)
            C = (0, 0)  # 圆心在原点

            # 判断线段AB是否与圆相交
            if self.line_circle_intersect(A, B, C, self.CIRCLE_RADIUS_KM):
                if flight_records.iloc[1]['HE'] < 1500:  # 高度需要小于1500米
                    new_time = flight_records.iloc[1]['UPDATE_TIME'] + timedelta(minutes=15)  # 到达时间为当前点对应的时间加15min

                    if flight_records.iloc[1]['OA'] == 'PVG':  # 如果出发地点是PVG
                        intersecting_flights.append({'flightnum': flight, 'time': new_time, 'type': 'outbound', 'LA': lat2, 'LO': lon2, 'HE': he2})
                    else:
                        intersecting_flights.append({'flightnum': flight, 'time': new_time, 'type': 'inbound', 'LA': lat2, 'LO': lon2, 'HE': he2})

        # # 输出符合条件的航班号列表
        # if intersecting_flights:
        #     print(f"[{now}] 以下航班连线与上海浦东国际机场30km圆相交，共有 {len(intersecting_flights)} 个航班。")
        #     # for flight in intersecting_flights:
        #     #     print(f"  - {flight}")
        #     print([flight['flightnum'] for flight in intersecting_flights])
        # else:
        #     print(f"[{now}] 没有航班连线与上海浦东国际机场30km圆相交。")

        return intersecting_flights

    # 计算距离，通过距离和高度判断落地时间
    def monitor_flight_data_2(self, ADSB_data, time):
        """
            读取数据，筛选航班，计算距离，通过距离和高度判断落地时间
        """
        # 浦东国际机场的坐标
        pudong_airport_coords = (31.1445, 121.8050)

        # 每分钟执行一次
        now = time
        one_minute_ago = now - timedelta(minutes=1)

        # 读取CSV文件数据
        df = ADSB_data

        # 转换'time'列为datetime类型
        df['UPDATE_TIME'] = pd.to_datetime(df['UPDATE_TIME'])

        # 筛选出时间在过去1分钟的数据
        accumulated_data = df[df['UPDATE_TIME'] >= one_minute_ago]

        # 如果没有新数据，跳过本次循环
        if accumulated_data.empty:
            print(f"[{now}] 没有新数据。")
        else:
            accumulated_data = accumulated_data.sort_values(by=['RE', 'UPDATE_TIME'], ascending=[True, False])
            # 对每个航班'RE'保留最新的两条记录
            accumulated_data = accumulated_data.groupby('RE').head(1).reset_index(drop=True)

        # 创建一个空的列表来存储符合条件的航班号
        intersecting_flights = []

        # 获取所有具有至少两条记录的航班号
        flights_with_two_records = accumulated_data['RE'].value_counts()
        flights_with_two_records = flights_with_two_records[flights_with_two_records >= 1].index.tolist()

        # 遍历这些航班号
        for flight in flights_with_two_records:
            # 获取该航班号的最新两条记录
            flight_records = accumulated_data[accumulated_data['RE'] == flight].sort_values(by='UPDATE_TIME', ascending=False).head(1)

            # 提取经纬度
            lon, lat, he = flight_records.iloc[0][['LO', 'LA', 'HE']]
            # 提取经纬度
            current_coords = (lat, lon)

            # 计算到浦东国际机场的距离(km)
            distance_to_airport = geodesic(current_coords, pudong_airport_coords).kilometers
            # print(distance_to_airport)

            # 距离小于20km, 高度小于1500米
            if distance_to_airport < 20 and 1500 > flight_records.iloc[0]['HE'] > 600:
                new_time = flight_records.iloc[0]['UPDATE_TIME'] + timedelta(minutes=15)  # 到达时间为当前点对应的时间加15min
                if flight_records.iloc[0]['OA'] == 'PVG':  # 如果出发地点是PVG
                    intersecting_flights.append({'flightnum': flight, 'time': new_time, 'type': 'outbound', 'LA': lat, 'LO': lon, 'HE': he})
                else:
                    intersecting_flights.append({'flightnum': flight, 'time': new_time, 'type': 'inbound', 'LA': lat, 'LO': lon, 'HE': he})

        # # 浦东国际机场的坐标
        # pudong_airport_coords = (31.1445, 121.8050)
        #
        # # 每分钟执行一次
        # now = time
        # one_minute_ago = now - timedelta(minutes=1)
        #
        # # 读取CSV文件数据
        # df = ADSB_data
        #
        # # 转换'time'列为datetime类型
        # df['UPDATE_TIME'] = pd.to_datetime(df['UPDATE_TIME'])
        #
        # # 筛选出时间在过去1分钟的数据
        # accumulated_data = df[df['UPDATE_TIME'] >= one_minute_ago]
        #
        # # 如果没有新数据，跳过本次循环
        # if accumulated_data.empty:
        #     print(f"[{now}] 没有新数据。")
        # else:
        #     # 按航班'RE'和'UPDATE_TIME'排序
        #     accumulated_data = accumulated_data.sort_values(by=['RE', 'UPDATE_TIME'], ascending=[True, False])
        #     # 对每个航班'RE'保留一条记录
        #     accumulated_data = accumulated_data.groupby('RE').head(1).reset_index(drop=True)
        #     # print(accumulated_data['RE'].value_counts())
        #
        # # 创建一个空的列表来存储符合条件的航班号
        # intersecting_flights = []
        #
        # # 获取所有具有至少一条记录的航班号
        # flights_with_one_records = accumulated_data['RE'].value_counts()
        # flights_with_one_records = flights_with_one_records[flights_with_one_records >= 1].index.tolist()
        #
        # # 遍历这些航班号
        # for flight in flights_with_one_records:
        #     # 获取该航班号的最新记录
        #     flight_records = accumulated_data[accumulated_data['RE'] == flight].sort_values(by='UPDATE_TIME', ascending=False).head(1)
        #
        #     # 提取经纬度
        #     lon, lat = flight_records.iloc[0][['LO', 'LA']]
        #     current_coords = (lat, lon)
        #
        #     # 计算到浦东国际机场的距离(km)
        #     distance_to_airport = geodesic(current_coords, pudong_airport_coords).kilometers
        #     # print(distance_to_airport)
        #
        #     # 高度需要小于1500米
        #     if distance_to_airport < 15 and 600 < flight_records.iloc[0]['HE'] < 1000:
        #         new_time = flight_records.iloc[0]['UPDATE_TIME'] + timedelta(minutes=15)  # 到达时间为当前点对应的时间加15min
        #
        #         if flight_records.iloc[0]['OA'] == 'PVG':  # 如果出发地点是PVG
        #             intersecting_flights.append({'flightnum': flight, 'time': new_time, 'type': 'outbound'})
        #         else:
        #             intersecting_flights.append({'flightnum': flight, 'time': new_time, 'type': 'inbound'})

        return intersecting_flights

