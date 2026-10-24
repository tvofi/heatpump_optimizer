"""R10-FLY-CLOUD-SETUP-TOOLCHAIN: does a cloud seat's shell get the toolchain?

The carries' control is "a non-login `python3 -c "import numpy"` succeeds in a
fresh cloud seat". A fresh seat cannot be made from inside one, so this
harness models the agent's own shell on the box it runs on: a first-level
`bash -c` (`env -i` drops SHLVL) on a socket stdin, as Claude Code's Bash tool
starts it, with the image PATH and none of the environment's variables. It
reads the profile and the remedy from the cloud-setup.sh it is given, so the
merge base and the head run through the same arms:

  bare       the agent's shell, nothing set                      (the defect)
  remedy     the script's own remedy: its profile, its ~/.bashrc hook on a
             stock ~/.bashrc, and BASH_ENV pointing at the profile
  remedy-nul the same on a /dev/null stdin: the null control, showing the
             profile itself works whenever bash reads it
  variables  the variables `cloud-setup.sh --variables` prints, set on the
             agent's shell (n/a where the script has no such mode)
  nested     #2452: under BASH_ENV, a nested `PATH=<stub>:$PATH bash -c`
             must still find the stub's python3 first

  python3 -I dev/audit/harnesses/r10_cloud_setup_toolchain.py \\
      --script <cloud-setup.sh> [--prefix /opt/hpo]

Needs an installed prefix (venv-ci with numpy). Prints one `ARM <name>: ...`
line per arm, then `verdict: toolchain reaches the agent's shell: yes|no`.
"""

import argparse
import hashlib
import os
import re
import socket
import subprocess
import tempfile
from pathlib import Path

IMAGE_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
PROBE = 'command -v python3; python3 -c "import numpy" 2>/dev/null && echo numpy-ok || echo numpy-missing'


def profile_text(script: str, prefix: str, out: Path) -> None:
    """Write the profile the script would write, by its own code."""
    if re.search(r"^write_profile\(\) \{", script, re.M):
        fn = re.search(r"^write_profile\(\) \{.*?^\}", script, re.M | re.S).group(0)
        cmd = f'{fn}\nwrite_profile "$1" "$2"'
    else:  # the merge base: an inline heredoc on $PROFILE and $PREFIX
        block = re.search(r'^cat > "\$PROFILE" <<EOF\n.*?^EOF$', script, re.M | re.S).group(0)
        cmd = f'PROFILE="$1"; PREFIX="$2"\n{block}'
    subprocess.run(["bash", "-c", cmd, "_", str(out), prefix], check=True, stdin=subprocess.DEVNULL)


def shell(env: dict, cmd: str, stdin_socket: bool) -> str:
    a, b = socket.socketpair()
    try:
        r = subprocess.run(["env", "-i", *(f"{k}={v}" for k, v in env.items()), "bash", "-c", cmd],
                           stdin=a.fileno() if stdin_socket else subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=60)
    finally:
        a.close(); b.close()
    return " ".join(r.stdout.split())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--prefix", default="/opt/hpo")
    args = ap.parse_args()
    script = Path(args.script).read_text()
    with tempfile.TemporaryDirectory() as td:
        home = Path(td) / "home"; home.mkdir()
        prof = Path(td) / "hpo-toolchain.sh"
        profile_text(script, args.prefix, prof)
        bashrc = Path("/etc/skel/.bashrc").read_text() if Path("/etc/skel/.bashrc").exists() else '[ -z "$PS1" ] && return\n'
        hooked = ". $PROFILE\" >> \"$HOME/.bashrc\"" in script
        (home / ".bashrc").write_text(bashrc + (f". {prof}\n" if hooked else ""))
        bare = {"HOME": str(home), "PATH": IMAGE_PATH}
        remedy = {**bare, "BASH_ENV": str(prof)}
        arms = {"bare": shell(bare, PROBE, True),
                "remedy": shell(remedy, PROBE, True),
                "remedy-nul": shell(remedy, PROBE, False)}
        if "--variables)" in script:
            r = subprocess.run(["env", "-i", f"PATH={IMAGE_PATH}", "bash", args.script, "--variables"],
                               stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True)
            env = dict(line.split("=", 1) for line in r.stdout.splitlines())
            arms["variables"] = shell({**bare, **env}, PROBE, True)
        else:
            arms["variables"] = "n/a (no --variables mode)"
        stub = Path(td) / "stub"; stub.mkdir()
        (stub / "python3").write_text("#!/bin/sh\necho stub\n"); (stub / "python3").chmod(0o755)
        live = {**remedy, "PATH": f"{args.prefix}/venv-ci/bin:{IMAGE_PATH}"}
        arms["nested"] = shell(live, f'PATH="{stub}:$PATH" bash -c "command -v python3"', False).replace(td, "<tmp>")
    print(f"script sha1 {hashlib.sha1(script.encode()).hexdigest()} (~/.bashrc hook: {'yes' if hooked else 'no'})")
    for k, v in arms.items():
        print(f"ARM {k}: {v}")
    ok = arms["variables"].endswith("numpy-ok") or arms["remedy"].endswith("numpy-ok")
    print(f"verdict: toolchain reaches the agent's shell: {'yes' if ok else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
