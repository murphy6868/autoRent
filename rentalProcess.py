import requests
from typing import Dict
from bs4 import BeautifulSoup
import logging as L
import datetime
import time
import functools

L.basicConfig(format="%(levelname)s : %(message)s", level=L.DEBUG)
requests.packages.urllib3.disable_warnings() 

class RentalProcess:
    def __init__(self, credentials):
        self.credentials = credentials
        self.sess = requests.session()
        self.sess.request = functools.partial(self.sess.request, timeout=5)
        self.sess.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
            }
        )
        self.PE_SSO_URL = "https://rent.pe.ntu.edu.tw/sso2_go.php"
        self.SSO_AUTH_URL = "https://adfs.ntu.edu.tw"
        self.PHPSESSID = ""
        self.PE_MEMBER_URL = "https://rent.pe.ntu.edu.tw/member/"
        self.PE_ORDER_URL = "https://rent.pe.ntu.edu.tw/order/ajax.php"
        self.PE_URL = "https://rent.pe.ntu.edu.tw"
        self.courtIDMap = {
            1:3,2:6,3:7,4:8,5:14,6:15,7:16,8:17,9:18,10:19,11:20,12:21,13:22,14:23,15:110
        }
    def __verifyToken(self):
        res = requests.get(self.PE_MEMBER_URL, headers={"Cookie":f"PHPSESSID={self.PHPSESSID}"})
        soup = BeautifulSoup(res.content, "html.parser")
        usernameFromMemberPage = soup.find("div", {"class": "Username"})
        if usernameFromMemberPage is None:
            raise False
        L.debug(f"RentalProcess.SSOLogin - they think you're {usernameFromMemberPage.text}")
        L.info("RentalProcess.SSOLogin - Login finished!")
        return True

    def refreshToken(self):
        if self.__verifyToken():
            return True
        self.SSOLogin()

    def SSOLogin(self):
        self.sess.cookies.clear()
        res = self.sess.get(self.PE_SSO_URL, verify=False)
        soup = BeautifulSoup(res.content, "html.parser")
        payload = {}
        form = soup.find("form")
        payloadAction = form.get("action")
        for ele in form.find_all("input"):
            if "UsernameTextBox" in ele.get("name"):
                payload[ele.get("name")] = self.credentials['username']
            elif "PasswordTextBox" in ele.get("name"):
                payload[ele.get("name")] = self.credentials['password']
            else:
                payload[ele.get("name")] = ele.get("value")

        res = self.sess.post(self.SSO_AUTH_URL + payloadAction, data=payload, verify=False)
        soup = BeautifulSoup(res.content, "html.parser")
        form = soup.find("form")
        res = self.sess.post(
            form.get("action"),
            data={ele.get("name"): ele.get("value") for ele in form.find_all("input")}
        )
        self.PHPSESSID = self.sess.cookies.get('PHPSESSID')
        self.__verifyToken()

    def rent(self, y, m, d, rentHours, rentCourtID):
        if self.PHPSESSID == "":
            self.SSOLogin()
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
        r = self.sess.get(url = URL)

        URL = "https://rent.pe.ntu.edu.tw/order/A/"
        r = self.sess.get(url = URL)

        URL = "https://rent.pe.ntu.edu.tw/__/j/Rent.js?"
        currentTime = str(int(time.time()))
        PARAMS = {currentTime:''}
        r = self.sess.get(url = URL, params = PARAMS)

        URL = "https://rent.pe.ntu.edu.tw/order/A/?"
        PARAMS = {'Step':'2'}
        data = """Save=OK&TotalAmount=0&SubVenuesSN="""+str(rentCourtValue)+"""&MemberType[1]=4&MemberType[2]=&MemberType[3]=&MemberType[4]=&RentSchedule={"""+rentCourtValueString+""":{"""+rentUnixString+""":"""+rentHoursString+"""}}"""
        r = self.sess.post(url = URL, params = PARAMS, data = data)

        URL = "https://rent.pe.ntu.edu.tw/order/A/?"
        PARAMS = {'Step':'3'}
        data = """Save=OK"""
        r = self.sess.post(url = URL, params = PARAMS, data = data)


            
        