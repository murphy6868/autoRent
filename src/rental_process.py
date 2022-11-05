
import log_utils, logging
import datetime
import time, random
import functools
import utils
from sso_helper import SsoHelper
L = log_utils.createLogger(__name__, log_level=logging.DEBUG)
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

        self.sess = requests.session()
        self.sess.verify = False
        self.sess.proxies.update(proxy)

        self.sess.request = functools.partial(self.sess.request, timeout = 5+random.random()*10)
        self.sess.get = functools.partial(self.sess.get, allow_redirects = False)
        self.sess.post = functools.partial(self.sess.post, allow_redirects = False)
        
        self.sess.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate",
                "Dnt": "1",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Te": "trailers",
                "Connection": "close",
            }
        )
        self.courtIDMap = {
            1:3,2:6,3:7,4:8,5:14,6:15,7:16,8:17,9:18,10:19,11:20,12:21,13:22,14:23,15:110
        }

    def checkIP(self):
        r = self.sess.get("https://ifconfig.me/all.json")
        L.debug(f"using IP: {r.json()['ip_addr']}")

    def refreshToken(self):
        self.phpSessID = self.ssoHelper.refreshToken(self.phpSessID)


    def rent(self, y, m, d, rentHours, rentCourtID):
        if self.phpSessID == "":
            self.phpSessID = self.ssoHelper.login(self.sess)
        rentCourtValue = self.courtIDMap[rentCourtID]
        rentCourtValueString = '"'+str(self.courtIDMap[rentCourtID])+'"'
        
        rentHoursString = "["
        for h in rentHours:
            rentHoursString += ( "\""+str(h)+"\"," )
        rentHoursString = rentHoursString[:-1] + "]"
        print("renting", rentCourtID, rentHoursString)

        rentDatetime = datetime.date(y, m, d)
        rentUnixString = '"' + str(int(time.mktime(rentDatetime.timetuple()))) + '"'
        #print("Unix_Time:", rentUnixString)
        

        URL = "https://rent.pe.ntu.edu.tw/order/?Add=A:2"
        r = self.sess.get(url = URL, allow_redirects=False)
        L.debug(r.text)

        URL = "https://rent.pe.ntu.edu.tw/order/A/"
        r = self.sess.get(url = URL, allow_redirects=False)
        L.debug(r.text)

        URL = "https://rent.pe.ntu.edu.tw/__/j/Rent.js?"
        currentTime = str(int(time.time()))
        PARAMS = {currentTime:''}
        r = self.sess.get(url = URL, params = PARAMS, allow_redirects=False)
        L.debug(r.text)

        URL = "https://rent.pe.ntu.edu.tw/order/A/?"
        PARAMS = {'Step':'2'}
        data =  """Save=OK&TotalAmount=0&SubVenuesSN="""+str(rentCourtValue)+\
                """&MemberType[1]=4&MemberType[2]=&MemberType[3]=&MemberType[4]=&RentSchedule={"""+\
                rentCourtValueString+""":{"""+rentUnixString+""":"""+rentHoursString+"""}}"""
        r = self.sess.post(url = URL, params = PARAMS, data = data, allow_redirects=False)
        L.debug(r.text)

        URL = "https://rent.pe.ntu.edu.tw/order/A/?"
        PARAMS = {'Step':'3'}
        data = """Save=OK"""
        r = self.sess.post(url = URL, params = PARAMS, data = data, allow_redirects=False)
        L.debug(r.text)


            
        