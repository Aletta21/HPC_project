#!/bin/bash
#BSUB -q gpuv100
#BSUB -J nsys_stats
#BSUB -n 4
#BSUB -W 00:10
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -R "rusage[mem=4GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o nsys_stats.out
#BSUB -e nsys_stats.err

module load cuda/12.6

nsys stats cupy_profile.nsys-rep