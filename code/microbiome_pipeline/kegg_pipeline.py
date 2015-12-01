import re
import json
import os
import sys

sys.path.append( "code/welder_api" )
from welder_api import *
from subprocess import call

params = {}
with open( "params.json" ) as f:
	params = json.loads( f.read() )

fastq_1 = params["fastq_end_1"]
fastq_2 = params["fastq_end_2"]
num_cores = params["num_cores"]

trim_folder = welder_run_task_add({
  "name": "fastq-mcf",
  "inputs": {
    "fastq_1": fastq_1,
    "fastq_2": fastq_2
    },
  "mounts": {
    "datasets": "$DATASETS/:rw"
    },
  "command": 'fastq-mcf -o ./outputs/fastq_1 -o ./outputs/fastq_2 -q 15 -l 50 --max-ns 2% -u ./datasets/microbiome_db/trim_db/trim.fa ./inputs/fastq_1 ./inputs/fastq_2',
  "container_image": "jordanualberta/microbiome",
  "requirements": {
    "cpus": 1,
    "mem": 512,
    "disk":512
    }
  })

fasta_folder = welder_run_task_add({
  "name": "seqtk",
  "inputs": {
    "fastq_1": "$TASKS/fastq-mcf/outputs/fastq_1",
    "fastq_2": "$TASKS/fastq-mcf/outputs/fastq_2",
    },
  "command": 'seqtk seq -A ./inputs/fastq_1 > ./outputs/fasta_1 && seqtk seq -A ./inputs/fastq_2 >> ./outputs/fasta_1',
  "container_image": "jordanualberta/microbiome",
  "requirements": {
    "cpus": 1,
    "mem": 512,
    "disk":512
    }
  })

split_folder = welder_run_task_add({
  "name": "split",
  "inputs": {
    "fasta": "$TASKS/seqtk/outputs/fasta_1"
    },
  "command": "bash ./code/microbiome_pipeline/split_fasta.sh",
  "container_image": "jordanualberta/microbiome",
  "requirements": {
    "cpus": 1,
    "mem": 512,
    "disk": 512
    }
  })

last_folder = welder_run_task_add({
  "name": "generate_lastal_jobs",
  "inputs": {
    "num_splits": "$TASKS/split/outputs/num_splits"
    },
  "mounts": {
    "datasets": "$DATASETS/:rw"
    },
  "parameters": {
    "num_cores": num_cores
    },
  "command": "python ./code/microbiome_pipeline/setup_kegg_lastal_jobs.py".format(num_cores),
  "container_image": "jordanualberta/microbiome",
  "requirements": {
    "cpus": 1,
    "mem": 512,
    "disk": 512
    }
  })
