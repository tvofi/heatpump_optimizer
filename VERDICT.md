Fix review: blocked 8fef39fc30e2e7700c6eac7303fa7c36d68c4673 harness: class-open #2220 arm B (yield.mjs, D13-s1-01) is neither in the diff nor dispositioned in a body that writes Closes #2220
bus-nonce: 2df24c8b56858a17e40131e8e62ec585

Round 1. Reviewer seat rev-2323 (fix-review.md, fresh origin/main; preamble diff over dev/governance/roles/ empty). Measured head 8fef39fc30e2 (code head e8adc1b560222), merge base 7215e39df7a1. Head re-read before posting: unchanged.

## The block, and what clears it (body-only; no code change)

Issue #2220 is the I3 class issue. Its own Enumerator section names two arms: arm A, `D14/I3/hook_shape_seams.py`, which is this PR's, and arm B, `D13/s1/yield.mjs`, which is D13-s1-01. This body names only arm A, but it writes `Closes #2220`. Step 6 says a seam the rule returns that is neither in the diff nor dispositioned in the body blocks.

Arm B is in fact closed by #2294, which has merged. #2294's body says so ("Part of #2220 ... D11-s1-01 belongs to R10-PRE-EDIT-HOOK"). The body here has to say it too. The roster also conflicts: `wave-r10-groups.json` gives R10-PRE-EDIT-HOOK `fixes: []`. Its brief's closing rule asks for `Part of #2220`, not `Closes`. #2294's group listed `fixes: [2220]` and yet wrote Part of, so neither PR, as drafted to its roster entry, closes the issue.

Two fixes would clear this:
- (a) Keep `Closes #2220` and add one line: arm B / D13-s1-01 is closed by #2294 (merged), and arm A is closed here. The orchestrator then sets this group's `fixes` to [2220].
- (b) Write `Part of #2220` per the roster, and the orchestrator closes #2220 by hand after the merge.

The orchestrator chooses between them.

## RESULT lines (my runs; finder's harnesses from handoff/audit-r10-register at d23205d13)

Base 7215e39df7a1:
- RESULT d11s1 escaped_heading_writes=1 control_refused=1; --perturb escaped=0
- RESULT d11s3 refused_heading_payloads=2 multiedit_refused=0 null_refused=0; --perturb 3/1/0
- RESULT sweep seams=16 escapes=1 (RELEASE_NOTES.md x MultiEdit); --clean 0; --perturb 2
- RESULT self-test 16 passed, 0 failed

Head 8fef39fc30e2:
- RESULT d11s1 escaped_heading_writes=0 control_refused=1
- RESULT d11s3 refused_heading_payloads=3 multiedit_refused=1 null_refused=0
- RESULT sweep seams=16 escapes=0
- RESULT self-test 21 passed, 0 failed

The finders' --perturb and --clean anchors do not exist at the head, because the fix rewrote the line they anchor on. So I re-derived the body's perturbed arms with my own perturbations, on copies of the head hook driven through the finder's sweep:
- clean: 0 escapes
- drop new_string from the tuple: 1 (Edit)
- drop the edits read: 1 (MultiEdit)
- both: 2

All four match the body, and the group's carry: the clean arm reads 0 and the perturbed arm 2.

## Mutation proof (on the predicate, not the tail; the self-test is the closure)

The body's claims, re-derived:
- `isinstance(edits, list)` changed to False: 2 red.
- The edits line replaced by `pass`: 2 red.
- Join on a space: 1 red.
- `"## "` changed to `"### "`: 3 red.

Mine:
- `list` changed to `tuple`: 2 red.
- `old_string` read instead of `new_string`: 2 red.
- Only `edits[:1]` read: 1 red.
- Top-level fields dropped: 1 red.

Two mutants survived. Neither blocks:
- **M6:** the guard changed to `if edits:` survives. It is equivalent: a string or dict iterates to no dict entries, and an int crashes. Every one of those allows.
- **M4:** dropping the `isinstance(e, dict)` filter survives. The case "non-object edits entries fail OPEN" pins the outcome, but not the filter, because a crash also allows. M4 is observable only on a mixed list such as `[7, {heading}]`: the head refuses that and M4 allows it. That is a schema-invalid MultiEdit. Adding a refuse case for that mixed list would pin the filter.

## Attacks (attacks.txt; base and head side by side)

- **CRLF and CR-only line endings**, in Write, Edit and in MultiEdit's edit 2: all refused at the head. The base let the MultiEdit cases through.
- **Heading position:** an indented heading, a heading in the middle of a new_string, a heading in edit 3 of 3, and a heading after an edit with no trailing newline are all refused at the head.
- **Mixed shapes:** MultiEdit plus a top-level new_string is refused.
- **NotebookEdit:** a `notebook_path` on RELEASE_NOTES.md with `new_source` is refused at both ends.
- **Null controls:** body-only edits and `###` sub-headings are allowed, and so is anything on main.
- **The census's field class** (Edit new_string, Write content, MultiEdit edits[].new_string, NotebookEdit new_source) gives 16 of 16 seams refused or NA at the head. It has no other text field in the matcher's tools.

Escapes at both base and head, the same for Edit as for MultiEdit:
- A heading split across two edits (`##` plus ` v9.9.9`).
- An Edit that inserts `##` before text already in the file.
- `##<TAB>v9.9.9`.

The predicate inspects the inserted text, not the resulting file, by design ("reads what is being written"). These escapes are not the MultiEdit seam, they are not in the census's class, and the stamp refuses at release. Observation only.

## Is failing open here an escape?

No:
- A non-list `edits`, or non-dict entries, is not a MultiEdit the tool could apply.
- Well-formed dict entries are still read when garbage sits beside them (A15, refused).
- The header's stated policy is to fail open, and the backstop still runs: `tools/release/stamp.py` rules 3 and 4, also listed in round-10's sweep-I3.md.

## Other contract steps

- **Required checks:** every check-run at the head has concluded (`commits/<sha>/check-runs` API). None is red, so step 11 has no trigger.
- **merge-tree** against origin/main: exit 0.
- **Version files:** VERSION, the manifest and the notes heading are untouched. The diff is `.claude/hooks/pre-edit.sh` plus the PR's own delivery row.
- **Forward-carry:** none owed beyond the group carry, which is met.
- **Owner gate:** `.claude/hooks/` is code-owned, so tvofi's review is still required.

Evidence: HEAD.txt, harness_raw.txt, mutants.txt, attacks.txt, body_rederive.txt, the scripts, and the finder harness sources. Paths are scrubbed.
