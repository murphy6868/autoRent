import requests
requests.packages.urllib3.disable_warnings() 
import functools
from bs4 import BeautifulSoup
from sso_helper import SsoHelper
def getOrderStatus(credentials):
    sess = requests.session()
    sess.verify = False
    sess.request = functools.partial(sess.request, timeout=5)
    sess.headers.update(
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
    ssoHelper = SsoHelper(credentials)
    ssoHelper.login(sess)
    pageNum = 0
    orders = ""
    while(1):
        pageNum += 1
        URL = f"https://rent.pe.ntu.edu.tw/member/rental/?TOS=%E5%B7%B2%E6%A0%B8%E5%87%86&TPS=%E5%BE%85%E7%B9%B3%E8%B2%BB&Page={pageNum}"
        PARAMS = {}
        res = sess.get(url = URL, params = PARAMS)
        soup = BeautifulSoup(res.content, "html.parser")
        tbodies = soup.find_all("tbody")
        if len(tbodies) == 0:
            break
        for tbody in tbodies:
            OrderNo = tbody.find("div", {"class": "MC OrderNo"}).text
            CreateDate = tbody.find("div", {"class": "CreateDate"}).text
            RD = tbody.find("span", {"class": "RD"}).text
            RT = tbody.find("span", {"class": "RT"}).text
            TotalAmount = tbody.find("div", {"class": "MC TotalAmount"}).text
            print(OrderNo, CreateDate, RD, RT, TotalAmount)
            orders+= '\n' + " ".join([OrderNo, CreateDate, RD, RT, TotalAmount])
    print(orders)


    