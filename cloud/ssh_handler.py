import base64
import paramiko
import subprocess
from paramiko.client import AutoAddPolicy


class SSHHandler():
    def __init__(self, ip:str):
        self.ip = ip
        self.client = paramiko.SSHClient()
        self.username = 'lpugens'
        self.client.set_missing_host_key_policy(AutoAddPolicy)

    def connect(self):
        self.client.load_system_host_keys()
        self.client.connect(self.ip, username=self.username)

    def send_bulk_files(self, files):
        command = f'scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r {files} {self.username}@{self.ip}:~/'
        print(f'$ {command}')
        result = subprocess.call(command, shell=True)
        print(result)

    def disconnect(self):
        self.client.close()

    def run(self, command:str):
        _, stdout, stderr = self.client.exec_command(command)
        print(f'$ {command}')
        self.__print_std(stdout, '...')
        self.__print_std(stderr, '!!!')
    
    def __print_std(self, stdout, prefix):
        for line in stdout:
            line = line.strip('\n')
            print(f'{prefix} {line}')
