import os, sys, time
mode, n = sys.argv[1], int(sys.argv[2])
if n <= 0:
    time.sleep(120); sys.exit(0)
pid = os.fork()
if pid == 0:
    {'pgrp': lambda: os.setpgid(0,0), 'session': os.setsid, 'cleanenv': os.setsid, 'plain': lambda: None}[mode]()
    env = {} if mode=='cleanenv' else os.environ
    os.execve(sys.executable,[sys.executable,sys.argv[0],mode,str(n-1)],env)
time.sleep(0.02); os.waitpid(pid,0)
