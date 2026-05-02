#!/bin/bash
#BSUB -q c02613
#BSUB -J final
#BSUB -n 4
#BSUB -W 00:30
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=16GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o final.out
#BSUB -e final.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

module swap cuda cuda/13.2.0

nvidia-smi

time python final.py 4571