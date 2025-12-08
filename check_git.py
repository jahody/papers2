import subprocess
import os

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"
    except Exception as e:
        return str(e)

with open('git_info.txt', 'w') as f:
    f.write("REMOTE:\n")
    f.write(run_cmd('git remote -v'))
    f.write("\nSTATUS:\n")
    f.write(run_cmd('git status'))
    f.write("\nGH STATUS:\n")
    f.write(run_cmd('gh auth status'))
