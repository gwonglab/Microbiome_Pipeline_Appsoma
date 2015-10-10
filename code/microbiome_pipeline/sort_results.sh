#!/bin/bash

set -eo pipefail

NUM_SPLITS=$1
NUM_CORES=$2

for SPLIT in $(seq 1 ${NUM_SPLITS})
do
  pigz -dc ./inputs/volume_*/fasta_${SPLIT}_*_r2_q3_a5_b2.blast.gz | sort -k1,1 -k12,12rn --compress-program=pigz -S 5G --parallel=${NUM_CORES} | top_percent_blast.py 15
done | pigz > ./outputs/merged_r2_q3_a5_b2.blast.gz
