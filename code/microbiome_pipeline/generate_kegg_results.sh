#!/bin/bash

set -eo pipefail

pigz -dc ./inputs/merged_blast | parse_kegg_results.py ./datasets/microbiome_db/kegg_id_map/kegg_id_map.txt | pigz > ./results/read_keggpath.txt.gz

pigz -dc ./results/read_keggpath.txt | awk -F'\t' '{count[$2]++}END{for(j in count) print j "\t" count[j]}' | sort -t "	" -k 2,2rn > ./results/keggpath_counts.txt
