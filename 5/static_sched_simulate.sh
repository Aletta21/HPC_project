#!/bin/bash
#BSUB -q hpc
#BSUB -J static_parallel
#BSUB -n 32
#BSUB -W 03:00
#BSUB -R "rusage[mem=8GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o static_parallel_32.out
#BSUB -e static_parallel_32.err

source ~/miniconda3/etc/profile.d/conda.sh
conda activate hpc


time python static_sched_simulate.py 90 32