from pathlib import Path
import yaml
import _dataclasses
import log_utils
L = log_utils.createLogger(__name__)

ROOT_PATH = Path(__file__).parent.parent

def getCredentials() -> _dataclasses.Credentials:
    path = ROOT_PATH.joinpath("credentials.yaml")

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
    task_path = ROOT_PATH.joinpath("tasks.yaml")
    sample_path = ROOT_PATH.joinpath("sample_tasks.yaml")
    if not task_path.exists():
        L.error(f"missing - {task_path}")
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
        with sample_path.open('w') as yaml_file:
            yaml_file.write(yaml.safe_dump(rentTasks))
