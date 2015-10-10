#!/bin/bash

set -eo pipefail

# Split fasta seq into min 1mb size, max 512 chunks
MB_SIZE=$(( $(du --apparent-size -m ./inputs/fasta | cut -f 1 -d '	') + 1 ))
if [ "$MB_SIZE" -le "512" ]
then
  NUMSPLITS=${MB_SIZE}
else
  NUMSPLITS=512
fi
SPLITFRAGTEMPLATE="./outputs/fasta_%1.1d" fastasplitn ./inputs/fasta ${NUMSPLITS}

echo $NUMSPLITS > ./outputs/num_splits
