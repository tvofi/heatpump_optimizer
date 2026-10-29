# Proposal triage, session s7, batch 59 (P273)

The rolling batch (V182) after batch 58 (#2934, merge-verdicted at
`56e61dc9edbb61c293b22254928ad8e1548b1bb6`). Facts were read at origin/main
`b0b2d7697f8c5baaef2c082d9bf3242b57249e68`.

## P273: card docs may still show the pre-R10-CARD-VOICE setup drawing

Verdict: REJECT. The measurement the proposal asks for comes first, and this seat took it. It
finds no drift, so the size-S docs fly-in would have nothing to change.

Source: `proposals.md` V185 (orchestrator, 2026-10-28T22:00Z). It cites item 4 of "Decisions for
the owner" in the card-symbols pre-study, `docs/design/card-symbols/NOTES.md` on
`probe/card-symbols-design` `2cc4d5ebc89657e4103c09447fc2d0e4c7adfe40`: "the docs/figure drift in
`docs/dashboard-card.md` and `docs/img/model/` (they still show the coil spring and the line-art
silhouettes)".

Instances:
- **The premise predates the fix.** The pre-study commit is dated 2026-10-20T15:17:11+02:00 and
  does not contain #2841 (`git merge-base --is-ancestor 75ac45353 2cc4d5ebc` is false). #2841
  merged on 2026-10-26 as `75ac453534e10c0a6ef88533ad5ff375cd6ca333`, and its own diff rewrites
  `docs/dashboard-card.md` (44 lines) and all three `docs/img/model/hydronic-*.svg`
  (`git show --stat 75ac45353`).
- **The spring is the shipped design, not a leftover.** In the card at main, the wood tank's type
  disc "is the coil's spring while a coil is configured in it, dimmed while that coil is not
  modelled" (`heatpump-optimizer-card.js:4002-4008`, glyph `SETUP_BADGE_GLYPH.coil`). The pipe
  of a configured but unmodelled coil is drawn dashed (`:3796`). So the four `spring` hits that
  V185 counts (`docs/dashboard-card.md:737-772`) describe what ships: the spring, its dimming,
  and the dashed pipe.
- **The silhouettes are gone from the figures.** The only `silhouette` match in each
  `hydronic-*.svg` is the card's own inlined comment saying the hand-drawn silhouettes were
  replaced (`heatpump-optimizer-card.js:4719`). No silhouette is drawn.
- **The figures equal the shipped card's render.** `tests/setup_qa_render.mjs` was run on a
  `git archive` of origin/main, with `HPO_QA_OUTDIR`/`HPO_QA_PREFIX=hydronic-`. All three outputs
  are byte-identical (`cmp`) to the committed `docs/img/model/hydronic-{coil,single-buffer,two-tank}.svg`.
  They were last regenerated in `c62c56cb5` ("regenerate the setup figures"). Three card commits
  landed after it, none in the setup drawing: `99367cbc3` (a receipt string), `c89e5b5db` (house
  grade), `59c744f4c` (a pop-up CSS comment).
- **Control.** The comparison can fail. In the archived copy, the coil glyph's arc
  `c1.3-2.9 2.6-2.9 3.9 0` was changed to `c1.3-2.0 2.6-2.0 3.9 0` and the figures were
  re-rendered. `hydronic-coil.svg` then differs (2 lines) while the two figures without a coil
  stay identical, which is exactly where the spring is drawn.

Cost: none further. A fly-in would cost a fixer seat and a review seat to land an empty diff.

Binding: the measurement refutes the premise. There is nothing to fix.

Residual, not a proposal: `docs/` is INERT in `tests/closure.py`, so a future change to the setup
drawing selects nothing that re-renders these figures. `tests/card_drift.mjs`'s header already
names that gap (#558 C2/C3), and `tests/setup_qa_render.mjs` names the hand-drawn case (#558 B9). This ruling takes no position on it.

## P274: cloud fixer commits carry identities the privacy guard refuses, found only at the opener

Verdict: ACCEPT, narrowed. Both halves go to R10-FLY-NO-FOOTERS (`carries-open`), the group that
already holds P253's carry on the same guard. The identity pin is prevention and lands first. The
code-ref guard in `body_push.sh` is the detector.

Source: `proposals.md` V186 (orchestrator, 2026-10-28T22:30Z).

Instances:
- **V186's three, as reported.** `r10-fly-sweep-defaults` and `r10-fly-instruments-split` had
  `noreply@localhost` authors. `email_leaks` refuses domain `localhost`
  (`tools/audit/seat/ref_privacy.py:244`), so a refusal at the opener is consistent, but no
  original SHA was recorded and this seat did not reproduce them. `r10-fly-prepr-summary`
  `4a7ccd930` is authored and committed by `Claude <noreply@anthropic.com>`. It **passes**
  main's guard (`ref_privacy.py guard --ref x --commits 4a7ccd930 --over origin/main`, rc 0),
  because `email_leaks` does not refuse that domain yet. That is the hole P253 closes. So this
  third instance cannot have been a refusal by main's guard.
- **The measured class.** `git ls-remote origin 'refs/heads/handoff/*'` lists 153 refs: 118 are
  fully on main and 35 are not. Across the 35, the commits not on main carry these author and
  committer pairs: 951 tvofi noreply, **28 `noreply@anthropic.com`**, 9 github-actions and 2
  `seat@users.noreply.github.com`. The 28 sit on 8 refs, all pushed on 2026-10-28:
  `r10-buffer-store` (3), `r10-cop-gate` (3), `r10-fly-rowonly-base` (1), `r10-learner-default`
  (1), `r10-orch-beatd` (3), `r10-rca-friction-residue` (4), `r10-review-carry` (6) and
  `r10-review-carry-pr` (7). On main since 2026-10-21, 424 of the commits are authored
  `noreply@anthropic.com` (`git log --since=2026-10-21 --format=%ae origin/main`).
- **Why it matters now.** P253 (`s6-batch51.md`, held carry on R10-FLY-NO-FOOTERS) adds class
  `anthropic-identity` to `email_leaks`. Once that lands, every one of those 8 refs, and every
  later cloud fixer whose runner identity is unset, is refused at `handoff_push.sh:141` /
  `app_push.sh:376`. That is the opener stall V186 prices at 5-10 orchestrator minutes each.
  P253 put "a cloud_dispatch.py prompt line" out of scope. These counts change that answer.
- **Where the guard runs today.** Commit identity is judged only at the opener
  (`handoff_push.sh:141`, `app_push.sh:376`). `body_push.sh:77` guards the body commit only, and
  `prepr.sh`'s `privacy_line` judges the lines a diff adds, not commit identity. The cloud fixer
  prompt (`tools/audit/seat/cloud_dispatch.py`, `_prompt`, role `fixer`) sets no git identity. The
  reviewer arm already pins one for its verdict commit (`-c user.email=seat@users.noreply.github.com`).

Accepted (narrowed), carried to R10-FLY-NO-FOOTERS:
1. **Prevention.** The `fixer` and `probe` setup text in `cloud_dispatch.py` tells the seat to
   run `git config user.name hpo-fixer && git config user.email
   70032254+tvofi@users.noreply.github.com` before its first commit. This is the seat preamble's
   identity. The self-test asserts the line is in the rendered fixer prompt. This lands with or
   before P253's refusal arm, never after it.
2. **Detector.** `body_push.sh` fetches `refs/heads/handoff/<topic>` and runs `ref_privacy.py
   guard --ref handoff/<topic> --commits <that sha> --over refs/remotes/origin/main` before it
   pushes the body. On a refusal it pushes nothing. The body ref is the return signal, so a failing
   code ref never reaches the opener. Self-test arm: a code commit with a `localhost` author is
   refused and no body ref is written; re-authored, it passes. Null control: commits already on
   main are not judged.
3. Not built: rewriting any history, or a guard inside the cloud harness itself.

Sequencing for the orchestrator, not a carry: when P253's refusal arm lands, the 8 refs above are
refused at the opener unless they are re-authored first, or merged before it lands.

Cost: about 1 prompt line plus 1 self-test assert in `cloud_dispatch.py`, and about 10 lines plus
1 self-test arm in `body_push.sh`, on a group already open. Nothing new in CI, no new file and
no extra API call.

Binding: the counted class. 28 commits on 8 open refs today, each a future opener stall once P253
lands, against a two-file change in a group already carrying P253.

## P275: carry_audit over-fires on verdict lines, and the train PARKs a green merge-verdicted PR on it

Verdict: ACCEPT, narrowed to a verdict self-check at review time (a stronger form of option (b)), to
R10-ORCH-REVIEW-PACKET. Option (a) is REJECTED. Option (c) is not taken.

Source: the orchestrator's message of 2026-10-29T04:14Z, not yet entered in `proposals.md`. It
offers options (a), (b) and (c).

Instances:
- **The two PARKs named** (`~/hpo-orch/r10s6/train.log`, `PARK #2914 findings` and
  `PARK #2887 findings`). They were re-run with origin/main's `items()` on the verdict files from
  `verdict/2914` `7e793cdb3` and `probe/rev-2887-d83aee5b` `156ddb202`:
  - `c63349c9` (#2914) is flagged `non-blocking` and is **a correct fire**. "V149 (FLOW-BOARD):
    not blocking. Its ruling is a DEFER in s6-batch47.md ..." is a reviewer's note that this PR
    does not settle, and it carries no `Carry:`. The reviewer prompt already requires one
    (`cloud_dispatch.py`, role `reviewer`: "Each finding this PR does not settle ... ending in its
    own `Carry: ...`").
  - `da4b2420` (#2887) is flagged `evidence` and is **an over-fire**. It is a `## Evidence` line,
    and DEFERRED matches only "residual" inside a carry's own title ("over-booking residual").
- **The findings-PARK record.** The seat ledger and train.log show 7 PARKs on the findings rule
  in 5 days: #2709, #2770, #2876, #2881, #2914 and #2887, plus #2764 on a different cause. #2709
  is not classified here. Of the other five, #2876, #2881 and #2914 are verdicts that hold a note with no `Carry:` (the auditor was
  right), and #2770 and #2887 are evidence-line over-fires. Each costs about 1 h of train time
  plus a hand `body_patch` (V187's figure).
- **The class, over every verdict.** `git ls-remote origin 'refs/heads/verdict/*'` gives 396
  verdict files. With origin/main's classifier, 82 of 367 merge verdicts hold at least one flagged
  item with no `Carry:` of its own. Since 2026-10-26, 17 merge verdicts of 125 verdicts do: 13
  `section`, 8 `non-blocking`, 8 `evidence` and 1 `under lead` items. This is an upper bound on
  PARKs, since a body can route an item by id.
- **Option (a), measured.** Of the 16 `evidence` flags in the corpus, most are prose describing a
  check or a move, for example "residual" as a field (`MeasuredCop.residual`, #2917 three times)
  and "blocks no merge" (#2827, #2937). At least one is a real defect left in place: #2612
  `434dcf9d`, 4 unpinned mutation sites added by the diff. The two low-risk narrowings were tried
  on a scratch copy: DEFERRED and NONBLOCK not read inside a code span, and NOT_REQUIRED also
  freeing "blocks no merge". They clear 2 of the 16 (#2554, #2836). Clearing the prose ones
  means not reading DEFERRED words in `## Evidence` at all, which also drops #2612's real one.
- **Where the auditor first reads a verdict.** Only `tools/audit/seat/queue_pre_flight.py:178-204`
  does, at train time, and no publication step does (`bus.sh` and `cloud_relay.sh` do not call
  it). `review_packet.py` already runs `carry_audit.py check --body` on the body (`:327`), and
  `carry_audit.py check --body FILE --comments FILE` already reads a verdict passed as a comment
  (`:560-562`, `finding_rows` `:387`).

Accepted (narrowed), carried to R10-ORCH-REVIEW-PACKET:
1. `review_packet.py`'s rendered packet gains a closing "before you return the verdict" step. It
   gives the exact command that audits the reviewer's own `verdict.md` against the PR body:
   `carry_audit.py check --body <body> --comments <json: [{"id": 0, "body": <verdict.md>}]>`.
   Every item it reports gets its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`,
   and an evidence line flagged by wording gets `Carry: dismissed: evidence, not a finding`. The
   reviewer returns the verdict only at rc 0.
2. `fix-review.md` gains one sentence binding that step. This is policy, and it merges on the
   owner's approving review or under mandate 6329234399.
3. Self-test: a packet rendered for a fixture PR contains the command. A fixture verdict holding
   #2914's `c63349c9` text gives rc 1, and gives rc 0 once the `Carry:` is added. Null control: a
   verdict whose only notes are routed gives rc 0.

Rejected: (a). Narrowing the predicate clears 2 of 16 measured false positives at low risk.
Clearing the rest would silence a guard whose PARKs were right in 3 of the 5 classified cases.
Under item 1 an over-fire costs the reviewer one `dismissed:` line at review time, not a PARK,
so what (a) would save falls to near zero. (b) as worded, a prompt rule, is already in
`cloud_dispatch.py` and did not prevent #2876, #2881 or #2914. Item 1 replaces the rule with the
check that enforces it. Not built: a relay-side refusal, since the cloud reviewer has exited by
then and the repair would fall back to the orchestrator.

Cost: about 10 lines in `review_packet.py` and its self-test, plus one policy sentence. Each
review gains one local command of a few seconds. No CI, no API and no new file. The orchestrator's
hand-dismissal path stays R10-FLY-CARRY-DISPOSITION's (not started).

Binding: 6 verdict-borne PARKs in 5 days at about 1 h of train time each, all catchable by the
reviewer before return, against about 10 lines in a group already open on the same file.
