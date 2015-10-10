#!/bin/bash

set -eo pipefail

pigz -dc ./inputs/merged_blast | dlca --taxPath ./datasets/microbiome_db/taxonomy > ./results/dlca_results.txt
ktImportTaxonomy -tax ./datasets/microbiome_db/taxonomy ./results/dlca_results.txt -o ./results/taxonomy.krona.html
