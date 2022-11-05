from pathlib import Path
import yaml, subprocess, psutil
import _dataclasses
import log_utils
L = log_utils.createLogger(__name__)

PROJECT_ROOT_PATH = Path(__file__).parent.parent

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
    samplePath = PROJECT_ROOT_PATH.joinpath("sample_tasks.yaml")
    if not taskPath.exists():
        L.error(f"missing - {taskPath}")
        rentTasks = []
        rentTask = {
            "date" : "2022/10/31",
            "rentHours" : "8,9,10",
            "rentCourtIDs" : "1,2,3"
        }
        rentTasks.append(rentTask)
        rentTask = {
            "date" : "2022/10/30",
            "rentHours" : "9,10",
            "rentCourtIDs" : "4,5,6",
        }
        rentTasks.append(rentTask)
        with samplePath.open('w') as f:
            f.write(yaml.safe_dump(rentTasks))

def startTorService(daemonNum, baseSocksPort=9050):
    torPath = PROJECT_ROOT_PATH.joinpath("tor")

    pidPaths = torPath.glob("*.pid")
    for pidPath in pidPaths:
        with pidPath.open('r') as f:
            pid = int(f.read())
        if psutil.pid_exists(pid):
            process = psutil.Process(pid)
            process_name = process.name()
            if process_name == "tor":
                process.kill()
                print(pid, "killed")

    torPath.mkdir(parents=True, exist_ok=True)
    torSocksPorts = []
    for d in range(daemonNum):
        socksPort = baseSocksPort + d
        torSocksPorts.append(socksPort)
        torDataPath = torPath.joinpath(f"tor{d}")
        p = subprocess.Popen([  "tor", "--RunAsDaemon", "0", 
                                "--PidFile", f"{torPath.as_posix()}/tor{d}.pid", 
                                "--SocksPort", str(socksPort), 
                                "--DataDirectory", torDataPath.as_posix()])
    return torSocksPorts
    # Follow this link: http://blog.databigbang.com/distributed-scraping-with-multiple-tor-circuits/