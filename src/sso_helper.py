from ast import Str
from bs4 import BeautifulSoup
import requests, sys, traceback
import logging, log_utils, utils
L = log_utils.createLogger(__name__, logging.DEBUG)

SSO_AUTH_URL = "https://adfs.ntu.edu.tw"
PE_MEMBER_URL = "https://rent.pe.ntu.edu.tw/member/"
PE_SSO_URL = "https://rent.pe.ntu.edu.tw/sso2_go.php"
NO_PROXY = {"http": "", "https": "",}

class SsoHelper():
    def __init__(self, credentials):
        self.credentials = credentials

    def __verifyToken(self, phpSessID):
        res = requests.get(PE_MEMBER_URL, headers={"Cookie":f"PHPSESSID={phpSessID}"})
        soup = BeautifulSoup(res.content, "html.parser")
        usernameFromMemberPage = soup.find("div", {"class": "Username"})
        if usernameFromMemberPage is None:
            return False
        L.debug(f"they think you're {usernameFromMemberPage.text}")
        L.info("Login finished!")
        return True

    def login(self, sess, rentDatetime=False):
        while(1):
            try:
                self.__try_login(sess, rentDatetime)
                return
            except KeyboardInterrupt:
                L.warning("KeyboardInterrupt")
                raise KeyboardInterrupt
            except Exception as e:
                L.warning(f"SSO login failed, retrying ... Exception: {e}")
                L.debug(traceback.format_exc())
        

    def __try_login(self, sess, rentDatetime=None):
        res = sess.get(PE_SSO_URL)
        L.debug(f"location: {res.headers['location']}")
        res = sess.get(res.headers['location'], proxies=NO_PROXY)

        soup = BeautifulSoup(res.content, "html.parser")
        payload = {}
        form = soup.find("form")
        payloadAction = form.get("action")
        inputs = form.find_all("input")
        if not inputs:
            return
        for ele in inputs:
            if "UsernameTextBox" in ele.get("name"):
                payload[ele.get("name")] = self.credentials.username
            elif "PasswordTextBox" in ele.get("name"):
                payload[ele.get("name")] = self.credentials.password
            else:
                payload[ele.get("name")] = ele.get("value")

        res = sess.post(SSO_AUTH_URL + payloadAction, data=payload, proxies=NO_PROXY)
        L.debug(f"location: {res.headers['location']}")
        res = sess.get(res.headers['location'], proxies=NO_PROXY)

        soup = BeautifulSoup(res.content, "html.parser")
        form = soup.find("form")
        L.debug(f"form.get('action'), {form.get('action')}")
        res = sess.post(
            form.get("action"),
            data={ele.get("name"): ele.get("value") for ele in form.find_all("input")}, allow_redirects=False
        )
        
        L.info(f"SSO Login Finished!")
        return