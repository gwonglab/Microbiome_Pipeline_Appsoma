import json
import os
import sys

sys.path.append( "code/welder_api" )
from welder_api import *

params = {}
with open( "params.json" ) as f:
	params = json.loads( f.read() )

num_cores = params['num_cores']

with open("./datasets/microbiome_db/human-microbiome/hmp_i50_db.prj") as f:
  for line in f:
    sp_line = line.rstrip(os.linesep).split("=")
    if sp_line[0] == "numofsequences":
      num_sequences = sp_line[1]
    elif sp_line[0] == "numofletters":
      num_letters = sp_line[1]
    elif sp_line[0] == "volumes":
      volumes = int(sp_line[1])

assert(num_sequences)
assert(num_letters)
assert(volumes)

with open("./datasets/microbiome_db/nt/nt_tax_i50_db.prj") as f:
  for line in f:
    sp_line = line.rstrip(os.linesep).split("=")
    if sp_line[0] == "numofsequences":
      num_sequences_nt = sp_line[1]
    elif sp_line[0] == "numofletters":
      num_letters_nt = sp_line[1]
    elif sp_line[0] == "volumes":
      volumes_nt = int(sp_line[1])

assert(num_sequences_nt)
assert(num_letters_nt)
assert(volumes_nt)

with open("./inputs/num_splits") as f:
  num_splits = int(f.readline())

lastal_folders = []

for volume in range(0, volumes):
  job = {
      "name": "lastal_job_v{}".format(volume),
      "inputs": {
        "fasta_dir": "$TASKS/split/outputs"
        },
      "mounts": {
        "datasets": "$DATASETS/:rw"
        },
      "command": "bash ./code/microbiome_pipeline/run_lastal_chunk.sh {} {} {} {}".format(volume,num_splits,num_cores,"./datasets/microbiome_db/human-microbiome/hmp_i50_db"),
      "container_image": "jordanualberta/microbiome",
      "requirements": {
        "cpus": num_cores,
        "mem": 6144, 
        "disk": 1024
        }      
      }
  lastal_folders.append(welder_run_task_add(job))

for volume in range(0, volumes_nt):
  job = {
      "name": "lastal_job_nt_v{}".format(volume),
      "inputs": {
        "fasta_dir": "$TASKS/split/outputs"
        },
      "mounts": {
        "datasets": "$DATASETS/:rw"
        },
      "command": "bash ./code/microbiome_pipeline/run_lastal_chunk.sh {} {} {} {}".format(volume,num_splits,num_cores,"./datasets/microbiome_db/nt/nt_tax_i50_db"),
      "container_image": "jordanualberta/microbiome",
      "requirements": {
        "cpus": num_cores,
        "mem": 6144, 
        "disk": 1024
        }      
      }
  lastal_folders.append(welder_run_task_add(job))

job = {
    "name": "sort_results",
    "inputs": {
      },
    "command": "bash ./code/microbiome_pipeline/sort_results.sh {} {}".format(num_splits,num_cores),
    "container_image": "jordanualberta/microbiome",
    "requirements": {
      "cpus": num_cores,
      "mem": 6144, 
      "disk": 1024
      }      
    }
for volume in range(0, volumes):
  job["inputs"]["volume_{}".format(volume)] = "$TASKS/lastal_job_v{}/outputs".format(volume)
for volume in range(0, volumes_nt):
  job["inputs"]["volume_nt_{}".format(volume)] = "$TASKS/lastal_job_nt_v{}/outputs".format(volume)

sort_folder = welder_run_task_add(job)

dlca_folder = welder_run_task_add({
  "name": "dlca",
  "inputs": {
    "merged_blast": "$TASKS/sort_results/outputs/merged_r2_q3_a5_b2.blast.gz"
    },
  "mounts": {
    "datasets": "$DATASETS/:rw"
    },
  "command": "bash ./code/microbiome_pipeline/dlca.sh",
  "container_image": "jordanualberta/microbiome",
  "requirements": {
    "cpus": num_cores,
    "mem": 512, 
    "disk": 512
    }      
  })
