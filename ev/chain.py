import os, sys, time
mode, n = sys.argv[1], int(sys.argv[2])
if n <= 0:
    time.sleep(60); sys.exit(0)
pid = os.fork()
if pid == 0:
    os.setsid()
    env = {"PATH": os.environ.get("PATH", "")} if mode == "cleanenv" else dict(os.environ)
    os.execve(sys.executable, [sys.executable, sys.argv[0], mode, str(n - 1)], env)
time.sleep(0.02)
os.waitpid(pid, 0)
