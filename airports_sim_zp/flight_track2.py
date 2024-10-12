'''
1.航班的到达机场DA是PVG，
2.只展示航班落地前15分钟的轨迹以及落地之后的轨迹，
3.航班轨迹的颜色通过高度来表示，类似于高度的热力图
'''

import numpy as np
import pandas as pd
import folium
from folium.plugins import BeautifyIcon
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from branca.colormap import LinearColormap
from datetime import timedelta

# 1. 读取数据
data = pd.read_csv('../dataset/ADS-B/2024-09-17/2024-09-17_18.csv')

# 2. 数据预处理
# 将 'TE' 列转换为日期时间格式
data['TE'] = pd.to_datetime(data['TE'])

# 确保列名正确，如果不同，请相应调整
# 假设列名为：'LA'（纬度），'LO'（经度），'高度'（高度），'RE'（航班号），'TE'（时间），'OA'（出发机场），'DA'（到达机场）
required_columns = ['LA', 'LO', 'HE', 'RE', 'TE', 'OA', 'DA']
for col in required_columns:
    if col not in data.columns:
        raise ValueError(f"缺少必要的列: {col}")

# 3. 过滤到达机场为PVG的航班
pvg_flights = data[data['DA'] == 'PVG']

# 检查是否有符合条件的航班
if pvg_flights.empty:
    raise ValueError("没有到达机场为PVG的航班数据。")

# 4. 获取高度的最小值和最大值用于颜色映射（不包括高度为0的点）
height_data = pvg_flights[pvg_flights['HE'] > 0]['HE']
min_height = height_data.min()
max_height = height_data.max()

# 5. 创建颜色映射，使用'viridis'色图
# 将 RGBA 数组转换为十六进制颜色字符串
viridis = plt.cm.viridis(np.linspace(0, 1, 256))
viridis_hex = [mcolors.to_hex(c) for c in viridis]

colormap = LinearColormap(
    colors=viridis_hex,
    vmin=min_height,
    vmax=max_height,
    caption='高度 (m)'
)

# 6. 初始化Folium地图
# 以所有点的平均位置为中心
center_lat = pvg_flights['LA'].mean()
center_lon = pvg_flights['LO'].mean()
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=5,
    tiles=None  # 不使用默认瓦片
)

# 添加多个瓦片图层供选择
folium.TileLayer(
    'OpenStreetMap',
    name='OpenStreetMap',
    attr='© OpenStreetMap contributors'
).add_to(m)
folium.TileLayer(
    'Stamen Terrain',
    name='Stamen Terrain',
    attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
).add_to(m)
folium.TileLayer(
    'Stamen Toner',
    name='Stamen Toner',
    attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
).add_to(m)
folium.TileLayer(
    'Stamen Watercolor',
    name='Stamen Watercolor',
    attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
).add_to(m)
folium.TileLayer(
    'CartoDB Positron',
    name='CartoDB Positron',
    attr='© OpenStreetMap contributors, © CARTO'
).add_to(m)
folium.TileLayer(
    'CartoDB Dark_Matter',
    name='CartoDB Dark Matter',
    attr='© OpenStreetMap contributors, © CARTO'
).add_to(m)

# 添加颜色图例到地图
colormap.add_to(m)

# 7. 处理每个航班
unique_flights = pvg_flights['RE'].unique()

for flight in unique_flights:
    flight_data = pvg_flights[pvg_flights['RE'] == flight].sort_values('TE')

    # 检查是否有轨迹数据
    if len(flight_data) < 2:
        continue  # 跳过数据点少于2的航班

    # 找到落地时刻（高度为0）
    landing_data = flight_data[flight_data['HE'] == 0]
    if landing_data.empty:
        # 如果没有高度为0的数据，跳过该航班
        continue
    landing_time = landing_data['TE'].iloc[0]

    # 落地前15分钟的时间点
    start_time = landing_time - timedelta(minutes=15)

    # 提取落地前15分钟的轨迹
    pre_landing_data = flight_data[(flight_data['TE'] >= start_time) & (flight_data['TE'] <= landing_time)]

    # 提取落地后的轨迹（高度为0）
    post_landing_data = flight_data[flight_data['TE'] > landing_time]

    # 绘制落地前15分钟的轨迹
    if not pre_landing_data.empty and len(pre_landing_data) >= 2:
        pre_coords = pre_landing_data[['LA', 'LO', 'HE']].values.tolist()
        for i in range(len(pre_coords) - 1):
            point1 = pre_coords[i]
            point2 = pre_coords[i + 1]
            avg_height = (point1[2] + point2[2]) / 2
            color = colormap(avg_height)
            folium.PolyLine(
                locations=[(point1[0], point1[1]), (point2[0], point2[1])],
                color=color,
                weight=3,
                opacity=0.8,
                popup=f'航班号: {flight}<br>高度: {avg_height}'
            ).add_to(m)

    # # 绘制落地后的轨迹（高度为0，使用红色）
    # if not post_landing_data.empty and len(post_landing_data) >= 2:
    #     post_coords = post_landing_data[['LA', 'LO', 'HE']].values.tolist()
    #     for i in range(len(post_coords) - 1):
    #         point1 = post_coords[i]
    #         point2 = post_coords[i + 1]
    #         # 由于高度为0，使用固定颜色，例如红色
    #         folium.PolyLine(
    #             locations=[(point1[0], point1[1]), (point2[0], point2[1])],
    #             color='red',
    #             weight=3,
    #             opacity=0.8,
    #             popup=f'航班号: {flight}<br>高度: {point2[2]}'
    #         ).add_to(m)

    # # 可选：标记落地点
    # landing_point = landing_data.iloc[0]
    # folium.Marker(
    #     location=[landing_point['LA'], landing_point['LO']],
    #     popup=f'航班号: {flight} 落地',
    #     icon=folium.Icon(color='red', icon='plane', prefix='fa')
    # ).add_to(m)

# # 8. 添加出发机场和到达机场标记（可选）
# unique_OA = pvg_flights['OA'].unique()
# unique_DA = pvg_flights['DA'].unique()

# # 添加出发机场标记
# for oa in unique_OA:
#     oa_data = data[data['OA'] == oa].iloc[0]
#     folium.Marker(
#         location=[oa_data['LA'], oa_data['LO']],
#         popup=f'出发机场: {oa}',
#         icon=folium.Icon(color='green', icon='plane-departure', prefix='fa')
#     ).add_to(m)
#
# # 添加到达机场标记（这里到达机场都是PVG）
# for da in unique_DA:
#     da_data = data[data['DA'] == da].iloc[0]
#     folium.Marker(
#         location=[da_data['LA'], da_data['LO']],
#         popup=f'到达机场: {da}',
#         icon=folium.Icon(color='red', icon='plane-arrival', prefix='fa')
#     ).add_to(m)

# 9. 添加图层控制
folium.LayerControl().add_to(m)

# 10. 保存地图到HTML文件
m.save('flight_tracks_map_15min.html')

print("地图已生成并保存为 'flight_tracks_map_15min.html'")
