#!/bin/bash
set -x

# [START startup_script]
CS_BUCKET="datasets_pugens"

# Install CUDA drivers
curl -O http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
sudo apt-get update
sudo apt-get install -y cuda



apt-get update
apt-get -y install git wget

gsutil -m cp -r "gs://$CS_BUCKET/data" ./

# Store the image in the Google Cloud Storage bucket and allow all users
# to read it.

# [END startup_script]
exit