

import pandas as pd
import math
import time
from datetime import datetime, timedelta

EARTH_RADIUS_KM = 6371.0

# 上海浦东国际机场的经纬度
CENTER_LON  = 121.808603
CENTER_LAT  = 31.142363

# 圆的半径，单位：千米
CIRCLE_RADIUS_KM = 30.0

# 定义一个函数，将经纬度转换为以中心点为原点的平面坐标（单位：千米）
def latlon_to_xy(lon, lat, center_lon, center_lat):
    """
    将经纬度转换为以中心点为原点的平面坐标（单位：千米）
    """
    x = (lon - center_lon) * 111 * math.cos(math.radians(center_lat))
    y = (lat - center_lat) * 111
    return x, y

# 定义Haversine公式计算两点之间的距离
def haversine(lon1, lat1, lon2, lat2):
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
    distance_km = EARTH_RADIUS_KM * c
    return distance_km

# 定义函数，判断线段AB是否与圆相交
def line_circle_intersect(A, B, C, R):
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

# 主函数
def monitor_flight_data(input_file, output_file):
    # 上海浦东国际机场的经纬度
    CENTER_LON = 121.808603
    CENTER_LAT = 31.142363

    # 圆的半径，单位：千米
    CIRCLE_RADIUS_KM = 10.0

    """
        读取数据，筛选并判断航班连线是否与指定圆相交
    """
    # 读取CSV文件数据
    df = pd.read_csv(input_file)

    # 转换'time'列为datetime类型
    df['UPDATE_TIME'] = pd.to_datetime(df['UPDATE_TIME'])


    # 按航班'RE'和'UPDATE_TIME'排序，确保最新的记录在前
    df = df.sort_values(by=['RE', 'UPDATE_TIME'], ascending=[True, False])
    # df = df.sort_values(by=['RE'], ascending=[True])

    # 对每个航班'RE'保留最新的两条记录
    df = df.groupby('RE').head(2).reset_index(drop=True)
    print(df[df['RE'] == '9VSCG'])

    print(f"已更新累积数据，共有 {df['RE'].nunique()} 个航班。")

    # 创建一个空的列表来存储符合条件的航班号
    intersecting_flights = []

    # 获取所有具有至少两条记录的航班号
    flights_with_two_records = df['RE'].value_counts()
    flights_with_two_records = flights_with_two_records[flights_with_two_records >= 2].index.tolist()
    print(flights_with_two_records)

    accumulated_data2 = pd.DataFrame(
        columns=['ID', 'HK', 'LO', 'LA', 'HE', 'GV', 'CO', 'FN', 'FN2', 'RE', 'FT', 'OA', 'DA', 'TE', 'ETA',
                 'UPDATE_TIME', 'SR'])

    # 创建一个空的列表来存储符合条件的航班号
    intersecting_flights = []

    # 遍历这些航班号
    for flight in flights_with_two_records:
        # 获取该航班号的最新两条记录
        flight_records = df[df['RE'] == flight].sort_values(by='UPDATE_TIME', ascending=False).head(2)

        # 提取经纬度
        lon1, lat1 = flight_records.iloc[0][['LO', 'LA']]
        lon2, lat2 = flight_records.iloc[1][['LO', 'LA']]

        # 将经纬度转换为平面坐标
        A = latlon_to_xy(lon1, lat1, CENTER_LON, CENTER_LAT)
        B = latlon_to_xy(lon2, lat2, CENTER_LON, CENTER_LAT)
        C = (0, 0)  # 圆心在原点

        # 判断线段AB是否与圆相交
        if line_circle_intersect(A, B, C, CIRCLE_RADIUS_KM):
            intersecting_flights.append(flight)
            accumulated_data2 = pd.concat([accumulated_data2, flight_records])

    print(intersecting_flights)
    accumulated_data2.to_csv(output_file, index=False)

# 输入和输出文件路径
input_file = '../dataset/ADS-B/2024-09-17/2024-09-17_00.csv'
output_file = '../dataset/ADS-B/2024-09-17_00_output.csv'

monitor_flight_data(input_file, output_file)