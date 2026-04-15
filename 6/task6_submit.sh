#!/bin/bash
#BSUB -q hpc
#BSUB -J task6_2
#BSUB -n 2
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6226R] rusage[mem=16GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o task6_2.out
#BSUB -e task6_2.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

time python task6.py 90 2