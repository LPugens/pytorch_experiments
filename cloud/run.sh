#!/bin/bash

# [START startup_script]
CS_BUCKET=$(curl http://metadata/computeMetadata/v1/instance/attributes/bucket -H "Metadata-Flavor: Google")
RESPOSITORY=$(curl http://metadata/computeMetadata/v1/instance/attributes/repository -H "Metadata-Flavor: Google")
OUTPUT_FOLDER=$(curl http://metadata/computeMetadata/v1/instance/attributes/output-folder -H "Metadata-Flavor: Google")

# Create a Google Cloud Storage bucket.
# gsutil mb gs://"$CS_BUCKET"

# Install CUDA drivers
curl -O http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
dpkg -i cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
apt-get update
apt-get -y install cuda


apt-get update
apt-get -y install python3 python3-pip unzip git wget

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -b

git clone "$RESPOSITORY"
cd pytorch_experiments || exit
/miniconda3/bin/conda env create --file environment.yml
# /miniconda3/bin/conda activate env_torch

gsutil cp -r "gs://$CS_BUCKET/data" ./

/miniconda3/envs/env_torch/bin/python trainer.py

# Store the image in the Google Cloud Storage bucket and allow all users
# to read it.
gsutil cp -r output gs://"$CS_BUCKET"

# [END startup_script]
