import pandas as pd
import folium
from folium.plugins import BeautifyIcon
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors  # 正确导入颜色模块

# 1. 读取数据
# 请将 'flight_data.csv' 替换为你的CSV文件路径
data = pd.read_csv('../dataset/ADS-B/2024-09-17/2024-09-17_18.csv')
# 将 'TE' 列转换为日期时间格式
data['UPDATE_TIME'] = pd.to_datetime(data['UPDATE_TIME'])
data = data[(data['OA'] == 'PVG') | (data['DA'] == 'PVG')]

# 确保列名与数据一致，如果不一致，请修改以下列名
# 假设列名为：'LO'（经度），'LA'（纬度），'RE'（航班号），'TE'（时间）
# 如果列名不同，请相应调整
longitude = data['LO']
latitude = data['LA']
flight_numbers = data['RE']
times = data['UPDATE_TIME']

# 2. 初始化地图
# 以所有点的平均位置为地图中心
center_lat = latitude.mean()
center_lon = longitude.mean()

# 手动指定 'attr' 参数
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=5,
    tiles='Stamen Terrain',
    attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'
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

# 3. 生成不同航班的颜色
# 获取唯一的航班号
unique_flights = data['RE'].unique()
num_flights = len(unique_flights)

# 使用Matplotlib生成颜色映射
colors = plt.cm.get_cmap('hsv', num_flights)

# 创建航班颜色字典
flight_colors = {flight: mcolors.rgb2hex(colors(i)) for i, flight in enumerate(unique_flights)}

# 4. 按航班分组并绘制轨迹（添加图层控制）
for flight in unique_flights:
    flight_data = data[data['RE'] == flight].sort_values('TE')  # 按时间排序
    coords = flight_data[['LA', 'LO']].values.tolist()  # Folium使用 [纬度, 经度]

    # 创建一个图层
    flight_layer = folium.FeatureGroup(name=f'航班 {flight}')

    # 添加航班轨迹到图层
    folium.PolyLine(
        coords,
        color=flight_colors[flight],
        weight=2.5,
        opacity=1,
        popup=f'航班号: {flight}'
    ).add_to(flight_layer)

    # 添加起点和终点标记
    folium.Marker(
        location=coords[0],
        popup=f'起点 - 航班 {flight}',
        icon=folium.Icon(color='green', icon='plane', prefix='fa')
    ).add_to(flight_layer)

    folium.Marker(
        location=coords[-1],
        popup=f'终点 - 航班 {flight}',
        icon=folium.Icon(color='red', icon='plane', prefix='fa')
    ).add_to(flight_layer)

    # 添加图层到地图
    flight_layer.add_to(m)

# 5. 添加图例（可选）
legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 200px; height: auto; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white;
     padding: 10px;
     ">
     &nbsp;<b>航班颜色</b><br>
'''
for flight, color in flight_colors.items():
    legend_html += f'&nbsp;<i style="background:{color};width:10px;height:10px;float:left;margin-right:5px;"></i>{flight}<br>'
legend_html += '</div>'

m.get_root().html.add_child(folium.Element(legend_html))

# 6. 添加图层控制
folium.LayerControl().add_to(m)

# 7. 保存地图到HTML文件
m.save('flight_tracks_map.html')

print("地图已生成并保存为 'flight_tracks_map.html'")