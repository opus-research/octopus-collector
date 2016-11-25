import subprocess


def run_cmd(cmd):
    print cmd
    return_code = subprocess.call(cmd, shell=True)
    if return_code != 0:
        raise BaseException("Error on executing the bash command: " + cmd)