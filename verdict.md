Design review: revise d1a4ae6a7472b807f23b4fe63a015b6dc412dff3 architecture-unsound

Round 1. Design tip d1a4ae6a7472b807f23b4fe63a015b6dc412dff3 (one file, design.md). The note's base b3831ff64eca1936f0b618193ee86c3e337b51a9 is an ancestor of the judging base b880dc914f3ba2590b7ce655d7419678b1c4968e, 38 commits behind; between them only tools/audit/seat/beatd.py and bus.sh move under tools/audit/, and no line the note cites moves. Every citation below is at b880dc914f.

## Revise

1. architecture-unsound, design.md section 2 "Prompt text" and section 6 "Part 2". The note routes *every* stop to a BLOCKED note on handoff-wip/<topic> by rewriting the setup line (tools/audit/seat/cloud_dispatch.py line 238) and the tail (lines 377-378). Both strings are shared by every role `_prompt` renders, so the shape as written:
   - gives the reviewer two contradictory stop channels: its body (lines 316-320) already sends every stop to a `Fix review: blocked <head> seat-refused: ...` verdict on probe/rev-<pr>-<nonce8>, which is the only ref the relay reads for it;
   - tells the designer and the design reviewer to push to handoff-wip/<topic> while their bodies say "You may push only to that ref" (lines 345, 357); for the design roles <topic> is the group's topic, so handoff-wip/<topic> is the fixer's step ref (WIP_NS, line 324): a refused design reviewer would write onto the fixer's WIP ref;
   - breaks the note's own null control: "probe text unchanged at :371" cannot hold, because the probe render also carries line 238 and the tail at 377-378.
   Fix wanted: the stop channel is per role, stated in each role's body (fixer: BLOCKED.md on handoff-wip/<topic>, as carry 10 asks; reviewer: the existing blocked verdict on its probe ref; designer: a BLOCKED note on its own design/<topic> push path or the `push-design` channel, whichever bus.sh admits; design reviewer: a `Design review: revise <sha> seat-refused` verdict on design-verdict/<topic>; probe: its body_push.sh return), and the shared setup and tail point to "your role's stop channel below" instead of naming a ref. The Part 2 self-test then asserts, per role, that the text names that role's return ref for a stop and no role names "your result"; the null control is the probe's result channel at line 371, unchanged in meaning, with the test stating why the shared lines changed under it (carry 10 already allows "or the test says why there is none").

## Checked and sound (no point)

- Seam (step 1): the three new modules each own one concern; queue grammar stays roster_queue.py's (parse_line :164, mark_line :199, `#done`/`#refused`); merge_train.py is not edited and already exposes `classify` (:11423) and `posted-verdict` (:11437); roster_lib.is_outside (:818), critical_path_read (:941), needs_design (:729) exist; gh_comment.fetch_thread is tools/pr/gh_comment.py:205; approve_held_runs.sh is tools/pr/; bus.sh dispatch-handoff exists (:899-907). No new write path into state another module owns.
- Shape (step 2): every drain step is one standing-merge.md or standing-dispatch.md names (preflight with closes as arguments, the unintended-close report, approve_held_runs.sh, bus.sh dispatch, outside_intake.py answer); cp-owed's arms and graces are carry 4 verbatim; FIRE-OWED (orchestrator_tick.py :1088) and _seat_on (:857) are moved, not re-implemented.
- Carry 12 confirmed landed: merge_pr.sh:379 prints `ALREADY POSTED: comment <id>` under `# mut:repost`, self-tested at :304 and :310.
- Carry 11 site confirmed: roster_lib.is_hotfix (:828-835) still admits `kind == "bug"`.
- Carry 5 site confirmed: beatd.jobs.json line 3 `"class_wait_s": 60`.
- Sibling sites (step 3): `git grep -n "your result" -- tools/audit/seat/` returns exactly :238, :371, :378, as the note says. The standing-merge/standing-dispatch caller set matches the note's list; tools/ci/selftest_closures.json is derived like closures.json, HANDOVER.md is carry 7.
- Siblings in flight (step 5): R11-PRE-PARALLEL-PIPELINE's part 3 rewrites standing-merge.md's serial route; the note orders part 4 after it. R11-PRE-SHARED-FILES cites orchestrator_tick.py:4144 only.

## Notes for the fixer

- Part 2: carry 9's premise "no match for foreground|background" is stale at this base: the setup line (:239-240) says "Run anything heavy in the background with Monitor", and the reviewer body already says "never end your turn while a background poll runs" (:318-319, pinned at :1403). The self-test arm must key on the new foreground-wait sentence, not on the word "background", or the reviewer arm passes on the base. Carry: R11-PRE-STANDING-SCRIPTS (item dr1-wait-premise)
- Part 1: R11-PRE-TOOLCHAIN-PIN's design adds a promote row to tools/audit/seat/beatd.jobs.json (its line 46), a hot file the note's section 5 lists only as beat_jobs.py; serialise the class_wait_s edit and the cp-owed row against it. Carry: R11-PRE-STANDING-SCRIPTS (item dr1-beatd-jobs-hot)
- Part 1: the stub contracts must keep citing `standing.md`, or tests/entities.py:42646-42650 (each standing-*.md cites standing.md) is edited in the same part that writes the stub. Carry: R11-PRE-STANDING-SCRIPTS (item dr1-stub-citation)

## Routed decisions

- decision: orchestrator: part 1 is sized S while it carries a new module with eight self-tested arms and a mutant per arm, the FIRE-OWED move with its agreement test, class_wait_s and is_hotfix across six files; whether it is S or M is the orchestrator's dispatch call, not a design defect.
