import json
import yaml

from dataclasses import dataclass, field
from datetime import datetime
from enum import auto, Enum
from getpass import getpass
from pathlib import Path


@dataclass
class Credentials:
    username: str = field()
    password: str = field(repr=False)

    @classmethod
    def from_cli(cls, path: Path):
        username = input("Username: ")
        password = getpass()
        credentials = {'username': username, 'password': password}
        with path.open('w') as yaml_file:
            yaml.safe_dump(credentials, yaml_file)
        return cls(username, password)

    @classmethod
    def from_yaml(cls, path: Path):
        with path.open('r') as yaml_file:
            credentials = yaml.safe_load(yaml_file)
            return cls(credentials["username"], credentials["password"])

@dataclass
class RentTasks:
    username: str = field()
    password: str = field(repr=False)