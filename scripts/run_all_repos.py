import os
import uuid
import shutil
import numpy as np
import os.path as osp
from pprint import pprint
from subprocess import STDOUT, check_output


# REPO_PREFIX = "https://github.com/ML-HW-SYS/a3-WenheLI"
REPO_PREFIX = "git@github.com:ML-HW-SYS/a3-%s.git"
SCRIPT_ROOT = os.getcwd()
print(SCRIPT_ROOT)
IDLEN = 6


def random_id(l):
    from random import choice
    from string import ascii_uppercase
    return ''.join(choice(ascii_uppercase) for i in range(l))


def pull_all_repos():
    repo_lst = {} # student id -> repo info
    with open("github_handles.txt", "r") as f:
        for l in f:
            h = l.strip()
            if h == "":
                continue
            repo_url = REPO_PREFIX % h
            repo_name = "a3-%s" % h
            cmd = "git clone %s" % repo_url
            print(cmd)
            os.system(cmd)
            cmd = "cd %s & git pull origin main" % repo_name
            print(cmd)
            os.system(cmd)

            # We will create one and save it to <repo_name>/leaderboard_id.txt
            if osp.isdir(repo_name):
                lid_fname = osp.join(repo_name, "leaderboard_id.txt")
                student_id = None
                if osp.isfile(lid_fname):
                    with open(lid_fname, "r") as sidf:
                        for l in sidf:
                            student_id = l.strip()[:IDLEN]
                            if student_id not in repo_lst.keys():
                                break
                            else:
                                student_id = None

                if student_id is None:
                    student_id = random_id(IDLEN)
                    print("SID created: ", student_id)
                    with open(lid_fname, "w+") as sidf:
                        sidf.write(student_id)
                    cmd = 'cd %s ; git pull ; echo `pwd` ; git add leaderboard_id.txt ; git commit -m "Leaderboard ID." ; git push' % repo_name
                    print(cmd)
                    os.system(cmd)
                repo_lst[student_id] = (repo_name, repo_url)

    print("=" * 80)
    print("=" * 80)
    print("Done pulling")
    print("=" * 80)
    pprint(repo_lst)
    print("=" * 80)
    return repo_lst


def profile_all_repos(repo_lst):
    results_lst = {}
    for sid, (repo_name, repo_url) in repo_lst.items():
        print("=" * 80)
        print("Profiling: %s %s" % (sid, repo_name))
        print("-" * 80)
        shutil.copy(
            "../repo_profiler.py", osp.join(repo_name, "repo_profiler.py"))
        os.chdir(repo_name)

        # Timout the profiler
        cmd = "python repo_profiler.py"
        print("CMD: ", cmd)
        try:
            output = check_output(cmd, stderr=STDOUT, timeout=100, shell=True)
            print(output)
            results_lst[sid] = (
                repo_name, osp.join(SCRIPT_ROOT, repo_name, "results.csv"))
        except Exception as e:
            print(e)
            print("Timeout:", osp.join(SCRIPT_ROOT, repo_name, "results.csv"))
        os.chdir(SCRIPT_ROOT)
        print("=" * 80)

    # Gather results
    print("=" * 80)
    print("Gather outputs")
    output, keys = {}, None  # student id
    for sid, (repo_name, result_fname) in results_lst.items():
        print(sid, repo_name)
        with open(result_fname) as rf:
            for l in rf:
                if sid not in output:
                    output[sid] = {}
                else:
                    field_lst = l.strip().split(",")
                    field_key = "-".join(field_lst[:2])
                    field_val = float(field_lst[2])
                    output[sid][field_key] = field_val
            avg = sum(output[sid].values()) / float(len(output[sid].values()))
            output[sid]['avg'] = avg
            if keys is None:
                keys = output[sid].keys()
    return output, keys


def create_leaderboard(results, keys):
    leaderboards = []
    all_data = {}
    for key in keys:
        lst = [(sid, res[key]) for sid, res in results.items()]
        lst = sorted(lst, key=lambda item: float(item[1]))
        with open(osp.join(SCRIPT_ROOT, "..", "%s.md" % key), "w") as ldfile:
            ldfile.write("|ID|Time(s)|\n")
            ldfile.write("|-|-|\n")
            for sid, secs in lst:
                ldfile.write("|%s|%3.5f|\n" % (sid, secs))
                if sid not in all_data:
                    all_data[sid] = {}
                all_data[sid][key] = secs
        leaderboards.append(lst)

    # The overall leader board
    all_data = sorted(list(all_data.items()), key=lambda item: item[1]['avg'])
    with open(osp.join(SCRIPT_ROOT, "..", "README.md"), "w") as ldfile:
        ldfile.write("|ID|%s|\n" % ('|'.join(keys)))
        ldfile.write("|%s|\n" % ("|".join(["-"] * (len(keys) + 1))))
        for sid, secs in all_data:
            ldfile.write("|%s|%s|\n" % (sid, "|".join(
                [("%3.5fs" % secs[k]) for k in keys])))
    return leaderboards


if __name__ == "__main__":
    # Load githubt handles
    os.system("rm -rf %s/a3-*/" % SCRIPT_ROOT)
    os.system("ls %s" % SCRIPT_ROOT)
    repo_lst = pull_all_repos()
    results, keys = profile_all_repos(repo_lst)
    leaderboards = create_leaderboard(results, keys)

    # Save the output for checking
    np.save("leaderboards.npy", leaderboards)
    np.save("results.npy", results)
    np.save("repos.npy", repo_lst)

    # Push
    os.system("git add ../*.md")
    from datetime import datetime as dt
    time_str = dt.now()
    os.system('git commit -m "Leader board at time: %s"' % time_str)
    os.system("git push")
