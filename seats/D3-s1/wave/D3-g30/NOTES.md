# Box D3-g30 working notes

- 2026-11-22T22:47Z null control (fullgate.py null, comment-only marker in tariff.py): gate_rc=1, wall 3777.3 s, load1 0.83..1.05,
  3 scripts red, identical in set and line counts to box D3-rem's accepted null (state/gates-prior/null-D3-rem-note.txt):
  closure.py selftest 2 (merge-tool pins, status skip-not-under-scoped), entities.py 1 of 2723 ("and is accepted when it
  does": scoped-path pin), harness_headers.py 4 of 115 (D6/claims.py header vs printed 2 lines, claims.json/md left
  modified, and "every inlined walk matches the canonical helper" naming this box's probes). No production file is read by
  any of them; usable, not re-taken. fullgate.py counts KILLED only beyond these.
- After the null, this box's probes were regenerated with the canonical repo_root (tools/audit/repo_root.py), so from a
  later gate on harness_headers may show 3 lines instead of 4: fewer than the null, never read as KILLED. Probe values
  unchanged (runprobes.sh: 16 same).
- Probes run only from a clean baseline worktree $HOME/probe-base (the gate's tree carries the mutant while a gate runs).
- 2026-11-23T00:59Z a stale `.git/worktrees/audit-r11-D3-s1/index.lock` (0 bytes, no git process held it; not created by the
  gate's own run.sh, whose log never mentions it) appeared 13 min into the 66686e3b gate. That gate ran its full hour, then
  fullgate.py's reset hit the lock (CalledProcessError) and wrote no record; gate_wave.sh then recorded 66686e3b and, as the
  tree stayed on the mutant commit, 5bf50f5d and cc96ce9e (each refused in seconds: "HEAD ... is not the baseline") as
  TIMEOUT. Those three TIMEOUTs are false and were withdrawn (kept under aborted/ as evidence, removed from the checkpoint).
  The lock was moved aside, the tree reset to the baseline, and the three keys are re-gated from scratch.
  Box-local workaround (never pushed as a tool change; copy at probes/_generator/gate_wave.box-local.sh): the driver now
  halts with DRIVER-ABORT instead of writing TIMEOUT when the tree is locked/off-baseline before a gate, or when fullgate
  ends without a record before the 4 h cap.
