# Proposal triage, session s14, batch 158 (P570)

This batch rules `s7/triage-queue-s7.txt` line 253, the orchestrator's question on batch 157's
P569 owed item 1, which it asked before acting on it. The bar and the denominators are batch 141's.

Sources:
- origin/main `444cf62fab`: `tools/audit/seat/shims/seat-gh`, `tools/audit/seat/seat_venv.sh`,
  `tools/audit/seat/record_beat.py` and `tools/audit/seat/outside_intake.py`;
- PR 3427's head `7cbfa68013` (`fix/r10-gh-read-residue`, group R10-GH-READ-RESIDUE), diffed
  three-dot against its merge base;
- `git worktree list --porcelain` and `ps` on this host, at about 03:10Z.

## P570: S14-GH-SHIM-INSTALL-RISK

Verdict: ACCEPT. The orchestrator's reading is right on main. Installing the shim from main today
would refuse record-issue posts from every checkout but one, so batch 157's owed item 1 is
withdrawn as written. The repair is already in open PR 3427. Install the shim once PR 3427 merges,
from a branch-backed worktree that is never rotated. A log-only copy and a symlink bake are both
rejected.

Source: queue line 253 (2026-11-11T03:07:13Z, the orchestrator).

Instances:
- **On main, the guard admits one tree.**
  - `seat-gh` line 338 lets a record-issue write through only when
    `a=$(rp "$script") && b=$(rp "$gcpy") && [ "$a" = "$b" ]`. Here `gcpy` is the single path
    `seat_venv.sh --install-shims` bakes into the copy (`seat_venv.sh` lines 293 and 302:
    `gcpy=$ROOT/tools/pr/gh_comment.py`).
  - The posters run `gh_comment.py` from their own checkout:
    - `record_beat.py` line 129: `[sys.executable, "-I", str(ROOT / "tools/pr/gh_comment.py"), "post", ...]`;
    - `outside_intake.py` line 287: the same with `REPO_ROOT`.
  - Inside `gh_comment.py`, `gh` is the subprocess (line 178), so the shim's parent is that python
    process and its script is that checkout's file.
  - So with one install on `~/.local/state/hpo/bin`, a post from the train's
    `merge_train/batch-wt`, from `s14/beat-wt-d08ed310` or from any other tools tree is refused
    (`exit 1`, "gh shim: a comment write on a record issue ... refused").
  - A false premise would have looked like a comparison against a path pattern or the repository,
    not one physical path.
  - Batch 157's caveat named only the baked tree's removal. It missed this case.
- **A symlink bake does not help.** `rp` resolves the directory with `pwd -P` and refuses a file
  that is itself a symlink (lines 198-205). A stable symlink therefore still resolves to one
  physical tree, and a symlinked file is refused outright.
- **A log-only copy is a fork of a guarded instrument.** It would be a hand-edited `seat-gh` with
  lines 123-342 removed, on every seat's and daemon's PATH.
  - It drifts from the tree on the next shim change.
  - It ships the logging half without the record-issue guard that `comment-readback.md` relies on.
  - This repository's rule for a tool narrower than the policy is to widen the tool, not to work
    around it.
- **The tool is already widened, in PR 3427 (P449).** Its `seat-gh` diff (+14 lines after line 338)
  admits another tree's `tools/pr/gh_comment.py` when two things hold:
  - the file is tracked there (`git ls-files --error-unmatch`);
  - that tree is listed by `git -C <baked tree> worktree list --porcelain`.
  Its `gh_calls.py` self-test drives all four cases:
  - the baked tree admitted;
  - a second registered worktree admitted;
  - null control: an unregistered clone refused;
  - null control: an untracked same-named file refused.
  A mutant that drops the registration check lets the clone through.
- **Every poster on this host is a worktree of one repository.** `git worktree list --porcelain`
  lists `merge_train/batch-wt`, `s14/beat-wt-*`, `s14/tick-wt-d08ed310`, `s14/tools-wt-*`,
  `s13/tools-wt-*`, `cloud-fold-wt` and `hpo-seats/r10s6/orch-wt*`. The live parents in `ps` are
  `beat-wt-d08ed310`, `tick-wt-d08ed310` and `tools-wt-45adb0c3`, all listed.
- **What is left after PR 3427: the baked tree must outlive the install.** The admit path runs
  `git -C <baked tree> worktree list`. If the baked tree is removed, that read fails and every
  record post is refused (it fails closed). That is why the baked tree must be one that is never
  rotated.

Cost:
- No new code. The repair, its self-test and its mutant are in PR 3427, already in review under
  R10-GH-READ-RESIDUE.
- After the merge, the install is one orchestrator step: a branch-backed worktree at the merged
  main, used only as the bake target and never moved, removed or reset by a rotation. Then
  `tools/audit/seat/seat_venv.sh --install-shims ~/.local/state/hpo/bin` is run from it.
- Per call, the shim adds one bash start, one `ps` and one append to a log capped at 1 MB with one
  rotation. It adds one `git worktree list` only on a record-issue write.
- After the install, check that each daemon's calls appear in `S/gh-calls.log` under its parent
  name. `gh_calls.py --coverage` reads `/proc`, which this host does not have.
- A rollback is removing `~/.local/state/hpo/bin/gh`.

Binding: the attribution is worth it on these terms.
- It is the precondition batch 157 named for P569 (a) and (c).
- It turns on a record-issue guard that has been dead on this host since it landed, for the same
  reason the logging was.
- Once PR 3427 merges it costs one command. Before that merge, every option carries a standing
  risk that a postmerge record beat is refused mid-train.

Routing: no carry. The fix site is PR 3427's head, already under review. The install is the
orchestrator's local step after that merge.
- Until then, the triage seat measures without the shim: a zero-API sampler of running `gh`
  processes and their parents, beside `gh api rate_limit` (which costs nothing against the
  bucket), from the 03:24:36Z reset. It installs nothing and touches no PATH.
