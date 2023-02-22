
import log_utils, logging
import datetime
import time, random
import functools
import utils
from sso_helper import SsoHelper
L = log_utils.createLogger(__name__, log_level=logging.DEBUG)
import requests
requests.packages.urllib3.disable_warnings() 

from pypasser import reCaptchaV3

SSO_AUTH_URL = "https://adfs.ntu.edu.tw"
PE_MEMBER_URL = "https://rent.pe.ntu.edu.tw/member/"
PE_ORDER_URL = "https://rent.pe.ntu.edu.tw/order/ajax.php"
PE_URL = "https://rent.pe.ntu.edu.tw"
DEBUG_PROXIES = {'http': 'http://localhost:8888', 'https': 'http://localhost:8888'}

class RentalProcess:
    def __init__(self, credentials, proxy):
        self.ssoHelper = SsoHelper(credentials)
        self.sess = None
        self.proxy = proxy
        self.courtIDMap = {
            1:3,2:6,3:7,4:8,5:14,6:15,7:16,8:17,9:18,10:19,11:20,12:21,13:22,14:23,15:110
        }

    def __checkIP(self):
        r = self.sess.get("https://ifconfig.me/all.json")
        L.debug(f"using IP: {r.json()['ip_addr']}")
    
    def login(self):
        self.sess = utils.createSession(proxy = self.proxy)
        self.ssoHelper.login(self.sess)

    def rent(self, rentDatetime, rentHours, rentCourtID):
        rentCourtValue = self.courtIDMap[rentCourtID]
        rentCourtValueString = '"'+str(self.courtIDMap[rentCourtID])+'"'
        
        rentHoursString = "["
        for h in rentHours:
            rentHoursString += ( "\""+str(h).zfill(2)+"\"," )
        rentHoursString = rentHoursString[:-1] + "]"
        L.info("renting", rentCourtID, rentHoursString)

        rentUnixString = '"' + str(int(time.mktime(rentDatetime.timetuple()))) + '"'
        L.debug(f"rentUnixString: {rentUnixString}")

        
        URL = "https://rent.pe.ntu.edu.tw/order/?Add=A:2"
        r = self.sess.get(url = URL)
        L.debug(r)

        URL = "https://rent.pe.ntu.edu.tw/order/A/"
        r = self.sess.get(url = URL)
        L.debug(r)

        URL = "https://rent.pe.ntu.edu.tw/__/j/Rent.js?"
        currentTime = str(int(time.time()))
        PARAMS = {currentTime:''}
        r = self.sess.get(url = URL, params = PARAMS)
        L.debug(r)

        ScheduleJson = "{"+rentCourtValueString+":{"+rentUnixString+":"+rentHoursString + "}}"

        URL = "https://rent.pe.ntu.edu.tw/order/ajax.php"
        data = f"""Fun=RentScheduleHtml&ScheduleJson={ScheduleJson}"""
        L.debug(f"data: {data}")
        r = self.sess.post(url = URL, data = data)

        URL = "https://rent.pe.ntu.edu.tw/order/A/?"
        PARAMS = {'Step':'2'}
        data =  """Save=OK&TotalAmount=0&SubVenuesSN="""+str(rentCourtValue)+\
                """&MemberType[1]=4&MemberType[2]=&MemberType[3]=&MemberType[4]=&RentSchedule={"""+\
                rentCourtValueString+""":{"""+rentUnixString+""":"""+rentHoursString+"""}}"""
        L.debug(f"data: {data}")
        r = self.sess.post(url = URL, params = PARAMS, data = data)
        L.debug(r)

        
        reCaptcha_response = reCaptchaV3('https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LevhgkjAAAAAMR687KO0VI28xEMH0J8UggvAVPr&co=aHR0cHM6Ly9yZW50LnBlLm50dS5lZHUudHc6NDQz&hl=zh-TW&v=O4xzMiFqEvA4YhWjk5t8Xuas&size=invisible', timeout = 10)

        URL = "https://rent.pe.ntu.edu.tw/order/A/?"
        PARAMS = {'Step':'3'}
        data = f"""Save=OK&RecaptchaToken={reCaptcha_response}"""
        r = self.sess.post(url = URL, params = PARAMS, data = data)
        L.debug(r)
        r = self.sess.post(url = URL, params = PARAMS, data = data)
        L.debug(r)
        r = self.sess.post(url = URL, params = PARAMS, data = data)
        L.debug(r)



            
        