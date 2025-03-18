import os
import uuid
import shutil
import numpy as np
import os.path as osp
from pprint import pprint
from subprocess import STDOUT, check_output
import git, subprocess
import pandas as pd

# REPO_PREFIX = "https://github.com/ML-HW-SYS/a3-WenheLI"
REPO_PREFIX = f"https://{os.environ['GH_TOKEN']}@github.com/ML-HW-SYS/a3-%s.git"
REPO_ROOT = os.getcwd()
print(REPO_ROOT)
IDLEN = 6
YEAR = '2025'


def random_id(l):
    names = ["Rug Heed Bend","Creed Symbol","Smalltalk Dribble","Blackouts","Digital Destroyers","Key to Innovation","Grapevine Squad","Rebooting Rebels","Computer Crew","Miss Hit Proclaim","Pseudo Boom","Gonzo Brutes","Byte Mechanics","The Hit Blunders","Hackerjacks","Loose Screws","Artful Maneuvers","The ERROR List","Troubleshooters","Blue Screens","Beast Isis","Geo-Thermal Energy","Pint Sized Benchwarmers","Digitally Destroyed","Prime Calculus","Electra","Brew Alley","Power Mongers","Bait Chums","Ping Intelligence","Skyhook DimensionThe Spin Doodles","The Systems Squads","The Alter Ridge","Remote Connections","Creative Juices","Analysis Systems","Bandwidth of Brothers","Mind Ink Bots","Freak Gravity","The Cyco Paths","Analyzing Anarchists","Tech Phantoms","Dev tools Conniesseurs","Remote Controllers","Fully Developed","Maidens of Maya","Mechanical United","Tech Connect", "The Tech Avengers", "The Tech Warriors", "The Tech Wizards", "The Techies", "The Technocrats", "The Technophiles", "The Technophobes", "The Technophreaks", "The Technophyles"]
    return names[l].replace(" ", "_")


def pull_all_repos():
    repo_lst = {} # student id -> repo info
    # if postrun_commit.txt exists, make a copy of it
    if osp.isfile(f"{REPO_ROOT}/postrun_commit.txt"):
        shutil.copy(f"{REPO_ROOT}/postrun_commit.txt", f"{REPO_ROOT}/postrun_commit.txt.bak")
    postrun_commit = open(f"{REPO_ROOT}/postrun_commit.txt", "a")
    # Read postrun_commit.txt.bak as a dict
    h_to_sha = {}
    if osp.isfile(f"{REPO_ROOT}/postrun_commit.txt.bak"):
        with open(f"{REPO_ROOT}/postrun_commit.txt.bak", "r") as f:
            for l in f :
                l = l.strip()
                if l == "":
                    continue
                h, sha = l.split(",")
                h_to_sha[h] = sha
    # Read column github_username from github_handles.csv
    usernames = pd.read_csv(f"{REPO_ROOT}/github_handles.csv")["github_username"]
    for idx, h in enumerate(usernames):
        h = h.strip()
        if h == "":
            continue
        repo_url = REPO_PREFIX % h
        repo_name = "a3-%s" % h
        cmd = "git clone %s" % repo_url
        print(cmd)
        os.system(cmd)
        cmd = "cd %s & git pull origin main" % repo_name
        print(cmd)
        if h not in h_to_sha.keys():
            execute=1
        else:
            if int(subprocess.getoutput("git rev-list --count --since=%s" % (h_to_sha[l])))>1:
                execute=1
            else:
                execute=0
        os.system(cmd)
        # We will create one and save it to <repo_name>/leaderboard_id.txt
        if osp.isdir(repo_name):
            lid_fname = osp.join(repo_name, "leaderboard_id.txt")
            student_id = None
            if osp.isfile(lid_fname):
                with open(lid_fname, "r") as sidf:
                    for l in sidf:
                        student_id = l.strip()
                        if student_id not in repo_lst.keys():
                            break
                        else:
                            student_id = None

            if student_id is None:
                while student_id is None or student_id in repo_lst.keys():
                    student_id = random_id(idx)
                print("SID created: ", student_id)
                with open(lid_fname, "w") as sidf:
                    sidf.write(student_id)
                cmd = 'cd %s ; git pull ; echo `pwd` ; git add leaderboard_id.txt ; git commit -m "Leaderboard ID." ; git push' % repo_name
                print(cmd)
                os.chdir(repo_name)
                repo = git.Repo()
                sha = repo.head.object.hexsha
                os.chdir(REPO_ROOT)
                os.system(cmd)
                postrun_commit.write("%s,%s\n" % (student_id, sha))
            # if int(subprocess.getoutput("git rev-list --count --since=yesterday --before=today HEAD"))>1:
            repo_lst[student_id] = (repo_name, repo_url, execute)
    postrun_commit.close()
    print("=" * 80)
    print("=" * 80)
    print("Done pulling")
    print("=" * 80)
    pprint(repo_lst)
    print("=" * 80)
    return repo_lst


def profile_all_repos(repo_lst):
    results_lst = {}
    commit_hashes = {}  # Store commit hashes for each student ID
    for sid, (repo_name, repo_url, execute) in repo_lst.items():
        if execute==0:
            print("Skipping: %s %s" % (sid, repo_name))
            continue
        print("=" * 80)
        print("Profiling: %s %s" % (sid, repo_name))
        print("-" * 80)
        shutil.copy(
            "./repo_profiler.py", osp.join(repo_name, "repo_profiler.py"))
        os.chdir(repo_name)
        open("tests/__init__.py", "w").close()
        
        # Get the latest commit hash
        try:
            repo = git.Repo()
            commit_hash = repo.head.object.hexsha[:6]  # Get first 6 characters
            commit_hashes[sid] = commit_hash
            print(f"Commit hash: {commit_hash}")
        except Exception as e:
            print(f"Error getting commit hash: {e}")
            commit_hashes[sid] = "N/A"

        # Timout the profiler
        cmd = "python repo_profiler.py"
        print("CMD: ", cmd)
        try:
            output = check_output(cmd, stderr=STDOUT, timeout=100, shell=True)
            print(output)
            results_lst[sid] = (
                repo_name, osp.join(REPO_ROOT, repo_name, "results.csv"))
        except Exception as e:
            print(e)
            print("Timeout:", osp.join(REPO_ROOT, repo_name, "results.csv"))
            if osp.isfile(osp.join(REPO_ROOT, repo_name, "results.csv")):
                with open(osp.join(REPO_ROOT, repo_name, "results.csv"), 'r') as fp:
                    lines = len(fp.readlines())
                if lines == 5:
                    results_lst[sid] = (
                        repo_name, osp.join(REPO_ROOT, repo_name, "results.csv"))
        os.chdir(REPO_ROOT)
        print("=" * 80)

    # Gather results
    print("=" * 80)
    print("Gather outputs")
    output, keys = {}, None  # student id
    for sid, (repo_name, result_fname) in results_lst.items():
        print(sid, repo_name)
        with open(result_fname) as rf:
            if sid not in output:
                output[sid] = {'commit_hash': commit_hashes.get(sid, 'N/A')}
            else:
                output[sid]['commit_hash'] = commit_hashes.get(sid, 'N/A')
            
            for l in rf:
                field_lst = l.strip().split(",")
                if len(field_lst) == 3 and field_lst[0] != "op":  # Skip header
                    field_key = "-".join(field_lst[:2])
                    field_val = float(field_lst[2])
                    output[sid][field_key] = field_val
            
            # Calculate average of timing values (excluding commit_hash)
            timing_values = [v for k, v in output[sid].items() if k != 'commit_hash']
            if timing_values:
                avg = sum(timing_values) / float(len(timing_values))
                output[sid]['avg'] = avg
            else:
                output[sid]['avg'] = float('inf')
            
            if keys is None:
                keys = list(output[sid].keys())
    
    # Ensure 'commit_hash' is in keys
    if keys and 'commit_hash' not in keys:
        keys.insert(0, 'commit_hash')
    
    return output, keys, commit_hashes


def create_leaderboard(results, keys, commit_hashes):
    leaderboards = []
    all_data = {}
    
    for key in keys:
        if key == 'commit_hash':
            continue  # Skip creating a separate leaderboard for commit hashes
        
        lst = [(sid, res[key], res.get('commit_hash', 'N/A')) for sid, res in results.items()]
        lst = sorted(lst, key=lambda item: float(item[1]))
        
        with open(osp.join(REPO_ROOT, "..", "%s.md" % key), "w") as ldfile:
            ldfile.write("|ID|Commit|Time(s)|\n")
            ldfile.write("|-|-|-|\n")
            for sid, secs, commit in lst:
                ldfile.write("|%s|%s|%3.5f|\n" % (sid, commit, secs))
                if sid not in all_data:
                    all_data[sid] = {}
                all_data[sid][key] = secs
                all_data[sid]['commit_hash'] = commit
        
        leaderboards.append(lst)

    # The overall leader board
    all_data_items = list(all_data.items())
    all_data_items = sorted(all_data_items, key=lambda item: item[1].get('avg', float('inf')))
    
    with open(osp.join(REPO_ROOT, ".", "README.md"), "w") as ldfile:
        # Create header with all keys except commit_hash (which will be a separate column)
        timing_keys = [k for k in keys if k != 'commit_hash']
        ldfile.write("|ID|Commit|%s|\n" % ('|'.join(timing_keys)))
        ldfile.write("|%s|\n" % ("|".join(["-"] * (len(timing_keys) + 2))))
        
        for sid, data in all_data_items:
            commit = data.get('commit_hash', 'N/A')
            values = [("%3.5fs" % data.get(k, float('inf'))) for k in timing_keys]
            ldfile.write("|%s|%s|%s|\n" % (sid, commit, "|".join(values)))
    
    return leaderboards


if __name__ == "__main__":
    # Load githubt handles
    os.system("rm -rf %s/a3-*/" % REPO_ROOT)
    os.system("ls %s" % REPO_ROOT)
    repo_lst = pull_all_repos()
    results, keys, commit_hashes = profile_all_repos(repo_lst)
    leaderboards = create_leaderboard(results, keys, commit_hashes)

    # Save the output for checking
    from datetime import datetime as dt
    time_str = dt.now()
    np.save(f"leaderboards_{time_str}.npy", leaderboards)
    np.save(f"results.npy_{time_str}", results)
    np.save(f"repos.npy_{time_str}", repo_lst)

    # # Push
    os.system("git add ./*.md")
    os.system('git commit -m "Leader board at time: %s"' % time_str)
    os.system(f"git push authedorigin 2025_2:{YEAR}")
