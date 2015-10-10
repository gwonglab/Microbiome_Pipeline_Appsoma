#!/bin/bash

set -eo pipefail

VOLUME=$1
NUM_SPLITS=$2
NUM_CORES=$3

HMP_DB="./datasets/microbiome_db/human-microbiome/hmp_i50_db"

parallel --halt 2 -j${NUM_CORES} "bash -c -o pipefail \"lastal -r2 -q3 -a5 -b2 -m50 ${HMP_DB}${VOLUME} ./inputs/fasta_dir/fasta_{1} | maf2blast.py | top_percent_blast.py 15 | pigz > ./outputs/fasta_{1}_hm${VOLUME}_r2_q3_a5_b2.blast.gz\"" ::: $(seq 1 $NUM_SPLITS)
