Fix review: merge a056bdc8127525d226ca7c1df003176228e961e3

bus-nonce: bd0b435c85bf2de49b47bc27c7f59f9b

## Evidence

- Round: first review (hotfix) of handoff r10-hotfix-shim-escapes. Measured head a056bdc8127525d226ca7c1df003176228e961e3, the body's named head and still the tip of handoff/r10-hotfix-shim-escapes at verdict time (ev/merge-tree.txt). No pull request exists, so there is no review packet and no CI run to read; no check is red, and the body's Red checks: none stands.
- Diff (three-dot from merge base cbd23f1c8, which is origin/main's tip): tools/audit/seat/shims/seat-gh and tools/audit/seat/gh_calls.py only. No new tracked file. VERSION, the manifest and RELEASE_NOTES.md are untouched. No claim file or budget moved, so env_drift and the step-14 metric checks have nothing to compare.
- Merge: `git merge-tree --write-tree origin/main a056bdc8127525d226ca7c1df003176228e961e3` rc 0 (ev/merge-tree.txt).
- Harness disclosure: the finder's harness is the brief's job_log reproduction, and nothing in the tree commits it. I built ev/shim-harness.sh: it installs the tree's seat-gh with a stub real gh ahead of /usr/local/bin/gh and calls merge_train.job_log through it. It is the reviewer's instrument, not the finder's.
- RESULT job_log via shim at main cbd23f1c8: None. RESULT job_log via shim at tip: the stub log, read with --allow-escape-sequences (ev/repro-main-vs-tip.txt).
- RESULT unknown flag: at main, `gh api --bogus ...` is reported as "a comment write on a record issue". At the tip it reports "unknown gh api flag --bogus". The --bogus=1 and -Z spellings are named correctly at the tip too. All of these are rc 1 at both ends.
- Null control (no write flag newly admitted): at the tip, the flag combined with each of -X POST on issues/201/comments, -f on issues/3394/comments, -X PATCH on issues/comments/9 and a graphql mutation is still refused, rc 1, with the comment-write message. A plain GET of actions/jobs/7/logs reaches the real gh at both ends. The flag is boolean (API_BOOL) and sets no write state in api_gate.
- Self-test: tip 211 checks, 0 failed (ev/selftest-tip.txt); main 206 checks, 0 failed (ev/selftest-main.txt). The body's 211 figure is re-derived.
- Mutation proof (ev/mutants.txt): M1, the body's mutant (flag dropped from API_BOOL), is killed by 3 checks. M2 (unknown-flag message disabled) and M3 (unk unset in the --x arm) are killed by 1 check each. M5 and M6 survive; see Findings.
- Not re-derived: the body's "tests/entities.py ... ALL 2707 ENTITY CHECKS PASSED". In this container, venv-ci has no homeassistant module, so entities.py exits 1 at import (ev/entities-tail.txt). The diff is tooling under tools/audit/seat; the train re-proves the gate on the current main.
- Class (step 6): the body names no enumeration rule, and the issue states one seam (one flag gh accepts that the shim's table lacked). I compared gh 2.89's `gh api --help` flag list with API_VAL, API_BOOL and the explicitly handled flags. Every gh 2.89 api flag is known. --allow-escape-sequences is absent from gh 2.89's help; merge_train.job_log already handles a gh that lacks it.
- owed-reds set printed: tests / mutation, tests / typing, validate / validate-hacs. None ran on this head.

## Findings

- Surviving mutants M5 and M6: dropping `unk=` from the `--x=y` arm or the `-xVALUE` arm of api_gate leaves the self-test at 0 failed. The body claims an unknown api flag is named as such, but only the bare `--x` spelling is pinned. Under either mutant, `--bogus=1` or `-Z` would again be reported as a record-issue comment write. At this head both spellings are named correctly (ev/repro-main-vs-tip.txt). Carry: dismissed: message-only on a call already refused rc 1 at both ends; behaviour is correct at this head, and two self-test lines would pin it
- `unk` is a global that the shim never initialises, so an inherited environment variable named unk relabels a refused record-issue comment write as "unknown gh api flag ZZ" (ev/env-unk-leak.txt). The call is still refused, rc 1. Carry: dismissed: stderr label only, fail-closed, and it needs an inherited env var named unk, which no tree caller sets
- `gh api --allow-escape-sequences=true`, a spelling gh accepts for a boolean, is refused as an unknown flag, because the `--*=*` arm checks API_VAL only. Carry: dismissed: fail-closed, and the one tree caller, merge_train.job_log, passes the bare flag

## Notes

- Closing self-audit: `carry_audit.py check --body verdict.md --pr-group R10-HOTFIX-SHIM-ESCAPES` exited rc 0 but reported "0 finding item(s)". It did not parse the three `## Findings` bullets, so their Carry markers were not checked by that run.
