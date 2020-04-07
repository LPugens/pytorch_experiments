import sys, traceback

import googleapiclient.discovery

from cloud.vm_handler import list_instances, VirtualMachine
from util import random_string
from threading import Thread
from time import sleep


project = 'pugens2'
zone = 'asia-east1-a'
machine_type = 'n1-standard-1'
bucket = 'datasets_pugens'
repository = 'https://github.com/LPugens/pytorch_experiments'
use_gpu = True


compute = googleapiclient.discovery.build('compute', 'v1')
instances = list_instances(compute, project, zone)
instance_name = random_string()
while instance_name in instances:
    instance_name = random_string()

vm = VirtualMachine(name=instance_name, project=project, zone=zone, machine_type=machine_type, use_gpu=use_gpu)
try:
    vm.instantiate( bucket, repository)
    vm.send_files('./cloud/startup_environment.sh')
    vm.send_files('./cloud/startup_conda.sh')
    vm.send_files('./cloud/run_script.sh')
    vm.run_command('sudo ./startup_environment.sh')
    vm.reboot()
    vm.run_command('./startup_conda.sh')
    vm.run_command('./run_script.sh')
    input('Press ENTER to finish the VM')
except Exception as e:
    vm.logger.stop_log()
    print('The following uncaugth exception caused the abortion of the VM:')
    print('-'*50)
    _, val, tb = sys.exc_info()
    print(traceback.print_exception(None, e, tb))
    print('-'*50)
finally:
    print('FINISHING THE VM')
    vm.delete(compute)

print("DONE")