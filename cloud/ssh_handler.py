import base64
import paramiko
import subprocess
from paramiko.client import AutoAddPolicy


class SSHHandler():
    def __init__(self, ip:str):
        self.ip = ip
        self.client = paramiko.SSHClient()
        self.username = 'lpugens'
        self.log_file = 'ssh_log.txt'
        self.client.set_missing_host_key_policy(AutoAddPolicy)

    def connect(self):
        self.client.connect(self.ip, username=self.username)
        open(self.log_file, 'w').close()

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
        self.__print_std(stdout, f'({command}) ...', True)
        self.__print_std(stderr, f'({command}) !!!', False)
    
    def __print_std(self, stdout, prefix, show_inputs):
        for line in stdout:
            line = line.strip('\n')
            if not show_inputs and line.startswith('+ '):
                continue
            print(f'{prefix} {line}')
