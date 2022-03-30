#! /bin/bash

source /home/gy46/.bashrc
cd /home/gy46/a3-leaderboard/scripts
# /share/apps/anaconda3/2021.05/bin/conda init &
# /share/apps/anaconda3/2021.05/bin/conda activate /home/gy46/anaconda2/envs/ece5545
export PATH="/usr/local/cuda/bin/:/home/gy46/anaconda2/envs/ece5545/bin/:${PATH}"
python run_all_repos.py
