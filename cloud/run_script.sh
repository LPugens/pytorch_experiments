
CS_BUCKET="datasets_pugens"

cd pytorch_experiments

conda activate env_torch

python trainer.py


gsutil cp -r output gs://"$CS_BUCKET"