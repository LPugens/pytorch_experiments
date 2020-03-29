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

ssh_handler = SSHHandler('34.71.103.184')
ssh_handler.connect()
ssh_handler.run('bash -s < startup_enviornment.sh')
ssh_handler.disconnect()

# # key = paramiko.RSAKey(data=base64.b64decode(b'SHA256:ymyvLsqVjnfafJekBSHJrez+mPl6W1qOkDn7zfrzelw'))
# client = paramiko.SSHClient()
# client.set_missing_host_key_policy(AutoAddPolicy())
# # client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)
# client.connect('34.71.103.184', username='lpugens')
# stdin, stdout, stderr = client.exec_command('lks -a')
# for line in stdin:
#     print('$ ' + line.strip('\n'))

# for line in stdout:
#     print('... ' + line.strip('\n'))

# for line in stderr:
#     print('!!! ' + line.strip('\n'))
    
# client.close()