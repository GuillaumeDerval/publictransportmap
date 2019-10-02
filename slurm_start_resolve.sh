#!/bin/bash

#SBATCH --job-name=resolve_min
#SBATCH --time=0-02:00:00 # days-hh:mm:ss
#
#SBATCH --ntasks=1
#SBATCH --mem=2000
#SBATCH --cpus-per-task=1

python 2_resolve_mindist.py $1 $2 $3