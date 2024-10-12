import pandas as pd
import math

# 地球半径，单位：千米
EARTH_RADIUS_KM = 6371.0

# 计算两点之间的Haversine距离
def haversine(lon1, lat1, lon2, lat2):
    # 将角度转换为弧度
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # 计算经度和纬度差值
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine公式
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 返回两点之间的距离，单位：千米
    distance_km = EARTH_RADIUS_KM * c
    return distance_km

# 筛选经纬度位于指定圆内的数据
def filter_data_within_circle(input_file, output_file, center_lon, center_lat, radius_km):
    # 读取表格
    df = pd.read_csv(input_file)

    # 初始化一个列表来存储筛选结果
    filtered_data = []

    # 遍历表格中的每一行，计算与中心点的距离
    for index, row in df.iterrows():
        lon = row['LO']
        lat = row['LA']

        # 计算当前点与圆心的距离
        distance = haversine(lon, lat, center_lon, center_lat)

        # 如果距离小于等于半径，保存数据
        if distance <= radius_km:
            filtered_data.append(row)

    # 将筛选后的数据转换为DataFrame
    filtered_df = pd.DataFrame(filtered_data)

    # 输出结果到新的CSV文件
    filtered_df.to_csv(output_file, index=False)
    print(f"筛选结果已保存为 {output_file}")

# 圆心坐标
center_lon = 121.808603
center_lat = 31.142363

# 圆的半径，单位：千米
radius_km = 30.0

# 输入和输出文件路径
input_file = '../dataset/ADS-B/2024-09-17/2024-09-17_00.csv'
output_file = '../dataset/ADS-B/2024-09-17_00_output.csv'

# 调用函数筛选数据并输出
filter_data_within_circle(input_file, output_file, center_lon, center_lat, radius_km)
