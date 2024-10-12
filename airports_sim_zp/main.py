import warnings
warnings.filterwarnings("ignore")

from flights import *
from task import *
from aviation import *
from airports import *
from crew import *
import os
import shutil
import time

def logger(start,end):
    print('start:',start)
    print('end:',end)
    print('time:',end-start)
    print('=====================')
    path = '../dataset/task_exec.xlsx'
    df = pd.read_excel(path)
    missing = df['People'].isnull().sum()
    print('缺失率', missing/len(df))

def main():
    df_temp = pd.read_csv('../dataset/work_time.csv')
    df_temp['min'] = 20
    df_temp['max'] = 35
    df_temp.to_csv('../dataset/work_time.csv')

    start_time = time.time()
    print('======   Clear the crew folder   =======')
    if os.path.exists('../dataset/crew/'):
        shutil.rmtree('../dataset/crew/')
    # 新建 crew 文件夹
    os.mkdir('../dataset/crew/')
    airport = airports()


    # # 全部航班数据
    # flights_path = '../dataset/flights_obs.xlsx'

    # 测试用数据
    # flights_path = './dataset/flights_obs_0217.xlsx'
    flights_path = '../dataset/flights_obs_0917_0923.xlsx'

    aviation_path =  '../dataset/new_aviationCompany.xlsx'

    crew_zizhi_path = '../dataset/人员资质证明.xlsx'
    crew_group_path = '../dataset/人员组别.xlsx'

    # # 全资质
    # crew_zizhi_path = '../dataset/人员资质证明-全资质.xlsx'
    # crew_group_path = '../dataset/人员组别-全资质.xlsx'

    # # +10%
    # crew_zizhi_path = '../dataset/人员资质证明+10%.xlsx'
    # crew_group_path = '../dataset/人员组别+10%.xlsx'

    # # -10%
    # crew_zizhi_path = '../dataset/人员资质证明-10%.xlsx'
    # crew_group_path = '../dataset/人员组别-10%.xlsx'

    # gate_lounge_path = './dataset/Gate_lounge.xlsx'
    gate_lounge_path = '../dataset/Gate_lounge_xy.xlsx' # 加入坐标
    # type_minNum_path = '../dataset/机型最小人员数.xlsx'
    type_minNum_path = '../dataset/机型最小人员数9月.xlsx'

    # begin = datetime.strptime("2024-09-16 23:59:00", "%Y-%m-%d %H:%M:%S")
    # end = datetime.strptime("2024-09-23 23:59:00", "%Y-%m-%d %H:%M:%S")

    '''
    没有使用ADSB数据
    '''
    # airport.login(aviation_path, flights_path, crew_zizhi_path, crew_group_path,gate_lounge_path,type_minNum_path)
    # print('======   Start the simulation   =======')
    #
    # while not airport.is_done():
    #     # data = airport.step()  # 启发式算法
    #     # data = airport.step_sim()  # 启发式算法
    #     data = airport.step_KM()  # KM算法
    #
    # print('完成的航班数：', airport.flightSet.index)
    # print('未完成的航班数', len(airport.flightSet.df_flights_left))
    # end_time = time.time()
    # airport.save_result()
    # logger(start_time, end_time)

    '''
    使用了ADSB数据
    '''
    airport.login_ADSB(aviation_path, flights_path, crew_zizhi_path, crew_group_path, gate_lounge_path,type_minNum_path)
    print('======   Start the simulation   =======')

    while not airport.is_done_ADSB():
        data = airport.step_ADSB()

    print('完成的航班数：', airport.flightSet.index)
    print('未完成的航班数', len(airport.flightSet.df_flights_left))
    end_time = time.time()
    airport.save_result()
    logger(start_time, end_time)


if __name__ == '__main__':
    main()