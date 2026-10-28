Fix review: blocked 5a03e901be80782cfacabf69b6bff1895dddb864 host-path: s6-batch5.md line 9 publishes the orchestrator's home directory, so ref_privacy --check refuses it and instrument-self-tests is red at this head

bus-nonce: a39799ec7d4958b7e4f4a91971229b0c

Round 2, from an independent second reviewer. I measured head 5a03e901be80782cfacabf69b6bff1895dddb864, and it is still the branch head on origin (`ev/HEAD.txt`). The merge base is e97f5749b. The roles diff since the merge base is empty (`ev/roles-diff.txt`), so the contract I applied is current.

## Block

Line 9 of `dev/programme/triage/s6-batch5.md` spells an absolute home-directory path, `/Users/<account>/hpo-orch/r10s6/` (redacted in `ev/line9-redacted.txt`). That path names the owner's account. #2310's owner ruling forbids publishing it, and `tools/audit/seat/ref_privacy.py --check` (CONTENT: every line a diff adds to a tracked file) refuses it.

- Reproduced locally at this head: `ref_privacy: REFUSE dev/programme/triage/s6-batch5.md:9: host-path in an added line of a tracked file`, exit 1 (`ev/ref_privacy-head.txt`).
- Null control: I dropped only that path from line 9 in a throwaway local commit, which I did not push. With that change, the same check passes with 0 refused, exit 0 (`ev/ref_privacy-scrubbed.txt`). The refusal therefore comes from that span alone.
- CI agrees. In `governance / instrument-self-tests` (job 120901210622), step 22, "Refuse a push that names the host, and an unregistered pusher", failed (`ev/ci.txt`).
- Earlier practice: no file under `dev/programme/` at the base carries a `/Users/` path (`ev/main-programme-host-paths.txt`). s6-batch1..3 and s5-batch2 cite the same evidence as "the s6 orchestrator's out-of-tree `proposals.md`" and name no host path.

The fix is one edit. Either run `ref_privacy.py scrub --write dev/programme/triage/s6-batch5.md`, or drop the path and keep the words "out-of-tree directory". The cited file names and the greps stay as they are.

This head also fails step 11 of `fix-review.md`. Three checks are red, all workflows have concluded, and a `pr-contract` run (job 120905148712) started after the last red one concluded. Yet the body's `## Red checks` says "none". The cheaper detector is `python3 -I tools/audit/seat/ref_privacy.py --check`, which ran locally in under 2 seconds before the handoff and shows exactly this red. So the unanswered `instrument-self-tests` red would be `root-cause-detectable` even without the block above.

## Findings

- Round-1 claim verified. Every counted instance in P63's `Instances:` now has its grep and log line beside it: w14/w15 at seat-ledger.md:93 and proposals.md:86, merge w3/w4 at seat-ledger.md:92 and :94, and #2698 at proposals.md:64 and seat-ledger.md:86. The uncounted w5/w6 is named, with its reason. That answers the round-1 `figure-uncited` block in form. The cited files are out of tree, so I could not run the greps, and the count of 3 is not re-derived (step 8). Taken as quoted, the #2698 ledger line describes a second writer that was averted ("the local update_pr stays the single writer"), not two live writers. "(4 filed)" cannot be re-derived from the cited filings either: line 64 holds two and line 86 holds one, which makes three. The ACCEPT survives either way, because the w14/w15 and w3/w4 citations each show two live seats with timestamps. Before BEATD's designer sizes the token, they should re-read the instances as 2 observed, 1 averted and 1 filed only. Carry: R10-ORCH-BEATD
- `s6-batch5.md` cites `s6-batch4.md` twice: once for the numbering after P62, and once for P57, the DEFER it supersedes. That file is not on origin/main; it exists only on open #2734 (`origin/triage/s6-batch4`). The body states no merge order, so this PR should merge after #2734. Carry: #2734

## Evidence

- `git merge-tree --write-tree origin/main 5a03e901b` exits 0 against the current origin/main 73b69fe0a, with no conflicting paths (`ev/merge-tree.txt`).
- CI at this head is in `ev/ci.txt`. The red checks are `instrument-self-tests` (step 22), `pr-contract` twice (step 10, "Check the body against the contract"), and `gate` twice (step 4, "Judge this head"). I did not read the step-10 log line. The red `gate` follows from the red runs it judges. Every other run is success or skipped.
- Classification: both files are under `dev/programme/`, which `tests/closure.py` lists as INERT. The diff touches no code, budgets, claim files, VERSION, manifest version or notes heading; the pr-contract version step printed "no version edit". The mutation proof is n/a, as the body says.
- Ruling on the merits, apart from the block: P57's DEFER named its trigger ("re-triage on a third instance"), and the w14/w15 recurrence is that trigger. The narrowed carry, a generation token checked by the tracked queue writers, answers P57's binding that a lock named in a brief binds only a seat that remembers it. The kill helper is rejected for a stated reason, and the destination R10-ORCH-BEATD is an existing group. The verdict ACCEPT is sound once the path is scrubbed.
