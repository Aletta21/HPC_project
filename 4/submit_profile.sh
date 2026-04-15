#!/bin/bash
#BSUB -J profile_jacobi
#BSUB -q hpc
#BSUB -W 15
#BSUB -R "rusage[mem=1GB]"
#BSUB -n 1
#BSUB -o profile_jacobi.out
#BSUB -e profile_jacobi.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

time LINE_PROFILE=1 python -u profile_simulate.py 20