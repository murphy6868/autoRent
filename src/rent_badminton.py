from getpass import getpass
import time, random, sys, os, copy, pprint
import multiprocessing
from multiprocessing import Pool
from rental_process import RentalProcess
from datetime import datetime, timedelta
import order_status, gen_tasks, slack_bot_utils
import utils, log_utils, logging
import requests
L = log_utils.createLogger(__name__, log_level=logging.DEBUG)

def doRent(rentArgs):
    rentDatetime = rentArgs['rentDatetime']
    rentHours = rentArgs['rentHours']
    rentCourtIDs = rentArgs['rentCourtIDs']
    random.shuffle(rentCourtIDs)
    credentials = rentArgs['credentials']
    proxy = rentArgs['proxy']
    rentalProcess = RentalProcess(credentials, proxy)
    for i in range(99999):
        for rentCourtID in rentCourtIDs:
            L.info(f"round {i}, Court {rentCourtID}")
            # rentalProcess.rent(rentDatetime, rentHours, rentCourtID)
            try:
                rentalProcess.rent(rentDatetime, rentHours, rentCourtID)
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



def rent_badminton():

    #slack_bot_utils.sendQRCode(); exit()
    #slack_bot_utils.sendUnpaidOrder(); exit()

    credentials = utils.getCredentials()

    tasks = utils.getRentTasks()
    pools, tasks_inputs = [], []
    totalProcessNum = 0
    torSocksPort = 9052
    for i, task in enumerate(tasks):
        L.info(f"Task {i}:\n\t{task}")

        pools.append(Pool(task["processNum"]))
        totalProcessNum += task['processNum']

        task_inputs = []
        rentArgs = {
            'rentDatetime': datetime.strptime(task['date'], "%Y.%m.%d"),
            'rentHours': task['rentHours'],
            'rentCourtIDs': task['rentCourtIDs'],
            'credentials': credentials
        }
        for i in range(task["processNum"]):
            rentArgs.update({"proxy": {"http": f"socks5://localhost:{torSocksPort}", 
                                        "https": f"socks5://localhost:{torSocksPort}"}})
            task_inputs.append(copy.deepcopy(rentArgs))
            torSocksPort += 1
        tasks_inputs.append(task_inputs)

    torSocksPorts = utils.startTorService(totalProcessNum)
    

    for pool, task_inputs in zip(pools, tasks_inputs):
        utils.waitToRent(task_inputs[0]['rentDatetime'])
        pool.map_async(doRent, task_inputs)
    for pool in pools:
        L.info('Pray!')
        pool.close()
        pool.join()

    
if __name__ == '__main__':
    rent_badminton()