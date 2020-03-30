#!/bin/bash

# [START startup_script]
CS_BUCKET="datasets_pugens"
RESPOSITORY="https://github.com/LPugens/pytorch_experiments"

# Create a Google Cloud Storage bucket.
# gsutil mb gs://"$CS_BUCKET"

# # Install CUDA drivers
# curl -O http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
# dpkg -i cuda-repo-ubuntu1804_10.1.243-1_amd64.deb
# apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
# apt-get update
# apt-get -y install nvidia-driver-435
# apt-get -y install cuda


apt-get update
apt-get -y install python3 python3-pip unzip git wget

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -b

git config --global user.name "LPugens GCLOUD"
git config --global user.email "lucaspugensf@gmail.com"
git clone "$RESPOSITORY"
cd pytorch_experiments || exit
/miniconda3/bin/conda env create --file environment.yml
# /miniconda3/bin/conda activate env_torch

gsutil -m cp -r "gs://$CS_BUCKET/data" ./

# Store the image in the Google Cloud Storage bucket and allow all users
# to read it.

# [END startup_script]
