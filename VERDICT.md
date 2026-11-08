Fix review: blocked acd78b4d770d1666652baa9d94559aa3ea9f57eb class-open: the minor-defect rule maps only minor/low and major/critical while the roster field it names carries medium, high and normal for 299 of 388 groups, and the word-budget cuts dropped triage obligations undisclosed

bus-nonce: 0dfcd349b51c03f8784b615ea337077a

Round: second review of this head (the first verdict's push was refused for missing `Carry:` markers); reviewed again in full from detached worktrees at the head and at the merge base afc1586a4424f997ce70ed2003add9d7de93d6f6.

## Block

- The third rule's predicate has an unguarded domain. `proposal-triage.md` at the head says a repair "rated minor or low is no longer exempt" and "Major or critical ... skip the bar", and names the roster group's `severity` as the field read. That field on `handoff/audit-r10-roster` (9263aea2) holds high 90, low 56, medium 202, critical 8, normal 7, major 1, unset 24 (ev/severity.txt). Medium, high and normal (299 of 388 groups, including this group, `medium`) fall in neither branch, so the triage seat cannot tell whether such a repair is exempt; the "classified first" sentence covers only unset values. Fix: map the roster's real scale (say low/normal/medium -> bar, high/critical -> skip, or whatever the owner's "minor" means on that scale, asked if unclear) and name the values once.
  Carry: R10-FLY-TRIAGE-BAR
- The cuts that paid the word budget (proposal-triage.md was 489/489 words at the base, 487/489 at the head) removed obligations, not only prose, and the body calls them "cutting prose": dropped are "An ACCEPT runs its rule on each instance, result beside it"; "Git and local logs before the API"; the `Cost:` field's "the estimate"; the `Instances:` "or log" and "cite, don't carry"; "its PR records it" for an exemption ACCEPT; the cost enumeration's units (seat model x effort x expected runs, Pi-class CPU, hot files, review rounds); the source "its Proposals line"; "medium effort: rulings are checked against code"; and the definition of proposal-sourced text (`triage P<n>` / `proposal P<n>`). Each changes what the seat must do, outside both owner rulings (ev/proposal-triage.diff). CLAUDE.md rule 2 forbids deleting working functionality merely to fit; restore them or have the owner rule each cut, and list each in the body. If the words do not fit, stop and ask, per the brief's "pay by cutting, never raise".
  Carry: R10-FLY-TRIAGE-BAR

## Findings

- The finder's harness: the group has no committed finder's harness (a policy group from owner rulings); the self-test and git grep are the only instruments, run by me as listed under Evidence.
  Carry: dismissed: policy group, no finder harness exists to run; the self-test stands in

## Evidence

- RESULT head: `machinery_ratchet self-test: 54 checks, 0 failed`; base: `54 checks, 0 failed` (ev/checks.txt).
- RESULT mutant THRESHOLD 1/10: `FAIL exemption: exactly 20% refuses`, `... as floats refuses`, `54 checks, 2 failed`, matching the body. Extra mutant 1/4: 3 failed (21% cases and the positive control), so the cases pin the threshold from both sides. Restored: 0 failed.
- RESULT `rules_sync.mjs --check`: `RULES-SYNC ok`. `policy_lint.mjs --budgets`: proposal-triage.md 35/36 lines, 487/489 words at the head (base 34/36, 489/489); no `*budgets*.json` change in the diff. Body figures 35/487 against 36/489 re-derived.
- git grep over dev/governance, tools, .claude at the head for 10%/1/10/5% in the improvement/exemption/keep sense: only the two new "at least 10%" keep sentences remain (ev/grep.txt). The ratchet sites were all changed; unrelated percentages left alone as the body says.
- `git merge-tree --write-tree origin/main acd78b4d...`: rc 0, tree bb3f441c (ev/merge-tree.txt); no conflict.
- CI: `merge_train.py classify ... --pr 3310`: `GREEN acd78b4d770d1666652baa9d94559aa3ea9f57eb pending: none red: none` (ev/classify.txt). No red check owes a root-cause answer.
- VERSION, manifest and notes heading untouched (the diff has 7 files, none of them).
- Head re-read before return: refs/pull/3310/head is still acd78b4d770d1666652baa9d94559aa3ea9f57eb.
- The body's `## Head` section also names c7f4535d as a "main" figure, which I could not tie to anything; the head it states is the head measured.
