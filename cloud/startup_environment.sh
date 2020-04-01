#!/bin/bash
set -x

# [START startup_script]
CS_BUCKET="datasets_pugens"

# # Install CUDA drivers
# curl -O http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
# dpkg -i cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
# apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
# apt-get update
# apt-get -y install nvidia-driver-435
# apt-get -y install cuda


apt-get update
apt-get -y install git wget

gsutil -m cp -r "gs://$CS_BUCKET/data" ./

# Store the image in the Google Cloud Storage bucket and allow all users
# to read it.

# [END startup_script]
exit