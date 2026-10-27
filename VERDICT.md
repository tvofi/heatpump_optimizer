Fix review: blocked 2724c87bb4e336561e7034eaf6b0142f4664371b class-open: step 6g's narrowed copy holds the generator's files but not the link targets C108 resolves, so a docs edit that adds a link to an in-tree file outside CLAIMS_INPUTS refuses a correct, re-recorded register, and the remedy the refusal prints cannot clear it (the whole-tree check passes the same commit)

bus-nonce: 01cfb6aad691e7e08ffbb06e84852a10

Head reviewed: `2724c87bb4e336561e7034eaf6b0142f4664371b` — `refs/pull/2853/head` and the branch tip re-read immediately before publishing; unchanged since dispatch. Worktree: detached at the head, created by me (`/tmp/rev-2853-1`), `git status --porcelain` empty. The fixer's tree and the shared checkout were not used. Findings are from the head's own code, driven both ends; the fixer's harness was not reused except where stated.

## B1 (blocking) — step 6g grades a copy that is not the generator's read set

**Claim.** The body, line 5: 6g "copies HEAD's inputs — … the paths `dev/audit/rounds/round4/D6/claims.py` reads". The enumerated list is presented as that read set, and `## Null control` presents byte-identity on this head as proof the narrowing is faithful.

**Evidence.** The generator reads more than the listed files. `dev/audit/rounds/round4/D6/claims.py:1209-1229` (C108) walks every relative link in `README.md`, `DISCLAIMER.md` and `docs/*.md`, resolves it against the document's directory and tests `.exists()`; only four hard-coded export-cut names are excused. So the generator's input population includes **whatever tree path a documentation link names** — it changes with the docs and no static enumeration can close it. The uncovered region is most of the tree: `tools/` except `tools/audit/archscore/ABOUT.md`, `tests/` except five entries, `dev/` except three, and the repo root except five files.

**Fixture.** Commit `eb7e1dee2` = this head + one line in `docs/architecture.md` linking `../tools/audit/seat/INSTRUMENTS.md`. The target exists in the tree; `docs/architecture.md` already links `../tools/audit/archscore/ABOUT.md` and `../tests/README.md` the same way, and both are inside the list — this is the same edit shape, one path over. The register was re-recorded **at the repo root on the full tree** and committed: C108 `true | 85 links, broken=[], of which removed-by-the-export=[]`.

**Harness.** Extracted `claims_reg_line` (the head's own function, sourced verbatim from `tools/pr/prepr.sh:325-354`) driven over (a) a whole-tree copy, `git archive HEAD | tar -x`, and (b) the copy the step builds, `git archive HEAD -- $CLAIMS_INPUTS "$CLAIMS_GEN" | tar -x`, at the same commit, in a clone at `/tmp/rev2853-def`.

**Metric.**

- whole-tree copy, 135,540 KB → **rc 0**, "claims.py rewrites claims.json and claims.md byte-identical, its header RESULTs hold"
- narrowed copy, 14,048 KB → **rc 1**, "committed claims.json claims.md not what … claims.py writes; header RESULT moved: claims_true=122 (header 123) claims_false=1 (header 0); re-run it and commit"
- C108 in the narrowed run: `false | 85 links, broken=[('docs/architecture.md', '../tools/audit/seat/INSTRUMENTS.md')], of which removed-by-the-export=[]`

**Perturbation.** (1) The same commit under the whole-tree copy passes, so the narrowing — not the fixture's register — is the cause. (2) Positive control for detection: a README link added *without* re-recording the register (the #2609 shape) is still refused, so the stale arm is intact. (3) Copy-shortness arm: `git archive HEAD -- README.md NOTICE_MOVED | tar -x` under the script's `set -uo pipefail` → rc 128, 0 files extracted, so a *renamed* entry refuses rather than grading short (the body's claim holds; tried to break it, could not).

**Why this blocks, not comments.**

1. The printed remedy cannot clear it. "Re-run it and commit" at the repo root writes exactly the register already committed — the whole-tree arm, rc 0, proves it — so the copy's output still differs and the next push refuses again. A seat following the message loops; the only escapes are to delete a correct link (wrong) or to edit `CLAIMS_INPUTS` (a further PR the message never implies).
2. The trigger is the check's own population: any diff touching `README.md` or `docs/*.md`. Adding in-repo links to those documents is routine.
3. `## Null control` cannot see it: it runs both copies on *this* head, whose nine out-of-docs links all land inside the list. It is a spot check on one tree, not a bound on the class.
4. `survivors=0` does not cover the arm: prepr-11 renames a **listed** entry, pinning "a listed path missing refuses", not "an unlisted read is missing from the copy". No mutant plants a link to an unlisted path.

**Shape of the fix (not designing it).** Make the copy faithful by derivation: e.g. archive the whole tree minus the measured 81.7 MB of `dev/audit` round evidence, keeping the generator's own directory — that preserves every link target at roughly the narrowed cost; or teach the generator to distinguish "absent from the export" from "broken in the repository", which the current `_export_cut` cannot. Either way, add one fixture/mutant that plants a link to an unlisted path: today no arm exercises it.

## Accepted, with the measurements that decided it

**A1 — the wall→CPU measure switch is not the block.** My both-ends run, same host, same session, `/usr/bin/time -p`:

- reviewed head `fa18c13d2`, whole-tree copy: total CPU 6.63–6.89 s, wall 13.16–16.06 s at load 39.28–40.35
- this head, narrowed copy: total CPU 3.63–3.81 s, wall 4.04–5.40 s at load 27.92–30.59

`prepr.sh` contains no comparison against 5 s; the budget is the group carry's and the body's. The body states wall with the load it was taken at and CPU, and the 8 s/15 s restatement is withdrawn. The change is cheaper in CPU at either load and, in these runs, in wall — the switch does not hide a regression.

**A2 — the raised wrapper bound cannot turn a survivor into a kill.** `run_step` passes `timeout=900` (`r10_seat_selftests_mutants.py:452`) and the verdict is `NOT RUN if rc == -1 else KILLED if rc else SURVIVED`. Forcing the bound to 0.01 s raises `TimeoutExpired` uncaught, exits non-zero with **zero** KILLED lines and no verdict: a timeout aborts, it cannot read as killed; raising 900→5400 only increases how many runs are evaluable. Stated limit: I did not reproduce the full 12-mutant run end to end — at load 110 the unmutated baseline self-test was still running after 35 minutes and I stopped it rather than hold the box. I re-derived the two new mutants directly: prepr-11's own row (extracted verbatim from the head's self-test) passes with the genuine list and fails with `NOTICE_MOVED` (`got ' NOTICE_MOVED'`); prepr-12's ARMS without `mutation` makes `--only mutation` an argparse error, rc 2, which fails the behavioural `--fill-red` row (`grep -c mutation` = 0, expected 1). 12/12 is accepted on that plus the rc-based kill rule, not on an independent full run.

**A3 — `--fill-red` is cheaper in the quantity paid and still detects.** Full predictor: wall 17.80 s / CPU 5.96 s; `--only mutation`: wall 8.40 s / CPU 3.18 s, with the same five mutation-site lines. Before/after on a real body over the five-site fixture: 2 lint errors → 1 (the mutation red written); on this head (no sites) the body is byte-identical, so the null control holds. The one-arm switch reduces work, not coverage: the arm it runs is the only one whose output it writes.

**A4 — the rest of the body checks out.**

- CI at this head: 47 contexts, **31 pass, 16 skipping, 0 fail** — including `gate`, `arch-score`, `tests / fast (3.14)`, `tests / mutation`, `pr-contract`, `governance / instrument-self-tests` (18m46s), `governance / delivery-status`.
- `harness_headers.py`'s import fix is pinned by a self-test row that blocks `voluptuous`/`homeassistant`, and that job passes at this head.
- `prepr.sh --body-check` on the real body passes: 17 figures resolved, 2 unverified, 0 refused; `## Red checks` answers both reds it names (`governance / delivery-status`, `governance / instrument-self-tests`).
- `VERSION`, the manifest version, `RELEASE_NOTES.md`'s heading, both claim files and every `*_budgets.json` are untouched at this head; no Claude/Co-Authored-By trailers; claims checked three-dot.
- `entities.py`'s `hb:` family (4 of 2,463 at this head against main's 6) is pre-existing and not head-caused; CI `tests / fast` and `gate` pass. My local re-run was still queued behind load 110 at publication; CI is the authority.
- `structure.py` / archscore: CI `gate` and `arch-score` pass at this head; local re-run queued behind load 110 (not load-bearing for the verdict).

## Tried to break, could not

- archive under an unmatched pathspec → rc 128, 0 files (no short grading).
- stale-register detection → still refuses a register that was not re-recorded.
- `--fill-red` null control → no sites, nothing written, body byte-identical.
- the CPU measure as cover for a wall regression → the old code is higher CPU at the same head, so the measure moves with the truth.
- 6g's byte-identity at this head → reproduced independently (14,048 KB copy, same `claims.json`/`claims.md` bytes as the committed register).

## Owed by this verdict

A blocked verdict re-owes the delivery row (`delivery-status-tracking.md`): `dev/programme/delivery/2853.md` must state this block and the under-coverage it names before the next handoff. This is the fourth round; if the next fixer finds the same class again, `fixer.md`'s round rule owes a re-cut, not a repair.
