import os
import time
import sys, traceback


import googleapiclient.discovery

from typing import List
from threading import Thread, Lock
from functools import partial
from cloud.ssh_handler import SSHHandler

class VirtualMachine():
    def __init__(self, name:str, project: str, zone:str, machine_type: str, use_gpu: bool, verbose: bool = False):
        self.alive = False
        self.project = project
        self.name = name
        self.zone = zone
        self.machine_type = machine_type
        self.use_gpu = use_gpu
        self.ip = None
        self.ssh_enabled = False
        self.last_ssh_up_position = None
        self.verbose = verbose
        self.logger = VirtualMachineSerialLogger(name, project, zone, verbose)
        self.compute = googleapiclient.discovery.build('compute', 'v1')

    def instantiate(self, bucket, repository):
        image_response = self.compute.images().getFromFamily(project='gce-uefi-images', family='ubuntu-1804-lts').execute()
        source_disk_image = image_response['selfLink']

        # Configure the machine
        machine_type = f"zones/{self.zone}/machineTypes/{self.machine_type}"
        # startup_script = open(os.path.join(os.path.dirname(__file__), 'run.sh'), 'r').read()

        config = {
            'name': self.name,
            'machineType': machine_type,

            "scheduling": {
                "onHostMaintenance": 'terminate',
                "automaticRestart": False
            },

            # Specify the boot disk and the image to use as a source.
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    "diskSizeGb": '50',
                    'diskType': f'https://www.googleapis.com/compute/v1/projects/{self.project}/zones/{self.zone}/diskTypes/local-ssd',
                    'initializeParams': {
                        'sourceImage': source_disk_image,
                    }
                }
            ],

            # Specify a network interface with NAT to access the public
            # internet.
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],

            # Allow the instance to access cloud storage and logging.
            'serviceAccounts': [{
                'email': 'default',
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_write',
                    'https://www.googleapis.com/auth/logging.write'
                ]
            }]
        }

        if self.use_gpu:
            config["guestAccelerators"] = [
                {
                "acceleratorType": f'projects/{self.project}/zones/{self.zone}/acceleratorTypes/nvidia-tesla-k80',
                "acceleratorCount": 1
                }
            ],

        operation = self.compute.instances().insert(
            project=self.project,
            zone=self.zone,
            body=config).execute()

        operation_result = wait_completion(self.compute, self.project, self.zone, operation)
        
        self.logger.start_log()

        if 'error' in operation_result:
            raise Exception(operation_result['error'])
        
        timeout = 60
        t0 = time.time()
        while self.ip is None:
            if time.time() - t0 > timeout:
                raise TimeoutError(f'The server IP was not available in less than {timeout}s')
            try:
                instance_info = self.compute.instances().list(project=self.project, zone=self.zone, filter=f'name:{self.name}').execute()
                self.ip = instance_info['items'][0]['networkInterfaces'][0]['accessConfigs'][0]['natIP']
            except Exception as _:
                pass
        print(self.ip)

        return operation

    def reboot(self):
        print(f'REBOOTING VM')
        self.wait_ssh_up()

        ssh_handler = SSHHandler(self.ip)
        ssh_handler.connect()
        ssh_handler.run('sudo reboot now')
        ssh_handler.disconnect()

        self.ssh_enabled = False
        self.wait_ssh_up()

    def delete(self):
        operation = self.compute.instances().delete(
            project=self.project,
            zone=self.zone,
            instance=self.name).execute()

        operation_result = wait_completion(self.compute, self.project, self.zone, operation)

        if 'error' in operation_result:
            raise Exception(operation_result['error'])

        self.logger.stop_log()

        return operation
    
    def send_files(self, path:str):
        print(f'SENDING {path}')
        self.wait_ssh_up()

        ssh_handler = SSHHandler(self.ip)
        ssh_handler.connect()
        ssh_handler.send_bulk_files(path)
        ssh_handler.disconnect()

    def run_command(self, script: str):
        print(f'RUNNING {script}')
        self.wait_ssh_up()

        ssh_handler = SSHHandler(self.ip)
        ssh_handler.connect()
        ssh_handler.run(script)
        ssh_handler.disconnect()

    def wait_ssh_up(self):
        print('Waiting SSH server to start...')
        t0 = time.time()
        started_string = 'INFO Finished running startup scripts.'
        while not self.ssh_enabled:
            if time.time() - t0 > 60*10:
                raise TimeoutError('Server took too long to start SSH service')
            if self.last_ssh_up_position is None:
                ssh_up_position = open('log.txt', 'r').read().find(started_string)
            else:
                ssh_up_position = open('log.txt', 'r').read().find(started_string, self.last_ssh_up_position+1)

            if ssh_up_position > 0:
                self.ssh_enabled = True
                self.last_ssh_up_position = ssh_up_position
            else:
                self.ssh_enabled = False
            time.sleep(1)


class VirtualMachineSerialLogger():
    def __init__(self, name, project, zone, verbose):
        self.name = name
        self.project = project
        self.zone = zone
        self.log = False
        self.thread = None
        self.log_file = 'log.txt'
        self.verbose = verbose
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        open(self.log_file, 'w').close()

    def start_log(self):
        self.log = True
        self.thread = Thread(target=self.log_procedure)
        self.thread.start()

    def stop_log(self):
        self.log = False
        if self.thread.is_alive():
            self.thread.join()

    def log_procedure(self):
        seeker = 0
        while self.log:
            try:
                output = self.compute.instances().getSerialPortOutput(project=self.project, zone=self.zone, instance=self.name, start=seeker).execute()

                seeker = output['next']
                if self.verbose:
                    print(output['contents'], end='', flush=True)
                f = open(self.log_file, 'a')
                f.write(output['contents'])
                f.close()
            except Exception as e:
                print('-'*50)
                print('WARNING')
                _, val, tb = sys.exc_info()
                print(traceback.print_exception(None, e, tb))
                print('-'*50)
            time.sleep(1)
        print('\n\n\nFINISHED LOGGING')

def operation_status(compute, project, zone, operation):
    result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

    return result


def list_instances(compute, project, zone) -> List[str]:
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else []


def wait_completion(compute, project, zone, operation):
    done = False
    while not done:
        result = operation_status(compute, project, zone, operation['name'])
        time.sleep(0.1)
        done = result['status'] == 'DONE'
    return result