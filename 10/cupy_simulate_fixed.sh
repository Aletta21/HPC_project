#!/bin/bash
#BSUB -q c02613
#BSUB -J cupy_fixed
#BSUB -n 4
#BSUB -W 00:30
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=16GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o cupy_simulate_fixed.out
#BSUB -e cupy_simulate_fixed.err
#BSUB -B
#BSUB -N

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

python cupy_simulate_fixed.py 90