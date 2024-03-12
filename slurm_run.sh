#! /bin/bash

export PATH="/usr/local/cuda/bin:$PATH"

cd /home/afa55/a3-leaderboard

source env/bin/activate

# # /share/apps/anaconda3/2021.05/bin/conda init &
# # /share/apps/anaconda3/2021.05/bin/conda activate /home/gy46/anaconda2/envs/ece5545
# export PATH="/usr/local/cuda/bin/:/home/gy46/anaconda2/envs/ece5545/bin/:${PATH}"
export GH_TOKEN=YOUR_TOKEN_HERE
python scripts/run_all_repos.py
