from getpass import getpass
import time, random, sys, os
import multiprocessing
from multiprocessing import Pool
from rental_process import RentalProcess
from datetime import datetime, timedelta
import order_status
import utils
import log_utils
L = log_utils.createLogger(__name__)

def doRent(rentArgs):
    y = rentArgs['y']
    m = rentArgs['m']
    d = rentArgs['d']
    rentHours = rentArgs['rentHours']
    rentCourtIDs = rentArgs['rentCourtIDs']
    random.shuffle(rentCourtIDs)
    credentials = rentArgs['credentials']

    rentalProcess = RentalProcess(credentials)
    for i in range(999999999):
        time.sleep(random.random())
        for rentCourtID in rentCourtIDs:
            try:
                rentalProcess.rent(y, m, d, rentHours, rentCourtID)
            except KeyboardInterrupt:
                L.warning("KeyboardInterrupt")
                return
            except Exception as e:
                L.warning(e)
        if i % 2 == 1:
            try:
                rentalProcess.refreshToken()
            except KeyboardInterrupt:
                L.warning("KeyboardInterrupt")
                return
            except Exception as e:
                L.warning(e)
    return




def waitToRent(y, m, d):
    startDate = datetime(y,m,d,23,59,45) - timedelta(days=8)
    pointOneSec = timedelta(milliseconds=100)
    while True:
        delta = startDate - datetime.now()
        if delta < pointOneSec:
            break
        print('  Wait for', str(delta)[:-5], 'to start at', startDate, end = '  \r')
        time.sleep(1)

def main():
    
    y, m, d = 2022, 11, 8

    # 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    rentCourtIDs = [3,4,5,6,7,8,9,10,11,12,13,14,15] 

    # 14,15,16   19,20,21
    rentHours = [19,20,21] 

    credentials = utils.getCredentials()
    print("y, m, d:", y, m, d)
    print("rentCourtIDs", rentCourtIDs)
    print("rentHours", rentHours)
    waitToRent(y, m, d)
    
    rentArgs = {
        'y':y,
        'm':m,
        'd':d,
        'rentHours':rentHours,
        'rentCourtIDs':rentCourtIDs,
        'credentials':credentials
    }

    #utils.getRentTasks()
    #order_status.getOrderStatus(credentials)
    #exit()

    processNum = multiprocessing.cpu_count() * 2

    inputs = [rentArgs]*processNum
    pool = Pool(processNum)

    pool_outputs = pool.map(doRent, inputs)
    print(pool_outputs)

    



    
if __name__ == '__main__':
    
    main()