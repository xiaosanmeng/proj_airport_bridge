# 机场 廊桥人员派工项目

## 快速使用

```
# 以下操作均在项目文件夹运行
python airports_sim/main.py # 开发版本 + 是否可以正常运行的版本
streamlit run airports_sim/main_visual.py # 开发版本 + 原始的可视化页面
streamlit run airports_sim/main_demo.py # 开发版本+可操控按钮可视化页面

streamlit run airports_sim_zp/main_demo.py # 展示版本+可操控按钮可视化页面
```



## 项目背景

Milestone 🌟🌟

2024-10-12 完成 zhoupeng 算法模块的嵌入，综合最近算法、ADSB 时间触发、面向业务需求的可视化代码



---

本项目主要面向浦东机场项目廊桥派工仿真项目，基于仿真技术配合匹配算法完成勤务人员的匹配工作，主要参考沈老师的《0317 机场派工逻辑》
<img src="https://chenxia31blog.oss-cn-hangzhou.aliyuncs.com/img/20240527110732.png" alt="沈老师派工逻辑梳理示意图" style="zoom: 25%;" />

### 仿真数据说明

位于项目根目录下 /dataset 文件夹中，主要包括：


固定数据
1. 人员组别
2. 人员资质说明
3. Gate_lounge 航站楼和登机口
4. new_aviationComnpany 航司对应的勤务需求

运营数据
1. 机务维修中心出港 2 月
2. 机务维修中心进港 2 月
3. 观测航班信息.xlsx; 在上述信息上提取的规则数据
4. 机型最小人员数;更新在最新的表格

额外新增的数据

- 【Zhoupeng 增加的数据】
- './dataset/flights_obs_0917_0923.xlsx' 新观察到的航班数据
- './dataset/Gate_lounge_xy.xlsx' 增加位置信息的机场近机位数据
- ADS-B 数据文件夹

### 仿真流程说明

【最新的和 zhoupeng 重建的算法带来放在 airports_sim_zp中】

- airports_sim_zp
- data 文件夹中新增 ADS_B 数据获取

【最初始的仿真流程再 airports_sim 文件夹中】

仿真过程的类整理在根目录 /airports_sim 文件夹中，其中文件作用包括

aviation.py
1. aviationCompany 航司公司类
2. ACSets 航司集合类

flights.py
1. fligths 单个航班类
2. flights set 集合航班类

crew.py
1. crew 主要是面向勤务人员操作

task.py
1. task 任务类，用于描述任务的时间、地点和任务属性,包括任务的持续时间
2. taskSet 任务集合类，方便后续操作

airports.py
1. operator 根据观察的勤务需求和空闲人员完成匹配
2. airports 函数仿真的主要逻辑，通过调用上述的类别，在时间线的步骤下，按照 flights 生成对应的航班，并根据 aviation 产生对应的 task，并调用 crew 的召回算法来获取当前的空闲人员，引入 operator 后完成两者的最优匹配。根据识别的结果来完成状态更新。

![仿真算法流程](https://chenxia31blog.oss-cn-hangzhou.aliyuncs.com/img/20240527112840.png)

### 待办事项
1. 将现实任务的时间替换现有的随机时间,task.get_task_duration
2. 更新匹配算法 ，airports.operator.match_algorithm


### 匹配算法思路
这部分主要由 zp 复杂，期望主导引入 TRB 论文，前期调研可行的匹配算法包括：
1. 基于规则的FIFO规则算法
2. 匈牙利匹配算法
3. 更优秀的二分图匹配算法，KM 匹配、GS 匹配等
4. MDP 动态时空价值匹配，基于未来状态的匹配算法

![可能的匹配算法思路](https://chenxia31blog.oss-cn-hangzhou.aliyuncs.com/img/20240527112739.png)

### 结果输出

生成的可行执行过程存储在 task-exec 文件中，完成匹配个数和工作时间的关系
![匹配算法缺失](https://chenxia31blog.oss-cn-hangzhou.aliyuncs.com/img/20240607123540.png)

### 如何修改本项目

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
4. Save the modfied(`'git add .'`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 版本控制

该项目使用Git进行版本管理。您可以在repository参看当前可用版本。

### 附录
### 算法说明
已经实现的功能包括

- AviationCompany() 航空公司
    - generate-time-task（time，location） 生成任务
    - update from row 更新航空公司
- ACSets() 航空公司集合
    - login 从数据中生成仿真
    - get_aviation from id 从代码获取航司信息
    - create task 根据代码生成航司对应的任务
    - get company coding ID 获取编码列表
- Crew 地勤人员集合
    - login 从数据中生成机组人员
    - **get near1 people 找到空闲的，同时处于对应1/4 terminal**
    - **get near2 people 找到空闲的，同时处于所有terminal的**
    - **get near3 people 找到即将完成任务的**
    - **_update people status 更新人员的状态**
- FlightsSet()
    - login 从数据中生成航班对应的任务
    - filter by id 根据航司信息获取航班id
    - get begin time 获取航班的开始时间
    - get near flights 获取最近的航班信息
    - is done 判断列表是否完成
- Task()
    - get-task-description 获取任务描述
    - get task duration 获取任务的持续时间
- Task set()
    - add task() 增加新的任务
- Airports（）
    - login() ，同时注册上述的机组人员、航班信息、terminal信息
    - get margin flights 获取最近的航班
    - generation task 从航班信息中获取time、location和id，由此生成任务
    - get terminal 获取登机口对应的terminal
    - step 更新函数，每一分钟更新
        - 获取需要添加的航班
        - **生成任务列表  # 应该是保留所有待办的任务清单，和对应的人员完成指派**
        - **获取对应的空闲人员 # 应该是获取所有空闲的人员，完成对应的任务的指派**
        - 完成人员和任务的指派问题
        - **更新任务和人员的状态 # 可能存在当前时间步骤没有完成任务**
    - is done 完成任务的更新
- Operator() 调度

    - match algorithm 完成任务集合和人员集合的匹配

![image](https://github.com/Yshen-group/proj_airport_bridge/assets/72689497/b499c788-4797-47c0-b1b3-2305e59e6025)

2024-03-28 整理，相关class整理在 /airports_sim 文件夹下面
mian py中首先注册航班信息、航司信息、人员信息，之后在有航班的情况下，不断的按照分钟来进行。

- task 任务类，task set 任务集合；其中任务由航司生成
- flights 单个航班类，flights 航司集合类
- aviation和acsets类，包括航司类，航司集合类，用于提供航司信息，和单独航司的任务生成
- crew类，用于筛选不同类别和不同组别的勤务人员
- airport 类，用于整体model的更新和终点条件的判断
    - 状态更新，获取当前的最近航班
    - 记录当前航班的任务
    - 召回附近的人员类别
    - 利用match算法为任务分配对应的人员
- operator类，用于匹配算法的整理

后续TODO
- 优化任务和任务类的表达，提升任务的获取和匹配获取接口
- 统一任务列表表达，其中单个航班的不同任务之间具有出入（一般、耳机、放行、廊桥等）
- 完成匹配分配之后，勤务人员的状态更新、回收函数的撰写
- 简单匹配算法的优化


### 结果展示

一个是基于 streamlit 的基本的可视化模板
一个是基于 streamlit 和交互页面的可视化模板，增加新的
- 开始
- 恢复
- 回到上一个状态
- 重新排列的多个阶段

### 如何参与开源项目

贡献使开源社区成为一个学习、激励和创造的绝佳场所。你所作的任何贡献都是**非常感谢**的。


1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 版本控制

该项目使用Git进行版本管理。您可以在repository参看当前可用版本。

