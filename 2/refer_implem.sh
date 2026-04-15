#!/bin/bash


#BSUB -q hpc               # Queue name (e.g., hpc)
#BSUB -J ex2_1           # Job name
#BSUB -n 1                # Number of cores (1 core)
#BSUB -W 01:00             # Walltime (hh:mm) - adjust as needed
#BSUB -R "select[model==XeonGold6226R] rusage[mem=4GB]"
#BSUB -R "span[hosts=1]"
#BSUB -o refer_implem_60_floors_new.out     # Standard output file
#BSUB -e refer_implem_60_floors_new.err      # Standard error file


#BSUB -B 
#BSUB -N

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613_2026

echo "Running serial"
time python simulate.py 60