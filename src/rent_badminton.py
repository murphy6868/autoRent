from getpass import getpass
import time, random, sys, os, copy
import multiprocessing
from multiprocessing import Pool
from rental_process import RentalProcess
from datetime import datetime, timedelta
import order_status
import utils, log_utils
import requests
L = log_utils.createLogger(__name__)

def doRent(rentArgs):
    y = rentArgs['y']
    m = rentArgs['m']
    d = rentArgs['d']
    rentHours = rentArgs['rentHours']
    rentCourtIDs = rentArgs['rentCourtIDs']
    random.shuffle(rentCourtIDs)
    credentials = rentArgs['credentials']
    proxy = rentArgs['proxy']

    rentalProcess = RentalProcess(credentials, proxy)
    for i in range(99999):
        for rentCourtID in rentCourtIDs:
            L.info(f"round {i}, Court {rentCourtID}")
            try:
                rentalProcess.rent(y, m, d, rentHours, rentCourtID)
                #rentalProcess.checkIP()
            except KeyboardInterrupt:
                L.warning("KeyboardInterrupt")
                return
            except Exception as e:
                L.warning(e)
        if i % 10 == 9:
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
    processNum = 50
    torSocksPorts = utils.startTorService(processNum)

    y, m, d = 2022, 11, 7


    # 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
    rentCourtIDs = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] 
    #rentCourtIDs = [5] 

    # 14,15,16   18,19,20   19,20,21
    rentHours = [19,20]
    #rentHours = [17]
    

    credentials = utils.getCredentials()
    
    print("y, m, d:", y, m, d)
    print("rentCourtIDs", rentCourtIDs)
    print("rentHours", rentHours)
    print("processNum", processNum)
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

    #doRent(rentArgs)
    #exit()

    inputs = []
    for i in range(processNum):
        rentArgs.update({"proxy": {"http": f"socks5://localhost:{torSocksPorts[i]}", 
                                    "https": f"socks5://localhost:{torSocksPorts[i]}"}})
        inputs.append(copy.deepcopy(rentArgs))

    pool = Pool(processNum)
    pool_outputs = pool.map(doRent, inputs)
    print(pool_outputs)

    



    
if __name__ == '__main__':
    
    main()