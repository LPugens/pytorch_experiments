#!/bin/bash

# [START startup_script]
CS_BUCKET=$(curl http://metadata/computeMetadata/v1/instance/attributes/bucket -H "Metadata-Flavor: Google")
RESPOSITORY=$(curl http://metadata/computeMetadata/v1/instance/attributes/repository -H "Metadata-Flavor: Google")
OUTPUT_FOLDER=$(curl http://metadata/computeMetadata/v1/instance/attributes/output-folder -H "Metadata-Flavor: Google")

# Create a Google Cloud Storage bucket.
gsutil mb gs://"$CS_BUCKET"

apt-get update
apt-get -y install python3 python3-pip unzip git wget

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -b

git clone "$RESPOSITORY"
cd Lucas_Master || exit
/home/lucaspugensf/miniconda3/bin/conda env create --file environment.yml
/home/lucaspugensf/miniconda3/bin/conda activate pugens_master

gsutil cp -r gs://"$CS_BUCKET"/datasets ./datasets

python3
# Store the image in the Google Cloud Storage bucket and allow all users
# to read it.
gsutil cp -r output gs://"$CS_BUCKET"/"$OUTPUT_FOLDER"

# [END startup_script]
