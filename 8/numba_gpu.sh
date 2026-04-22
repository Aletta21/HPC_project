#!/bin/bash
#BSUB -q gpuv100
#BSUB -J task8_cuda
#BSUB -n 4
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "select[gpu16gb]"
#BSUB -W 00:30
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o task8_cuda.out
#BSUB -e task8_cuda.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

nvidia-smi

time python numba_gpu.py 90
