from keep_alive import keep_alive
import os
from pathlib import Path
import utils
SERVER_DIR = Path(__file__).parent
# cert_pem = SERVER_DIR.joinpath('cert.pem')
# key_pem  = SERVER_DIR.joinpath('key.pem')

cert = SERVER_DIR.joinpath('certificate.crt')
ca_certs = SERVER_DIR.joinpath('ca_bundle.crt')
key  = SERVER_DIR.joinpath('private.key')


def genCertificate():
    os.system(f"openssl req -x509 -newkey rsa:4096 -nodes \
                -out {cert.as_posix()} -keyout {key.as_posix()} -days 365")

if __name__ == '__main__':
    #utils.killTorService()
    utils.startTorService(1, baseSocksPort=9050, RunAsDaemon=1)
    os.system(f"gunicorn --certfile {cert.as_posix()} --keyfile {key.as_posix()} --ca-certs {ca_certs.as_posix()} \
               -b 0.0.0.0:8443 'src.slack_bot_server.keep_alive:app' --log-level debug --timeout 120")
