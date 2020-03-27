import os
import time

from typing import List
from threading import Thread, Lock
from functools import partial

compute_lock = Lock()

class VirtualMachine():
    def __init__(self, name:str, project: str, zone:str):
        self.alive = False
        self.project = project
        self.name = name
        self.zone = zone
        self.logger = VirtualMachineSerialLogger(name, project, zone)

    def instantiate(self, compute, bucket, repository):
        image_response = compute.images().getFromFamily(project='gce-uefi-images', family='ubuntu-1804-lts').execute()
        source_disk_image = image_response['selfLink']

        # Configure the machine
        machine_type = f"zones/{self.zone}/machineTypes/n1-standard-1"
        startup_script = open(os.path.join(os.path.dirname(__file__), 'run.sh'), 'r').read()

        config = {
            'name': self.name,
            'machineType': machine_type,

            # Specify the boot disk and the image to use as a source.
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
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
            }],

            # Metadata is readable from the instance and allows you to
            # pass configuration from deployment scripts to instances.
            'metadata': {
                'items': [{
                    # Startup script is automatically executed by the
                    # instance upon startup.
                    'key': 'startup-script',
                    'value': startup_script
                }, {
                    'key': 'bucket',
                    'value': bucket
                }, {
                    'key': 'repository',
                    'value': repository
                }]
            }
        }

        with compute_lock:
            operation = compute.instances().insert(
                project=self.project,
                zone=self.zone,
                body=config).execute()

        operation_result = wait_completion(compute, self.project, self.zone, operation)
        
        self.logger.start_log(compute)

        if 'error' in operation_result:
            raise Exception(operation_result['error'])

        return operation

    def delete(self, compute):
        with compute_lock:
            operation = compute.instances().delete(
                project=self.project,
                zone=self.zone,
                instance=self.name).execute()

        operation_result = wait_completion(compute, self.project, self.zone, operation)

        if 'error' in operation_result:
            raise Exception(operation_result['error'])

        self.logger.stop_log()

        return operation


class VirtualMachineSerialLogger():
    def __init__(self, name, project, zone):
        self.name = name
        self.project = project
        self.zone = zone
        self.log = False
        self.thread = None

    def start_log(self, compute):
        self.log = True
        self.thread = Thread(target=partial(self.log_procedure, compute))
        self.thread.start()

    def stop_log(self):
        self.log = False
        if self.thread.is_alive():
            self.thread.join()

    def log_procedure(self, compute):
        seeker = 0
        while self.log:
            try:
                with compute_lock:
                    output = compute.instances().getSerialPortOutput(project=self.project, zone=self.zone, instance=self.name, start=seeker).execute()

                wait_completion(compute, self.project, self.zone, output)

                seeker = output['next']
                print(output[''])
            except Exception as _:
                print('VM not available')
            time.sleep(1)
        print('\n\n\nFINISHED LOGGING')

def operation_status(compute, project, zone, operation):
    result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

    return result


def list_instances(compute, project, zone) -> List[str]:
    with compute_lock:
        result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else []


def wait_completion(compute, project, zone, operation):
    print(f'WAITING: {operation}')
    done = False
    while not done:
        with compute_lock:
            result = operation_status(compute, project, zone, operation['name'])
        done = result['status'] == 'DONE'
    print(result)
    return result