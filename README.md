# autoRent

## Requirements
- python3.9+
- tor
- gunicorn

## Installation

- Python packages: `pipenv sync` or `pip3 install -r requirements.txt`

## Configuration
- Add credentials.yaml (see [sample_credentials.yaml](sample_credentials.yaml))

## Usage 1 - Rent courts
Edit [tasks.yaml](tasks.yaml) (see [sample_tasks.yaml](sample_tasks.yaml))

```
python3 src/main.py
```
## Usage 2 - Start Slack bot server
Start Tor service on 127.0.0.1:9050
```
python3 src/slack_bot_server/main.py
```
