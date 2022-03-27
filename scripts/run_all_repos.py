import os
import sys
import shutil
import pytest
import os.path as osp

from subprocess import STDOUT, check_output

# REPO_PREFIX = "https://github.com/ML-HW-SYS/a3-WenheLI"
REPO_PREFIX = "git@github.com:ML-HW-SYS/a3-%s.git"
SCRIPT_ROOT = os.getcwd()
print(SCRIPT_ROOT)


if __name__ == "__main__":
    # Load githubt handles
    repo_lst = []
    with open("github_handles.txt", "r") as f:
        for l in f:
            h = l.strip()
            if h == "":
                continue
            repo_url = REPO_PREFIX % h
            repo_name = "a3-%s" % h
            repo_lst.append((repo_name, repo_url))
            cmd = "git clone %s" % repo_url
            print(cmd)
            os.system(cmd)
            cmd = "cd %s & git pull origin main" % repo_name
            print(cmd)
            os.system(cmd)
    print("=" * 80)
    print("=" * 80)
    print("Done pulling")
    print("=" * 80)
    print(repo_lst)
    print("=" * 80)

    results_lst = []
    for repo_name, repo_url in repo_lst:
        # cmd = 'bash -c "conda activate ece5545 & python -m pytest tests/test_1dconv_cpu.py"'
        # repo_path = osp.join(SCRIPT_ROOT, repo_name)
        # sys.path.insert(0, repo_path)
        # ret_code = pytest.main(["tests/test_1dconv_cpu.py"])
        # print(ret_code)
        # cmd = 'python -m pytest tests/test_1dconv_cpu.py'
        # print(cmd)
        # os.system(cmd)
        # sys.path.remove(repo_path)
        shutil.copy(
            "../repo_profiler.py", osp.join(repo_name, "repo_profiler.py"))
        os.chdir(repo_name)
        # os.system("ls *")
        # Timout in 10 s
        cmd = "python repo_profiler.py"
        print("CMD: ", cmd)
        # os.system(cmd)
        try:
            output = check_output(cmd, stderr=STDOUT, timeout=100, shell=True)
            print(output)
            results_lst.append(osp.join(SCRIPT_ROOT, repo_name, "results.csv"))
        except Exception as e:
            print(e)
            print("Timeout:", osp.join(SCRIPT_ROOT, repo_name, "results.csv"))
        os.chdir(SCRIPT_ROOT)

    # Gather results
    for result_fname in results_lst:
        print(result_fname)
        # TODO: output a leader board page from the results
        # TODO: create a repository on this, with only the scripts
        # TODO: the leaderboard will be the MARKDOWN function on the READER or github pages
        # TODO: final step is the G2

        # TODO: create the ananymous names for each repository and push it