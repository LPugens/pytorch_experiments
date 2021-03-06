#!/bin/bash
set -x

CONDA="/home/lpugens/miniconda3/bin/conda"
RESPOSITORY="https://github.com/LPugens/pytorch_experiments"


wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -b
$CONDA update -n -y base -c defaults conda
$CONDA init bash

git clone "$RESPOSITORY"
cd pytorch_experiments
$CONDA install -y pytorch torchvision cudatoolkit=10.1 -c pytorch

exit