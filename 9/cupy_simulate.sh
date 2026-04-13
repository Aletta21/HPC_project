#!/bin/bash
#BSUB -q gpuv100
#BSUB -J cupy_simulate
#BSUB -n 1
#BSUB -W 00:30
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=16GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o cupy_simulate.out
#BSUB -e cupy_simulate.err
#BSUB -B
#BSUB -N

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

time python cupy_simulate.py 90