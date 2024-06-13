from flights import *
from task import *
from aviation import *
from airports import *
from crew import *
import os
import shutil
import time
import streamlit as st


def logger(start,end):
    print('start:',start)
    print('end:',end)
    print('time:',end-start)
    print('=====================')
    path = './dataset/task_exec.xlsx'
    df = pd.read_excel(path)
    missing = df['People'].isnull().sum()
    print('缺失率', missing/len(df))

def show_crew(df_crew):
    st.write(df_crew)

def main():
    # 清空 crew 下的所有文件，'./dataset/crew/'
    st.title('系统仿真过程')
    start_time = time.time()
    print('======   Clear the crew folder   =======')
    if os.path.exists('./dataset/crew/'):
        shutil.rmtree('./dataset/crew/')
    # 新建 crew 文件夹
    os.mkdir('./dataset/crew/')
    airport = airports()
    flights_path = './dataset/flights_obs.xlsx'
    aviation_path =  './dataset/new_aviationCompany.xlsx'
    crew_zizhi_path = './dataset/人员资质证明.xlsx'
    crew_group_path = './dataset/人员组别.xlsx'
    gate_lounge_path = './dataset/Gate_lounge.xlsx'
    airport.login(aviation_path,flights_path,crew_zizhi_path,crew_group_path,gate_lounge_path)
    print('======   Start the simulation   =======')

    while not airport.is_done():
        data = airport.step() # 获取数据接口
        now = data['time']
        flights = data['flights']
        crew = data['crew']
        st.title('当前时间：{}'.format(now))
        show_crew(crew)


    print(airport.flightSet.index)

    end_time = time.time()
    airport.save_result()
    logger(start_time,end_time)

if __name__ == '__main__':
    main()