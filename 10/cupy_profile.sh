#!/bin/bash
#BSUB -q gpuv100
#BSUB -J cupy_profile
#BSUB -n 4
#BSUB -W 00:30
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=16GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o cupy_profile.out
#BSUB -e cupy_profile.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate cupy_env

module swap cuda cuda/12.6

nsys profile -o cupy_profile python cupy_simulate.py 5