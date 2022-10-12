from getpass import getpass
import time
import multiprocessing
from multiprocessing import Pool
from rentalProcess import RentalProcess
import random

def doRent(rentArgs):
    y = rentArgs['y']
    m = rentArgs['m']
    d = rentArgs['d']
    rentHours = rentArgs['rentHours']
    rentCourtIDs = rentArgs['rentCourtIDs']
    random.shuffle(rentCourtIDs)
    credentials = rentArgs['credentials']

    rentalProcess = RentalProcess(credentials)
    # try:
    #     rentalProcess.SSOLogin()
    # except Exception as e:
    #     print(e)
    for i in range(10):
        time.sleep(random.random())
        for rentCourtID in rentCourtIDs:
            #rentalProcess.SSOLogin()
            #rentalProcess.rent(y, m, d, rentHours, rentCourtID)
            try:
                rentalProcess.rent(y, m, d, rentHours, rentCourtID)
            except KeyboardInterrupt:
                return
            except Exception as e:
                print(e)
        if i % 2 == 1:
            try:
                rentalProcess.refreshToken()
            except KeyboardInterrupt:
                return
            except Exception as e:
                print(e)
        if i % 10 == 9:
            try:
                rentalProcess.SSOLogin()
            except KeyboardInterrupt:
                return
            except Exception as e:
                print(e)
    return

def main():
    username = input("Username: ")
    print("Password: ")
    password = getpass()
    y, m, d = 2022, 10, 19
    rentHours = [12]
    rentCourtIDs = [1]
    credentials = {'username':username, 'password':password}
    rentArgs = {
        'y':y,
        'm':m,
        'd':d,
        'rentHours':rentHours,
        'rentCourtIDs':rentCourtIDs,
        'credentials':credentials
    }

    # rentalProcess = RentalProcess(credentials)
    # for i in range(1):
    #     for rentCourtID in rentCourtIDs:
    #         rentalProcess.SSOLogin()
    #         rentalProcess.rent(y, m, d, rentHours, rentCourtID)
    #         # try:
    #         #     rentalProcess.SSOLogin()
    #         #     rentalProcess.rent(y, m, d, rentHours, rentCourtID)
    #         # except Exception as e:
    #         #     print(e)
    # exit()


    processNum = multiprocessing.cpu_count() - 5
    #processNum = 5

    inputs = [rentArgs]*processNum
    pool = Pool(processNum)

    pool_outputs = pool.map(doRent, inputs)
    print(pool_outputs)

    



    
if __name__ == '__main__':
    
    main()