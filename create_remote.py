#!/usr/bin/env python

import argparse
import os
import time

import googleapiclient.discovery


def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None


def create_instance(compute, project, zone, name, bucket, output_folder, repository):
    image_response = compute.images().getFromFamily(
        project='gce-uefi-images', family='ubuntu-1804-lts').execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'run.sh'), 'r').read()

    config = {
        'name': name,
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
            }, {
                'key': 'output-folder',
                'value': output_folder
            }]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()


def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()


def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)


def main(project, bucket, zone, instance_name, output_folder, repository):
    compute = googleapiclient.discovery.build('compute', 'v1')
    try:

        print('Creating instance.')

        operation = create_instance(compute, project, zone, instance_name, bucket, output_folder, repository)
        wait_for_operation(compute, project, zone, operation['name'])

        instances = list_instances(compute, project, zone)

        print('Instances in project %s and zone %s:' % (project, zone))
        for instance in instances:
            print(' - ' + instance['name'])

        print(f"""
        Instance created.
        It will take a minute or two for the instance to complete work.
        Check this URL: http://storage.googleapis.com/{bucket}/{output_folder}
        Once the image is uploaded press enter to delete the instance.
        """)

    except Exception as e:
        print(e)

    finally:
        print('Deleting instance.')

        operation = delete_instance(compute, project, zone, instance_name)
        wait_for_operation(compute, project, zone, operation['name'])


def run():
    args = parse_args()
    main(args.project_id, args.bucket_name, args.zone, args.name, args.output_folder, args.repository)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project_id', type=str, help='Your Google Cloud project ID.',
                        default='pugens2')
    parser.add_argument('bucket_name', type=str, help='Your Google Cloud Storage bucket name.',
                        default='datasets_pugens')
    parser.add_argument('--repository', type=str, default='https://github.com/LPugens/pytorch_experiments',
                        help='Git repository to fetch.')
    parser.add_argument('--zone', type=str, default='us-central1-f', help='Compute Engine zone to deploy to.')
    parser.add_argument('--name', type=str, default='demo-instance', help='New instance name.')
    parser.add_argument('--output-folder', type=str, default='output', help='Output folder to store in the bucket.')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    run()
