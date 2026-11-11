# Proposal triage, session s6, batch 9 (P77-P78)

Two proposals from the s6 `proposals.md`, S6-V13 and S6-V14, both filed
2026-10-24. Numbering continues after `s6-batch8.md` (P66-P76, unmerged at this
base). GitHub calls: 0 for the rulings; the three V14 job figures are the
filing's own.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P77: space-padded `wc -l` compared as text (S6-V13)
Verdict: REJECT the tracked helper and the watcher instrument; nothing is built
Source: s6 `proposals.md` `## V13`.
Instances: 2, both in out-of-tree seat scratch: a sweep's offset file held "      32" and broke `tail -n +`; the triage proposals watcher read "      99" as a change and exited, leaving its liveness file stale for about 20 min. Tracked code already uses the fix as its convention: `git grep -n "wc -l < .* | tr -d ' '" origin/main -- tools/audit/seat/cloud_relay.sh` prints 11 sites, and `git grep -n -E '\$\(wc -l' origin/main -- tools | wc -l` prints 48 line-count substitutions in 12 files. No tracked script ships the padded text comparison.
Cost: a helper is a new tracked file (closure classification, a self-test, an `INSTRUMENTS.md` row) for a one-token idiom (`$(( $(wc -l < f) ))`); a tracked watcher instrument replaces per-seat scratch loops that the seat contracts already tell a seat to write.
Binding: the harm is a few minutes of a stale liveness file, found by the next sweep, in untracked scripts, and the cure is an idiom the tree already follows; a new file and its upkeep cost more than that. Would change the answer: a padded `wc` text comparison found in a tracked script (the grep above is the check), or a third scratch instance that cost a lost PR rather than minutes.

## P78: file-content host paths reach CI because prepr never runs `ref_privacy.py --check` (S6-V14)
Verdict: ACCEPT -> R10-FLOW-JIDOKA (raises an existing carry from a note to a required arm; no new group)
Source: s6 `proposals.md` `## V14`.
Instances: 3 reds in CI on "Refuse a push that names the host", all 2026-10-24: batch 5 (#2735, job 120901210622, step failed at 5a03e901b), batch 6 (#2738, job 120905519221, "1 refused" at line 9 of the batch file) and batch 7 (#2741). `git grep -c ref_privacy origin/main -- tools/pr/prepr.sh` prints 0: prepr never calls it. The tool judges content: its own header says `--check` "also judges every line a diff adds to a tracked file since" the merge base. Run at this base on a clean tree: `python3 -I tools/audit/seat/ref_privacy.py --check` took 0.56 s wall and printed "98 line(s) added since 73b69fe0a9fa judged, 0 refused". Older instances: the 2026-10-22 `ref_privacy --check` red on #2625, already in R10-FLOW-JIDOKA's carry.
Cost: XS -- one call in `prepr.sh` (about 5 lines with its `step` line), one self-test row; 0.56 s per run, no API. It sits inside the owner's ruling on that group (quick, deterministic checks only; `ref_privacy --check` is named in it).
Binding: three reds in a day, each a red CI run and a repair push on a docs-only PR, against about half a second locally. The group's carry already says the replay must include this check but is not-started, so the three reds are the evidence that it is owed first. Narrowing: only the content arm over the diff's added lines; nothing is rewritten, so there is no codemod risk. Neighbours: P76 (verdict files at `push-verdict`) covers a different path to the same leak.
Carry text (for `roster_edit.py append-carry R10-FLOW-JIDOKA`, citing `triage: dev/programme/triage/s6-batch9.md#P78`): "Priority and shape of the ref_privacy arm in `prepr.sh` (the 2026-10-22 carry, 'must include instrument-self-tests ref_privacy --check'): three CI reds on 2026-10-24 (#2735, #2738, #2741) were home paths in added lines of docs-only batch files, and `prepr.sh` has no call to it. Add `python3 -I tools/audit/seat/ref_privacy.py --check` as a prepr step (and to `--body-check`), 0.56 s measured, refusing on any line the diff adds that it judges. Controls: a diff adding a home path to a tracked file refuses and names file and line; the same diff with the path made `~/`-relative or removed passes (null); one self-test row, one mutant that deletes the call. Do not widen to a full-tree scan."
