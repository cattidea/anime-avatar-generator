import subprocess
import os
import time


def new_process(cmd, **kwargs):
    shell = os.name == "nt"
    kwargs['shell'] = shell
    p = subprocess.Popen(cmd, **kwargs)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            p.terminate()
            break
