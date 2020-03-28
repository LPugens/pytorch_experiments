import googleapiclient.discovery

from cloud.vm_handler import list_instances, VirtualMachine
from util import random_string
from threading import Thread
from time import sleep


project = 'pugens2'
zone = 'us-central1-f'
bucket = 'datasets_pugens'
repository = 'git@github.com:LPugens/pytorch_experiments.git'


compute = googleapiclient.discovery.build('compute', 'v1')
instances = list_instances(compute, project, zone)
instance_name = random_string()
while instance_name in instances:
    instance_name = random_string()

vm = VirtualMachine(instance_name, project, zone)
try:
    vm.instantiate(compute, bucket, repository)
except Exception as e:
    print(e)
finally:
    sleep(10)
    vm.delete(compute)

print("DONE")