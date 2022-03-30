#! /bin/bash

cd /home/gy46/a3-leaderboard/scripts
# /share/apps/anaconda3/2021.05/bin/conda init &
# source /home/gy46/.bashrc & /share/apps/anaconda3/2021.05/bin/conda activate /home/gy46/anaconda2/envs/ece5545
export PATH="/home/gy46/anaconda2/envs/ece5545:${PATH}"
python run_all_repos.py
