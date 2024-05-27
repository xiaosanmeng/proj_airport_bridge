from flights import *
from task import *
from aviation import *
from airports import *
from crew import *

def main():
    airport = airports()
    flights_path = './dataset/flights_obs.xlsx'
    aviation_path =  './dataset/new_aviationCompany.xlsx'
    airport.login(aviation_path,flights_path)

    while not airport.is_done():
        airport.step()
    airport.save_result()

if __name__ == '__main__':
    main()