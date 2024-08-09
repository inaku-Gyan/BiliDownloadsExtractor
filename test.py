# import subprocess as sp


import time
import subprocess


def cmd(command):
    subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, encoding="utf-8")
    # subp.wait(2)
    if subp.poll() == 0:
        print(subp.communicate())
        print(subp.communicate())
    else:
        print("失败")


def func():
    pass


cmd("ffmpeg -version")
print("hello", flush=True)
cmd("exit")
