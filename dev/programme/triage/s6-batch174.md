# Proposal triage, session s14, batch 174 (P591)

This batch rules queue line 270 (the orchestrator's shim intake), 2026-11-11.

Sources:
- origin/main `e67b79c9fc`. Every line number below is at that commit.
- The installed shim `~/.local/state/hpo/bin/gh` (reinstalled 07:50Z), the merge train's log,
  `$HPO_STATE_DIR/gh-calls.log`, and `ps`.

## P591: SHIM-COMMENT-GUARD-ONE-CHECKOUT

Verdict: ACCEPT, re-pointed, as a PART 2 ITEM carry on R10-GH-READ-RESIDUE (stage in-progress).
That group owns `tools/audit/seat/shims/`, which includes `seat-gh`, the shim's source. Neither of
the proposal's alternatives is taken as written:
- A blob equal to origin/main's refuses every checkout that lags main by one commit to
  `gh_comment.py`.
- A registered-checkout list is one more file to keep current.
- Refusing the install fixes nothing for checkouts that already exist.

Source: the orchestrator's queue line 270, 2026-11-11.

Instances, measured:
- **The defect.** `seat_venv.sh --install-shims` writes one tree's path into the shim's `gcpy=`
  line (`tools/audit/seat/seat_venv.sh:301-305`). The shim lets a record-issue comment write
  through only when the caller's script real path equals `gcpy`. The installed copy now reads
  `gcpy=.../s14/tools-wt-45adb0c3/tools/pr/gh_comment.py`.
- **Live checkouts running seat tools,** counted from `ps` argv:
  - `tickloop-wt`: 7 processes (`orchestrator_tick.py` and the tick loop's posters);
  - `beat-wt-a7628041`: 4 (`beatd.py`);
  - `tools-wt-45adb0c3`: 1 (the merge train, by cwd).
  Whichever checkout installed last is the only one whose tracker posts pass.
- **A refusal that happened.** The train log, line 19861: `#3424 OWED record: the #3394 comment
  was refused (1: gh shim: a comment write on a record issue ...)`. That was under the
  earlier install.
- **A refusal waiting to happen.** In `gh-calls.log`, `tickloop-wt/tools/pr/gh_comment.py` runs at
  07:52-07:53Z, after the 07:50Z reinstall baked the train's checkout. Its next tracker write is
  refused. Had the guard accepted any checkout, `gcpy` would not name a single tree.

The fix, in `shims/seat-gh` and its self-test:
- Accept a caller whose script real path is `<root>/tools/pr/gh_comment.py`, where `<root>` is a
  checkout of this repository (it holds `tools/audit/seat/shims/seat-gh`) and
  `git -C <root> diff --quiet HEAD -- tools/pr/gh_comment.py` holds (committed, unmodified).
- A committed `gh_comment.py` carries `mandate_guard`, which is the reason the guard exists.
- The baked `gcpy` stays as the fast path. The guard stays deny-by-default for every other caller.
- The `ps` spoof residual is unchanged and still accepted by design.
- Self-test:
  - a second checkout's clean `gh_comment.py` passes;
  - the same file with a local edit is refused;
  - a `gh_comment.py` outside any checkout is refused.

What it costs and what it saves:
- **Cost:** about 15 shim lines and 3 self-test cases, in a group that is already open on this file.
- **Benefit:** every tracker record post from 2 of the 3 live checkouts is refused after each
  install, and each refusal is an OWED record the orchestrator hand-repairs.
- It clears the 20% bar as a carry. No new mechanism is added.
