import base64
import paramiko
from paramiko.client import AutoAddPolicy


class SSHHandler():
    def __init__(self, ip:str):
        self.ip = ip
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy)

    def connect(self):
        self.client.connect(self.ip, username='lpugens')

    def disconnect(self):
        self.client.close()

    def run(self, command:str):
        _, stdout, stderr = self.client.exec_command(command)
        print(f'$ {command}')
        for line in stdout:
            print('... ' + line.strip('\n'))

        for line in stderr:
            print('!!! ' + line.strip('\n'))
