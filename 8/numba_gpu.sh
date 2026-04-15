#!/bin/bash
#BSUB -q c02613
#BSUB -J task8_cuda
#BSUB -n 4
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -R "rusage[mem=4GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o task8_cuda.out
#BSUB -e task8_cuda.err
#BSUB -B
#BSUB -N

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

nvidia-smi

time python numba_gpu.py 90