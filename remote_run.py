import googleapiclient.discovery

from cloud.vm_handler import list_instances, VirtualMachine
from util import random_string
from threading import Thread
from time import sleep


project = 'pugens2'
zone = 'us-central1-a'
machine_type = 'n1-standard-1'
bucket = 'datasets_pugens'
repository = 'https://github.com/LPugens/pytorch_experiments'


compute = googleapiclient.discovery.build('compute', 'v1')
instances = list_instances(compute, project, zone)
instance_name = random_string()
while instance_name in instances:
    instance_name = random_string()

vm = VirtualMachine(instance_name, project, zone, machine_type)
try:
    vm.instantiate(compute, bucket, repository)
    input('Press ENTER to finish the VM')
except Exception as e:
    print(e)
finally:
    print('FINISHING THE VM')
    vm.delete(compute)

print("DONE")