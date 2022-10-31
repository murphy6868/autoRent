from ast import Str
from bs4 import BeautifulSoup
import requests, functools
import log_utils
L = log_utils.createLogger(__name__)

SSO_AUTH_URL = "https://adfs.ntu.edu.tw"
PE_MEMBER_URL = "https://rent.pe.ntu.edu.tw/member/"
PE_SSO_URL = "https://rent.pe.ntu.edu.tw/sso2_go.php"
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

    def refreshToken(self, phpSessID) -> str:
        if self.__verifyToken(phpSessID):
            return phpSessID
        else:
            return self.login()

    def login(self, sess, timeout=5) -> str:
        
        sess.request = functools.partial(sess.request, timeout=timeout)
        print(sess.headers)
        res = sess.get(PE_SSO_URL, verify=False)
        print(sess.headers)
        soup = BeautifulSoup(res.content, "html.parser")
        payload = {}
        form = soup.find("form")
        payloadAction = form.get("action")
        for ele in form.find_all("input"):
            if "UsernameTextBox" in ele.get("name"):
                payload[ele.get("name")] = self.credentials.username
            elif "PasswordTextBox" in ele.get("name"):
                payload[ele.get("name")] = self.credentials.password
            else:
                payload[ele.get("name")] = ele.get("value")

        res = sess.post(SSO_AUTH_URL + payloadAction, data=payload, verify=False)
        soup = BeautifulSoup(res.content, "html.parser")
        form = soup.find("form")
        res = sess.post(
            form.get("action"),
            data={ele.get("name"): ele.get("value") for ele in form.find_all("input")},
            verify=False
        )
        phpSessID = sess.cookies.get('PHPSESSID')
        self.__verifyToken(phpSessID)
        return phpSessID