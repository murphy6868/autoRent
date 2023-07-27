import subprocess, psutil, time, requests, functools, random, json, os, tempfile, shutil, sys, shlex, aiohttp
from pathlib import Path
from datetime import datetime, timedelta
import multiprocessing  
import oyaml as yaml
from fake_useragent import UserAgent
import _dataclasses
import logging, log_utils
L = log_utils.createLogger(__name__, logging.DEBUG)
from collections import OrderedDict
PROJECT_ROOT_PATH = Path(__file__).parent.parent

TOR_PROXY = {'http': 'socks5://localhost:9050', 'https': 'socks5://localhost:9050'}
NO_PROXY = {"http": "", "https": "",}


def runAsDaemon(target, args):
    p = multiprocessing.Process(target=target, args=args, daemon=True)
    p.start()

def dump(s, fileName):
    path = PROJECT_ROOT_PATH.joinpath(fileName)
    with path.open('w') as f:
        f.write(str(s))

def dump_json(s):
    path = PROJECT_ROOT_PATH.joinpath('testing/dump_json.txt')
    with path.open('w') as f:
        json.dump(s, f)

from aiosocksy.connector import ProxyConnector, ProxyClientRequest
async def createAsyncSession():
    sess = aiohttp.ClientSession(connector=ProxyConnector(), request_class=ProxyClientRequest, headers={
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
        })
    sess.get = functools.partial(sess.get, allow_redirects = False)
    sess.post = functools.partial(sess.post, allow_redirects = False)
    return sess

def createSession(proxy = {}):
    sess = requests.session()

    sess.verify = False
    sess.request = functools.partial(sess.request, timeout = 20+random.random()*10)
    sess.get = functools.partial(sess.get, allow_redirects = False)
    sess.post = functools.partial(sess.post, allow_redirects = False)
    sess.proxies.update(proxy)
    ua = UserAgent()
    sess.headers.update(
        {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://rent.pe.ntu.edu.tw/member/?U=login",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Te": "trailers",
            "Connection": "close"
        }
    )
    return sess

def waitToRent(targetDate):
    L.info("waitToRent")
    startDate = targetDate + timedelta(days=-8, hours=23, minutes=59, seconds=45)
    pointOneSec = timedelta(milliseconds=100)
    while True:
        delta = startDate - datetime.now()
        if delta < pointOneSec:
            break
        print('  Wait for', str(delta)[:-7], 'to start at', startDate, end = '  \r')
        time.sleep(0.1)

def getCredentials() -> _dataclasses.Credentials:
    path = PROJECT_ROOT_PATH.joinpath("credentials.yaml")

    if path.exists():
        L.debug(f"loading credentials from {path}")
        credentials = _dataclasses.Credentials.from_yaml(path)
        L.info(f"credentials loaded - {credentials}")
        return credentials
    else:
        credentials = _dataclasses.Credentials.from_cli(path)
        L.info(f"credentials entered - {credentials}")
        return credentials

def getRentTasks():
    taskPath = PROJECT_ROOT_PATH.joinpath("tasks.yaml")
    if not taskPath.exists():
        L.error(f"missing - {taskPath}")
        exit()
    else:
        with taskPath.open('r') as f:
            tasks = yaml.safe_load(f)
        return tasks

def killTorService(ProcName = "tor"):
    for proc in psutil.process_iter():
        if proc.name() == ProcName:
            L.warning(f"killing {proc.pid}")
            proc.kill()

def runTorCMD(torCMD, my_env):
        p = subprocess.Popen(torCMD, env=my_env, stdout=subprocess.PIPE)
        while True:
            output = p.stdout.readline().decode("utf-8")
            if not output:
                break
            if '100%' in output:
                L.info(output)
            
 # Follow this link: http://blog.databigbang.com/distributed-scraping-with-multiple-tor-circuits/            
def startTorService(daemonNum, baseSocksPort=9052, RunAsDaemon=0):
    L.info(f"startTorService, daemonNum = {daemonNum}")
    
    tor_env = os.environ.copy()
    tor_env["PATH"] = "/tmp2/b04902071/tor-0.4.7.10/src/app/:" + tor_env["PATH"]

    torSocksPorts = []
    tempDir = Path('/tmp/torData')
    shutil.rmtree(tempDir, ignore_errors=True)
    tempDir.mkdir()
    
    for d in range(daemonNum):
        socksPort = baseSocksPort + d
        torSocksPorts.append(socksPort)
        torDataDirPath = tempDir.joinpath(f"tor{d}")
        torDataDirPath.mkdir()
        torCMD = f"tor --RunAsDaemon {RunAsDaemon} --PidFile {tempDir.as_posix()}/tor{d}.pid --SocksPort {socksPort} --DataDirectory {torDataDirPath}"
        torCMD = shlex.split(torCMD)
        L.debug(torCMD)
        runAsDaemon(runTorCMD, [torCMD, tor_env])
        
    return torSocksPorts
   

