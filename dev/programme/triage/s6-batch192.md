# Proposal triage, session s14, batch 192 (P614)

The bar and the denominators are batch 141's.

Sources:
- origin/main `ee64358be7`. Every line number below is at that commit.
- `handoff/audit-r10-roster` at `d48ffabbf1`, `dev/programme/rosters/wave-r10-groups.json`:
  461 groups, read 2026-11-11T12:02Z.

## P614: BRIEF-LINT-BASENAME-PATH

Verdict: REJECT. `brief_lint.mjs` is not changed to refuse a directory-qualified path that
resolves only through its basename. The mechanism the proposal describes is real. But no live
brief carries such a path, and a refusal built on the current tokenizer would be wrong on about
nine in ten of the tokens it fires on.

Source: queue line 292, 2026-11-11T11:59:59Z, a side observation from feature triage f5:
`brief_lint.mjs` did not report `tools/pr/ref_privacy.py` (the real file is
`tools/audit/seat/ref_privacy.py`), although `brief-citations.md` says a cited path must resolve.

Instances:
- **The mechanism.** `lookupPath` (`tools/policy/brief_lint.mjs:158-163`) returns the exact path
  if it is tracked. Otherwise it returns the first tracked file with the same basename. The
  comment at `:154-157` says this is deliberate: a bare filename in prose does not commit to a
  directory. The fallback does not tell a bare name from a directory-qualified one.
  - Run at `ee64358be7`, `resolvePathToken('tools/pr/ref_privacy.py')` returns
    `tools/audit/seat/ref_privacy.py`. The exact path returns itself. A made-up basename,
    `tools/pr/nonexistent_xyz.py`, returns `null`. So the observation reproduces.
  - The reported instance is in no landed brief: `grep -c 'tools/pr/ref_privacy.py'` on the
    roster file at `d48ffabbf1` gives 0. It was fixed in the draft before the draft was queued.
- **How many briefs carry one today.** The harness takes every group's `brief` and `carry` text
  on the roster at `d48ffabbf1`. It tokenizes them with `PATH_TOKEN_RE` (`:352-355`, the same
  regex brief_lint uses), keeps the tokens that contain a `/`, and resolves each against
  `git ls-tree -r --name-only ee64358be7`. "Live" means `resume.stage` is `not-started` or
  `in-progress` (48 groups).

  | | slash tokens | exact | only through the basename | resolve nowhere |
  |---|---|---|---|---|
  | live (48 groups) | 291 | 206 | 19 | 66 |
  | all other groups | 2,100 | 1,796 | 121 | 183 |

- **What the 140 basename-only tokens are.** Each was read and classified by hand.
  - 91 are a suffix of the real tracked path. `PATH_TOKEN_RE` starts at `\b`, so it drops the
    leading dot: `.github/workflows/gate-sweep.yml` is tokenized as
    `github/workflows/gate-sweep.yml`, and `.claude/settings.json` as `claude/settings.json`.
    The basename fallback is what currently passes these correct citations.
  - 2 are an escaped newline read as part of the path (`\ntools/...` gives `ntools/...`).
  - 33 are not paths into this tree. They are slash-joined prose lists
    (`merge_pr.sh/proof_watch.py`), seat worktree or `HERE/` prefixes, REST API paths
    (`repos/.../actions/workflows/ci.yml`), an upstream Home Assistant path, a `DRAFT_WT/`
    placeholder, two files their group creates, or a citation the brief itself marks as no longer in
    the tree (R10-ROUND-PLAYBOOK-FINAL: "a path the tree no longer has").
  - 14 name a real file in the wrong directory, and all 14 are in done or absorbed groups. Most
    point to where a file lived before a later move: the role contracts and `prepr.sh` once sat
    under `tools/audit/`, and `ref_privacy.py`, `moved_paths.py` and `handoff_push.sh` were cited
    one directory away from `tools/audit/seat/`. The rest: `field_coverage.mjs` under
    `.claude/workflows/` instead of `tools/policy/` (x2), the `k1725_blas_kernel_gap.py` harness
    under `tools/` instead of `dev/audit/` (x2), two round-10 `study-reseed` harnesses under `tools/`
    instead of `dev/audit/rounds/`, and one `arch3-s3` patch directory (really `arch-s3`).
  - Live groups: 0 of 19 basename-only tokens name a wrong directory.
- **Null control: the proposed refusal run over the same corpus.** The rule would be "a token with
  a `/` that is not tracked exactly is refused". On the 140 basename-only tokens it fires 140
  times, and 14 are true. That is 10.0% precision, and 0 of 19 (0%) on live briefs. Before any
  refusal could fire usefully, the tokenizer would first need a dot-prefix fix.
- **What a wrong directory costs a seat.** The seat opens a missing path, then finds the file by
  basename: one failed read and one search. That is a few hundred tokens, against a fixer run of
  10^5 or more. The 14 instances are spread over 413 finished groups. Even if every one cost a full
  extra tool round, the saving is far under 1% of fixer tokens. The bar is 20%.

Cost:
- A dot-prefix fix to `PATH_TOKEN_RE`. Every path class uses that regex, so the fix moves every
  rule family's acceptance.
- A refusal arm in `lookupPath` and a test per arm. `tools/policy/brief_lint.mjs` is 1,671 lines,
  a policy-tool hot file.
- Then a pass over every live brief, with 66 live tokens already unresolved. That count is outside
  this ruling.

Binding: the benefit measures 0 live instances and under 1% of fixer tokens at worst. The cost is
a regex change on a shared hot file, plus a refusal that is 90% false positive (100% on live
briefs) until that regex change lands. Even or marginal is REJECT. This is well below even.

Disposition:
- No group and no carry.
- Re-open trigger: this returns as a queue line if, with the leading dot kept by the tokenizer, 3
  or more live briefs at one roster head carry a directory-qualified path that resolves only
  through a basename in another directory. It also returns if a fixer or reviewer verdict records
  a review round lost to such a path.
