Fix review: merge d240ff73d16e39f113b0527ee077076cc7e9a201

bus-nonce: a84c86c8dc26e7f1c5e8462190ea637e

## What I measured

Head **d240ff73d16e39f113b0527ee077076cc7e9a201** — the head the PR body
names, and still the branch head at `git ls-remote` immediately before this
post. One commit on top of the merge of `origin/main` into `6f220a553`. Three-dot
diff against merge base `c729bb32e`: 4 files (`tools/audit/seat/bus.sh`,
`dev/governance/roles/orchestrator.md`, `dev/governance/config/policy_budgets.json`,
`dev/programme/delivery/2115.md`).

**Instrument: mine, not the fixer's.** `bus.sh --self-test` is the fixer's own
arm harness and I did not measure with it. I drove `push-verdict` through a real
`dispatch` over a throwaway bare repo, with `HPO_BUS_STATE` pointed at a temp dir
I own — never the live bus state (`evidence-2115/arm-a9.txt` records the state
path each run used). Scripts:
`/Users/timmalmstrom/hpo-seats/r9rev-2115/arms.sh` and `a9.sh`; bus.sh copies at
head (sha256 `fb7fff78…`) and at the merge base (sha256 `f8706db3…`).

The fixer's self-test does pass at the head: **48 checks, 0 failed** — I ran it
separately, and it is not what my numbers come from.

## RESULT lines — both ends, one harness

```
arm                                              pre-fix (c729bb32e)   fixed (d240ff73d)
A1 correctly bound nonce                         ACCEPT rc0 + ref      ACCEPT rc0 + ref
A2 nonce no dispatch minted                      ACCEPTED rc0 + ref    REFUSE rc1, no ref
A3 another pull request's nonce                  ACCEPTED rc0, moved   REFUSE rc1, ref unchanged
A4 nonce dispatched at the old head (#2075)      ACCEPTED rc0, moved   REFUSE rc1, ref unchanged
A5 fresh dispatch at the new head (remedy)       ACCEPT rc0 + newref   ACCEPT rc0 + newref
A6/A6b two nonces, same (pr,head)                ACCEPT rc0 + ref      ACCEPT rc0 + ref
A7 no dispatched record exists at all            ACCEPTED rc0 + ref    REFUSE rc1, no ref
A8/A9 divergent $S                               ACCEPTED rc0 + ref    REFUSE rc1
```

**Mutation proof (step 1), re-run at the head.** Removing the single named
production line — `why=$(dispatch_binding "$v" "$pr" "$hsha") || die …` — flips
A2, A3, A4 and A7 back to ACCEPTED with a ref pushed, and leaves A1/A5/A6
accepting. The refusal arms depend on that line and on nothing else
(`evidence-2115/arms-mutant.txt`).
`bus.sh` is INERT: `closure.py select` prints `MODE: SCOPED -- 0 script(s) run,
33 scoped out` with bus.sh among the 4 changed files, and the mutation lane CI
does run is the self-test, wired at `.github/workflows/governance.yml:332`
(`instrument-self-tests`, green).

## 1. Does it refuse the unbound and still accept the bound? — yes, both arms

Three refusal classes, each verified in its own arm, and the refusal message
matches the class it claims (verbatim, `evidence-2115/msgs-head.txt`):

```
unknown nonce <n>: no dispatch in <state>/dispatched minted it; mint one at this head with …
nonce <n> belongs to pull request #12, not #7; mint a dispatch for this one with …
nonce <n> was dispatched at head 1111…, not the head 2222… this verdict names; mint a fresh dispatch …
```

The false-refusal hunt (a refusal that also rejects a legitimate verdict is worse
than the bug) found none in the supported configuration. A1, A5, A6 and A6b are
legitimate verdicts and all still propose: the correctly bound nonce; the body's
own remedy, a fresh dispatch at the moved head; and **two dispatches for the same
(pr, head)**, where the `awk '$4 == n'` match is on the nonce, so the second
nonce resolves to its own record rather than being shadowed by the first.

## 2. Is the check at publish time? — yes

Every refusal exits non-zero with `bus: REFUSE: push-verdict: …` — push-verdict's
own die, not a later gate — and in every refusing arm **no `review/<pr>` ref was
created**, while A3 and A4 confirm an existing `review/7` tip is byte-identical
after the refusal. The call sits at `bus.sh:157`, before `mktemp`, before the
tree is built and before `append_commit`; nothing is pushed on a refusal.

## 3. Does `orchestrator.md` §7 state what the check does? — yes, and it under-claims rather than over-claims

The merged operative sentence (read against the code character for character):

> a move that re-issues the verdict needs a fresh `bus.sh dispatch` at the new
> head before the reviewer publishes, since `push-verdict` refuses a nonce whose
> dispatch head is not the head the verdict names.

The code is `[ "$rh" = "$3" ]` at `bus.sh:119`, where `$3` is the head taken from
the verdict's first line by `verdict_sha`. "the head the verdict names" ↔ `$3`;
"the nonce's dispatch head" ↔ `$rh` read from `$S/dispatched` field 2. The rule
claims nothing the check does not enforce. It is silent about the other two
refusal classes (unknown nonce, another pull request's nonce) — a rule that
states less than the check enforces, which is the safe direction and not the
defect class this programme keeps finding.

Markdown is intact: the insertion replaces a full stop with a semicolon inside
the existing `A head that moves under a review costs that review, and it has
happened twice` clause and leaves the following `**A conflict with main after the
handoff is resolved by merge, never a re-cut**` bold run closed and unchanged.

## 4. Is the budget raise the measured value? — yes, exactly, re-derived with the tree's own instrument

`node tools/policy/policy_lint.mjs --budgets` at the head, the row for
`tools/audit/briefs/orchestrator.md` (the budget key that `trackedFiles`' `canon`
still spells for `dev/governance/roles/orchestrator.md`):

```
tools/audit/briefs/orchestrator.md   293  293   4142  4142
```

Measured 293 lines and 4142 tokens against a cap of 293 and 4142 — the raise is
the measurement with zero slack, not a guess and not the old value padded. I
re-derived the token figure independently from the blob: head bytes 16566,
`Math.round(16566/4)` = 4142; no trailing-empty element is counted, so the line
count is 293. The raise was necessary: at the merge base the same file measures
290 lines / 16361 bytes = 4090 tokens against the old cap of 291 / 4096, so the
added prose would have breached both caps without it. The run exits 0 with no
error line, and CI's `policy-docs` job — which runs the whole linter, not just
`--budgets` — is green. `corpus_tokens` (59951) stays inside its band (cap 59591
+500); no aggregate cap was touched; `_measured`/`always_loaded_tokens` unchanged.

**Not metric-gamed (step 14).** The movement is paid for by the mechanism the
body names: delete the two added policy lines and the cap returns to its old
measurement, so the movement does not survive the removal. No other number the
diff moves.

## Notes recorded, not blocking

**(a) The reader's own scope of the nonce is `(pr, head)`, not `(pr, head, reviewer)`.** A nonce minted for reviewer X is accepted from reviewer Y at the same (pr, head) — the check reads `$4` and never `$3`. That is out of the class this PR names (the body states the binding as the pull request and the head) and it is unchanged from `confirm`, which reads the same three fields, so it is not a seam the body's rule fails to return. The fixer's arm table and the code agree on three classes; I found no fourth *inside* that binding.

**(b) `$S` divergence now refuses at publish where it used to be accepted (arms A8/A9).** The header discloses this ("NONCE VISIBILITY"), and the body repeats it. I measured it: an orchestrator that dispatches with a command-scoped `HPO_BUS_STATE` while the reviewer resolves the default `$HOME/.zcode/bus` gets a refusal at publish, where the pre-fix tree proposed and the orchestrator's `confirm` then succeeded. Nothing in the tree sets or exports `HPO_BUS_STATE`, so the default path is consistent for every seat and the divergence needs a per-command override; it is self-inflicted, refused loudly, and names the one-command remedy. Worth the orchestrator knowing that "one session on one machine" is necessary but not sufficient — the variable must also be *exported* consistently — but it is a disclosed precondition, not a defect and not a new late failure.

## Contract checks

- **Head**: the SHA in the PR body is the SHA I measured, and the head is unchanged at post time.
- **VERSION / manifest / RELEASE_NOTES**: not in the diff. **Claim files**: untouched — no `tests/golden` or card fixture is in the three-dot diff, so the drift check is vacuous by construction; CI's `env-matrix` is green. (I started `env_drift.py --all` and stopped it rather than burn twenty minutes re-running what CI already grades; the vacuity is from the diff's file list, not from the run.)
- **Conflicts**: `git merge-tree --write-tree origin/main d240ff73d…` exits 0 — no conflict, and no `MERGE-CLAIM: refused` marker to read.
- **Red checks**: I read the commit's own `check-runs` API across the whole range (`0ef609458`, `6f220a553`, `78a067541`, `d240ff73d`), not the body's account. The only failing check anywhere in the range is `budget-raise-gate`, at the last two heads. The body names it and answers it: it is the raise's own gate, it reads the two raised values, and no cheaper detector reads a raise. Answered, and per my dispatch I leave the raise's owner gate to the orchestrator.
- **Forward carry (step 10)**: the destination the body names is `dev/governance/roles/orchestrator.md` §7, and the rule is there in this diff.
- **Architecture (step 15)**: `fixer.md` step 17's list is about the HA model/coordinator surface; this diff adds one predicate function, one call site and one header paragraph to the instrument that owns dispatch and confirm, and re-uses the existing `$S/dispatched` record with no parallel store. Sound on the added lines.
- **Sibling, not duplicate**: #2107 gates `dispatch` on the delivery row (`row_position.py`, `bus.sh`); this gates `push-verdict` on the dispatch. Different subcommand, different fact.
- **Round**: this is the first review round of this head.

The published verdict's first line parses as a merge; the change is a refusal
that fires earlier, names the fact that failed and the command that fixes it, and
takes nothing away from a verdict its own dispatch bound.
