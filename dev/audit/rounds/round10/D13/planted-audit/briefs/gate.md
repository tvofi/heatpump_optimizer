TEST-SUITE RUN (sample set pda-1109). For each pair below, run the product suite at commit A and at
commit B and report both exit codes. At each commit: `git fetch origin <sha>`, a fresh detached worktree
there, then `PYTHONPATH=tests/hastub python3 tests/features.py` (the tests.yml invocation, venv-ci python3
on PATH), in the background under Monitor, polling at most every 240 s; allow up to 60 min per run.
- pair k3: A=56a214c8bd8f72dfc4839234dc749cc53ec6813c B=02954c6aa76b64f0bbf904f233f954c5d0cbb168
- pair q7: A=ce4cdb2271c3a3883c422e228f55d526d93827e2 B=bb2ab4b3b54485ba07ad4fb4ae5f7faf58a7bbd2
- pair m2: A=a942da87b28a2ec60cf29717754c6a663c9f4efe B=19dff27fe599c934aa0441ae5c5f98035fc30914
Result body: one line per run, exactly `<pair> <A|B> <sha> rc=<n> <the suite's last summary line>`, then
for any run with rc != 0 the names of its FAIL lines (at most 20). Run nothing else; judge nothing.
