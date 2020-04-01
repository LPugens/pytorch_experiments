#!/bin/bash
set -x

CONDA="/home/lpugens/miniconda3/bin/conda"
PYTHON_ENV_TORCH="/home/lpugens/miniconda3/envs/env_torch/bin/python"

CS_BUCKET="datasets_pugens"

cd pytorch_experiments

$PYTHON_ENV_TORCH trainer.py --dataset-path ../data

sudo gsutil cp -r output gs://"$CS_BUCKET"

exit