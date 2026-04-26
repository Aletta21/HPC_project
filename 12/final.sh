#!/bin/bash
#BSUB -q gpua100
#BSUB -J final
#BSUB -n 4
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "select[gpu40gb]"
#BSUB -W 02:00
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o final.out
#BSUB -e final.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

nvidia-smi

time python final.py 4571
