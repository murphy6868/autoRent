
import log_utils, logging
import datetime
import time, random
import functools
import utils
from sso_helper import SsoHelper
L = log_utils.createLogger(__name__, log_level=logging.INFO)
import requests
requests.packages.urllib3.disable_warnings() 


SSO_AUTH_URL = "https://adfs.ntu.edu.tw"
PE_MEMBER_URL = "https://rent.pe.ntu.edu.tw/member/"
PE_ORDER_URL = "https://rent.pe.ntu.edu.tw/order/ajax.php"
PE_URL = "https://rent.pe.ntu.edu.tw"
DEBUG_PROXIES = {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}

class RentalProcess:
    def __init__(self, credentials, proxy = {}):
        self.ssoHelper = SsoHelper(credentials)
        self.phpSessID = ""

        self.sess = utils.createSession(proxy = proxy)
        #self.sess = utils.createAsyncSession(proxy = proxy)

        self.courtIDMap = {
            1:3,2:6,3:7,4:8,5:14,6:15,7:16,8:17,9:18,10:19,11:20,12:21,13:22,14:23,15:110
        }

    def checkIP(self):
        r = self.sess.get("https://ifconfig.me/all.json")
        L.debug(f"using IP: {r.json()['ip_addr']}")

    def refreshToken(self):
        self.ssoHelper.login(self.sess)
        #self.phpSessID = self.ssoHelper.refreshToken(self.phpSessID, self.sess)


    def rent(self, rentDatetime, rentHours, rentCourtID):
        if self.phpSessID == "":
            self.phpSessID = self.ssoHelper.login(self.sess, rentDatetime)
        rentCourtValue = self.courtIDMap[rentCourtID]
        rentCourtValueString = '"'+str(self.courtIDMap[rentCourtID])+'"'
        
        rentHoursString = "["
        for h in rentHours:
            rentHoursString += ( "\""+str(h)+"\"," )
        rentHoursString = rentHoursString[:-1] + "]"
        print("renting", rentCourtID, rentHoursString)

        rentUnixString = '"' + str(int(time.mktime(rentDatetime.timetuple()))) + '"'

        URL = "https://rent.pe.ntu.edu.tw/order/?Add=A:2"
        r = self.sess.get(url = URL)
        L.debug(r.text)

        URL = "https://rent.pe.ntu.edu.tw/order/A/"
        r = self.sess.get(url = URL)
        L.debug(r.text)

        URL = "https://rent.pe.ntu.edu.tw/__/j/Rent.js?"
        currentTime = str(int(time.time()))
        PARAMS = {currentTime:''}
        r = self.sess.get(url = URL, params = PARAMS)
        L.debug(r.text)

        URL = "https://rent.pe.ntu.edu.tw/order/A/?"
        PARAMS = {'Step':'2'}
        data =  """Save=OK&TotalAmount=0&SubVenuesSN="""+str(rentCourtValue)+\
                """&MemberType[1]=4&MemberType[2]=&MemberType[3]=&MemberType[4]=&RentSchedule={"""+\
                rentCourtValueString+""":{"""+rentUnixString+""":"""+rentHoursString+"""}}"""
        r = self.sess.post(url = URL, params = PARAMS, data = data)
        L.debug(r.text)

        URL = "https://rent.pe.ntu.edu.tw/order/A/?"
        PARAMS = {'Step':'3'}
        data = """Save=OK"""
        r = self.sess.post(url = URL, params = PARAMS, data = data)
        L.debug(r.text)



            
        