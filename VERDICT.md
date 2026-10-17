Fix review: merge e1048139659b3e995de63df5ac809ca4ddf8bc0d

bus-nonce: e270f5bb078eff733e4f62ea7a48bfb6

Round 2. My round-1 `blocked ... harness: class-rule-missing` is answered, and I
re-ran the class myself rather than reading the answer. Detached worktree at the
head; `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`
empty before step 1. Merge base `e3f3b312fff572904f24d78a44a2c4492b1a8ddb`.

RESULT 1 mutation proof: all four named mutants redden exactly one check each,
in their own worktree at this head, baseline `ALL 2343 ENTITY CHECKS PASSED`
(its `  FAIL ` lines are embedded negative-control output, reproduced unchanged
by every mutant). Each FAIL-set diff against the baseline is one added line.
  M1 `> s` -> `> s + 1` -> `1 of 2343`, the multi-issue check, all twelve rcs 0;
  the scope null control and the two-keywords control stay green; the harness
  reads `seams_open=86`.
  M2 delete `gsub(/[.!?][[:space:]]+/, "&\n", t)` -> `1 of 2343`, the SCOPE null
  control, `{'part-of': 0, 'leaves-open': 1, 'bare-reference': 0, 'heading': 0}`;
  the multi-issue check stays green; harness `seams_open=0`,
  `refused_but_not_seam=8` naming `punct:! punct:? punct:.. word:i.e.
  not-owned:leaves-open not-owned:superseded-by not-owned:across-a-sentence
  not-owned:prose-mention`.
  M3 `c = " " clause[i]` -> `c = clause[i]` -> `1 of 2343`, the multi-issue
  check, all twelve rcs 0; harness `seams_open=86`, `refused_but_not_seam=1`
  `not-owned:two-keywords-one-clause`.
  M4 whole arm-1b block deleted -> `1 of 2343`, the multi-issue check; harness
  `seams_open=86`.
  M2 and M4 are the pair that matters: removing the arm cannot red a check about
  scope, and narrowing the scope cannot red the multi-issue check. Each pin is
  load-bearing for its own production lines, not for the other's.

RESULT 2 harness, both ends, run by me: the committed
`dev/audit/harnesses/closing_keyword_ownership.py` prints
`shapes=102  seams_open=0  refused_but_not_seam=0  refusal_not_gating=0`, rc 0.
`--script` on the round-1 head's own `tools/pr/preflight.sh` prints
`seams_open=73`, rc 1 — so the matrix is not vacuous, and the six seams my
round-1 evidence measured are rows of it. `--corpus` over the 200 most recently
merged PRs prints `corpus_clause_scope=0 []` and `corpus_whole_body=25`.

RESULT 3 null controls, re-run by me: the changed-template shapes pass —
`Closes #2231. Closes #2230.`, `Closes #2231. See #2230.`, `See #2231 and #2230
for context.`, `Closes #2231.` then a blank line then `Part of #2230.` all exit
0 — and the corpus is the false-positive floor (`corpus_clause_scope=0` at every
lane count I read). The twelve multi-reference shapes all refuse.

RESULT 4 claim files: neither `tests/golden/claimed_drift.txt` nor
`card_claimed_drift.txt` nor any fixture is in the diff, so no drift claim is
owed.

RESULT 5 VERSION: `VERSION`, the manifest version and the `RELEASE_NOTES.md`
heading are absent from the three-dot diff.

RESULT 6 class CLOSED, and this is the round-1 block answered by measurement:
  my six separable seams (`/`, `&`, `+`, `(`, `;`, a plain word, and a newline
  split) all exit 1 through arm 1b at this head, where each exited 0 at the
  round-1 head;
  a hunt of my own outside those six — a full issue URL, `owner/repo#N`, `GH-N`,
  `Closes:`, `FIXED`, `Resolved` as the first reference, a keyword and its
  reference split across a newline, two multi-reference clauses in one body —
  finds no under-fire; every one refuses through arm 1b;
  the rule is stated, committed and independently implemented, and the body
  tabulates every class seam with a disposition. `seams_open=0` is the claim
  under generated shapes; my instances are the same claim under real ones.
  One residual in the OTHER direction, named so it is not silent: the ownership
  count is per clause, so a same-clause prose mention after a closing keyword is
  refused too — `Closes #2231 because of #2230.`, `Closes #2231, as reported in
  #2230.` and `Closes #2231 (the cause is #2230).` all exit 1. That is loud, it
  carries a remedy line ("give each reference its own keyword, or move it out of
  the closing sentence"), and it refuses 0 of the 200 merged bodies, so it is an
  over-fire observation rather than a seam.

RESULT 7 head: the body's `## Head` names
`e1048139659b3e995de63df5ac809ca4ddf8bc0d` and the authored code head
`2f7aafdc856db407ac2407c4231d547899546b88`; the head is that SHA and the
merge base is `e3f3b312f` as stated. Confirmed from the range, not the body.

RESULT 8 figures: eight of ten re-derive exactly, two do not, and I report them
rather than confirming them.
  Re-derived: the corpus `0` and `25`; the no-list count over the 200 (`27`);
  the twelve round-1 bodies (`12/12` exit 0 at this head); `MODE: SCOPED -- 2
  script(s) run` (CI's own fast job printed `MODE: SCOPED -- 2 script(s) run, 31
  scoped out`, identical); `102/0/0/0`; `--script` on the round-1 head `73`; the
  nine-body over-fire from round 1.
  NOT re-derivable, 1: the body's "with the workflow's own derivation, 6 still
  exit 1 -- #2007 #2008 #2009 #2010 #2015 #2041". Running its own two inputs
  gives **5**: `#2009 #2010 #2015 #2041 #2341`. `#2007` and `#2008` are outside
  the `--limit 200` window (they are in at `--limit 202`) and `#2341` — which
  closes `#2267`, a roster `issues` number no group names in `fixes` — is inside
  it and refuses at `intended=0`. The body's own hedge ("re-take those against a
  newer tip") does not cover this: `origin/main` is still `e3f3b312f`, the tip it
  names. The RULE the bullet demonstrates still holds — the derivation does
  refuse a Part-of close — so this is a stale enumeration, not a false claim.
  NOT re-derivable, 2: `tests/entities.py:18410`'s failure detail says "keeping
  the count across the blank line would refuse 24 of the 200 most recently merged
  bodies". No scope reproduces 24 — clause 0, sentence-only 3, paragraph 7,
  whole-body 25 — and the same file's own comment at `:18361`, the harness and
  `preflight.sh:68` all say 25. Off by one, in a detail string only rendered when
  the check fails; the file contradicts itself.
  One more, minor: "`closure.py lane-plan` is identical with and without them"
  holds for this pull request's own scoped two-script plan (identical at lanes
  1-4, measured) and not for `--all-scripts` (non-identical at lanes 1-4,
  measured). The load-bearing half — this PR's gate is unaffected — is true.

RESULT 9 harness: committed, in `dev/audit/harnesses/` (fixer.md step 18's home),
independently implemented from the awk it grades, with `NOT_OWNED` as a
scope-null control and `--script` as the cross-head control. It reds on the
round-1 arm and passes on this one, which is `defect-root-cause.md`'s
demonstration for a check.

RESULT 10 forward-carry: `none` is right. The same-stage sibling seam my round-1
verdict named is closed in this diff — `fixer.md` step 8's first disposition —
rather than routed to an issue, and the rule's remaining shapes are the generated
matrix and the `NOT_OWNED` table, each with its exit code.

RESULT 11 red checks, read off the commit's check-runs API, not the body:
  `coverage-ratchet` is red at THIS head too (00:35:33Z) and is named and
  answered in `## Red checks`; the answer is the one I measured in round 1 and it
  still holds, and the shortfall has widened rather than narrowed — `4 module(s)
  below the 95.0 % per-module floor: early_cutoff.py 81.53 %, coordinator.py
  84.14 %, sysid.py 91.28 %, price_model.py 94.77 %`, every module absent from
  this diff. It is not one of the ruleset's 17 required contexts and does not
  gate the merge; all seventeen are green.
  `pr-contract` at the round-1 head: red once at 20:29:55Z and green at
  20:34:14Z on the same commit, as the body says. I read the failing job
  (`117181315015`): the red was
  `check 'coverage-ratchet' is red and '## Red checks' does not name it` — the
  body check doing its job on the round-1 body. This revision's `## Red checks`
  names it and answers it, and `pr-contract` is green at this head, so the
  trigger is answered; the body's one-line account of that red is thinner than
  the rest of the section, not silent.

RESULT 12 head re-read before posting: still
`e1048139659b3e995de63df5ac809ca4ddf8bc0d`.

RESULT 13 conflict: none. `git merge-tree --write-tree origin/main
e1048139659b3e995de63df5ac809ca4ddf8bc0d` exits 0 with no conflicted path;
GitHub's `BLOCKED` is the ruleset awaiting the code-owner review.

RESULT 14 metric-gamed: the diff moves one instrument, `tests/closures.json`, and
both movements are earned. The `inert_reads["tests/harness_headers.py"]` entry is
the new harness, which `inline_scan` reads as a child process; the `closures`
job at this head prints `committed closures cover every file this run touched`,
and `closure.layout_errors` is `[]`. The `seconds` move `99.7 -> 241.1` is the
same one extra file, and CI measured `tests/harness_headers.py` green in 188 s,
so the recording is the right order; the scoped lane plan for this pull request's
two scripts is identical with and without it at lanes 1-4. No structure or policy
budget moves (`tests/structure.py`: `STRUCTURE RATCHET PASSED`, and none of the
four changed paths plus the harness is in `POLICY_GLOBS`). No golden, no mutation
ledger, no claim file.

RESULT 15 architecture-unsound: none on added lines. The change consolidates the
closing-reference spelling into one `CLOSING_REF` in `preflight.sh`, which is an
improvement on the round-1 head's two in-file spellings and is what closes the
observation I raised there; the harness lives where step 18 sends it; no
`homeassistant` import, no side effect beyond printing, inputs on stdin.

RESULT 16 round: round 2, a repair after a block, not a re-cut.

Merge. The two unreproducible numbers in RESULT 8 are body-and-detail
corrections, not defects in the fix — I am naming them here rather than letting
them pass as confirmed, per step 8; the code, the pins and every load-bearing
figure are sound.
