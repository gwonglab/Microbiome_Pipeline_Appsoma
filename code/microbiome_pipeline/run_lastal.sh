#!/bin/bash

set -eo pipefail

NUM_CORES=$1

# Split fasta seq into min 1mb size, max 512 chunks
MB_SIZE=$(( $(du --apparent-size -m ./inputs/fasta | cut -f 1 -d '	') + 1 ))
if [ "$MB_SIZE" -le "512" ]
then
  NUMSPLITS=${MB_SIZE}
else
  NUMSPLITS=512
fi
SPLITFRAGTEMPLATE="/tmp/fasta_%1.1d" fastasplitn ./inputs/fasta ${NUMSPLITS}

#NUMNTVOLUMES=$(cat ${LIB_DIR}/db/nt_db/nt_tax_last.prj | grep "^volumes=" | cut -f 2 -d '=')

HMP_DB="./datasets/microbiome_db/human-microbiome/hmp_i50_db"
NUMHMVOLUMES=$(cat ${HMP_DB}.prj | grep "^volumes=" | cut -f 2 -d '=')

NUM_SEQS=$(cat ${HMP_DB}.prj | grep "^numofsequences=" | cut -f 2 -d '=')
# Slightly inaccurate.  last only counts ATCGs, not any ambiguous bases
NUM_BASES=$(cat ${HMP_DB}.prj | grep "^numofletters=" | cut -f 2 -d '=')

echo "parallel --halt 2 -j${NUM_CORES} \"bash -c -o pipefail \"lastal -r2 -q3 -a5 -b2 -m50 ${HMP_DB}{1} /tmp/fasta_{2} | maf2blast - ${NUM_BASES} ${NUM_SEQS} | pigz > ./outputs/fasta_{2}_hm{1}_r2_q3_a5_b2.blast.gz\"\" ::: $(seq 0 $(($NUMHMVOLUMES-1))) ::: $(seq 1 $NUMSPLITS)"

parallel --halt 2 -j${NUM_CORES} "bash -c -o pipefail \"lastal -r2 -q3 -a5 -b2 -m50 ${HMP_DB}{1} /tmp/fasta_{2} | maf2blast - ${NUM_BASES} ${NUM_SEQS} | pigz > ./outputs/fasta_{2}_hm{1}_r2_q3_a5_b2.blast.gz\"" ::: $(seq 0 $(($NUMHMVOLUMES-1))) ::: $(seq 1 $NUMSPLITS)
