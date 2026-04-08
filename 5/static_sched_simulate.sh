#!/bin/bash
#BSUB -q hpc
#BSUB -J static_parallel
#BSUB -n 2
#BSUB -W 00:30
#BSUB -R "select[model==XeonGold6226R] rusage[mem=16GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o static_parallel_2.out
#BSUB -e static_parallel_2.err
#BSUB -B
#BSUB -N
#BSUB -u s253129@dtu.dk

source ~/miniconda3/etc/profile.d/conda.sh
conda activate hpc

time python static_sched_simulate.py 90 2