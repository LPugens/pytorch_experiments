
CS_BUCKET="datasets_pugens"
CONDA="/home/lpugens/miniconda3/bin/conda activate env_torch"

cd pytorch_experiments

$CONDA activate env_torch

python trainer.py


gsutil cp -r output gs://"$CS_BUCKET"