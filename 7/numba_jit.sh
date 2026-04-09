#!/bin/bash
#BSUB -q hpc
#BSUB -J numba_jit
#BSUB -n 1
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6226R] rusage[mem=16GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o numba_jit.out
#BSUB -e numba_jit.err
#BSUB -B
#BSUB -N

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

time python numba_jit.py 90