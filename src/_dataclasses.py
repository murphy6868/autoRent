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
    slackBotOAuthToken: str = field(repr=False)

    @classmethod
    def from_yaml(cls, path: Path):
        with path.open('r') as f:
            credentials = yaml.safe_load(f)
            return cls(credentials['username'], credentials['password'], credentials['slackBotOAuthToken'])

@dataclass
class RentTasks:
    username: str = field()
    password: str = field(repr=False)