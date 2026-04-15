#!/bin/bash
#BSUB -q gpuv100
#BSUB -J cupy_fixed
#BSUB -n 4
#BSUB -W 00:30
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=16GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o cupy_fixed.out
#BSUB -e cupy_fixed.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate cupy_env

module swap cuda cuda/12.6

time python cupy_simulate_fixed.py 90