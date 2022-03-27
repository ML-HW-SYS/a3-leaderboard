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
            student_id = str(uuid.uuid1())
            print("SID created: ", student_id)
            with open(osp.join(repo_name, "leaderboard_id.txt"), "w") as sidf:
                sidf.write(student_id)
            repo_lst[student_id] = (repo_name, repo_url)

            # TODO: push the student-id to their repository
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
    output = {}  # student id
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
    keys = output[sid].keys()
    return output, keys


def create_leaderboard(results, keys):
    leaderboards = []
    for key in keys:
        lst = [(sid, res[key]) for sid, res in results.items()]
        lst = sorted(lst, key=lambda item: float(item[1]))
        with open(osp.join(SCRIPT_ROOT, "..", "%s.md" % key), "w") as ldfile:
            ldfile.write("ID,Time(s)\n")
            for sid, secs in lst:
                ldfile.write("%s,%3.5f\n" % (sid, secs))
        leaderboards.append(lst)
    return leaderboards

if __name__ == "__main__":
    # Load githubt handles
    repo_lst = pull_all_repos()
    results, keys = profile_all_repos(repo_lst)
    leaderboards = create_leaderboard(results, keys)

    # Save the output for checking
    np.save("leaderboards.npy", leaderboards)
    np.save("results.npy", results)
    np.save("repos.npy", repo_lst)
