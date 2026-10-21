Group: R10-FLOW-DESIGN-POLICY (registration pending: roster PR-B). Spec: pack file `dev/programme/flow-study/roster/groups/R10-FLOW-DESIGN-POLICY.json`, plus `design-seats/designer.md` and `design-seats/design-review.md`, at pin 30c57744ad8aab329d0054880fc9a3154262f204 on `claude/dazzling-gauss-7l3u2b`. Authority: owner ruling 2026-10-21, `RULINGS-201-3.md` at the same pin (R16–R19), and the owner's addendum to R16 (#201 comment 6322712314), which revokes decision 0012.

**This is policy.** Every file it changes is code-owned: `dev/governance/roles/`, `dev/governance/decisions/`, `CLAUDE.md`, `dev/governance/config/policy_budgets.json` and `tools/policy/policy_lint.mjs`. It merges only on the owner's approving review at its head.

What it lands, item by item against the brief:

1. **Two role contracts**: `dev/governance/roles/designer.md` and `dev/governance/roles/design-review.md`. They are built from the drafts at pin 30c57744a. They keep the drafts' steps and scope, and carry over the pin's later sections:
   - `designer.md`: **"Stops you"** keeps only an undecided predecessor seam and a brief that changes behaviour no finding names. **"A note, not a stop"** covers a finding with no finder harness. For an owner-reported one (R10-SCORES, R10-UX-HEALTH, R10-HEAT-METER), the owner's report is quoted as the evidence and the work carries on. For a judge-verified one, the judge's re-run is the evidence. A finding that cannot be stated precisely enough for a failing test is still a stop.
   - `design-review.md`: three sections follow "You do not": **"Notes for the fixer are findings, not revise points"**, **"Decisions are routed, not revised"** (`decision: orchestrator` or `decision: owner`), and **"Three notes at most"**, after which the designer re-cuts. The drafts' "after two revise rounds" sentence is gone.
   - **The carry grammar, in both contracts.** A note for the fixer is `Carry: <group> (item <id>)` or `Carry: dismissed: <reason of two or more words> (item <id>)`, with the colon, in `carry_audit.py`'s grammar. In `designer.md` it is step 7; in `design-review.md` it is the "Notes for the fixer" section.
   - **The PR's deliberate departures, kept from round 1.** The threshold is every L/XL group with no approved design, pre-study or prototype (R17). The 1-h revalidation box is hard. Each seat reports its token count where the harness gives one. Verdicts go to `design-verdict/<group>`. The evidence plan and sibling-site census cite `fixer.md` steps 2–4 and 8 rather than restate them. The drafts' "modelled on" lists and their "after the moratorium" landing notes are cut.
2. **`orchestrator.md` section 5**: unchanged from round 1. Dispatch the designer when the group's last predecessor dispatches, the design reviewer at the design's head, and the fixer only after `Design review: approve <sha>`.
3. **`fixer.md` step 17** and 4. **`fix-review.md` step 15**: unchanged from round 1.
5. **`CLAUDE.md`** names both contracts in its role table (unchanged).
6. **Decision 0012 is revoked, kept as history.**
   - Its status line reads "Revoked 2026-10-21 (owner addendum 6322712314); kept as history" and points to 0014. Its last section is "Revoked (2026-10-21)".
   - Both "the rest of this record stands" sentences are gone: the 2026-09-25 one and round 1's. So is round 1's "Void since" preface to the moratorium section, which reads as first recorded again.
   - Decision 0014's title and item 1 say 0012 is revoked, and its source line cites pin 30c57744a and the addendum.
   - The `tools/policy/policy_lint.mjs` comment on 0012's `CORPUS_EXCLUDED` entry now says the record is revoked and describes the moratorium in the past tense. That is a comment-only edit; the entry itself and every check are unchanged.

Alternatives considered:
- **Delete 0012.** Rejected: the addendum keeps the file as history.
- **Cite the carry grammar from one contract in the other.** Rejected: the brief puts the grammar in both, and each seat opens only its own contract.
- **A second document beside the architect note.** Rejected in round 1: STUDY §7 extends the note.

## Head

d2ba1e1852fa2195ade00436a78558333cc695ba, measured 2026-10-21T19:32Z. It is one commit on the round-1 PR head d3e34be538b02f1186419a3e7e4220bdf269803d. `git merge origin/main` (57f0c9c77cfd5958e0a2443e158bea8326bedae2 at 2026-10-21T19:32Z) reported "Already up to date". It was never rebased.

## Mutation proof

The pinning checks are `policy_lint.mjs`'s `index` and `budgets` classes. Each mutant was applied in a detached worktree at d2ba1e18, run with `node tools/policy/policy_lint.mjs`, then restored with `git checkout .` (`git status --short` empty afterwards):

- **M1.** Delete the two `CLAUDE.md` role-table rows. Result: two `[index]` errors, "`CLAUDE.md` does not name `dev/governance/roles/design-review.md`" and the same for `designer.md`. TOTAL 2.
- **M2.** Set `corpus_tokens` to 62391, one below measured minus `_band`. Result: one `[budgets] (whole corpus)` error, "about 62892 tokens exceeds the cap of 62891". TOTAL 1. At 62392 it reads TOTAL 0. So 62892 is the measured value plus nothing (`ratchet-budgets.md` step 3).
- **M3.** Set `designer.md`'s token cap to 877. Result: one `[budgets]` error, "about 878 tokens ... exceeds its cap of 877". TOTAL 1.
- **M3b.** Set `design-review.md`'s line cap to 52. Result: one `[budgets]` error, "53 lines exceeds its cap of 52". TOTAL 1.

No production code line changed, so there is no production mutant to draw, and there are no unpinned sites.

## Null control

- M0: the same worktree, unmutated, prints `TOTAL: 0 error(s) across 43 policy file(s)`. At origin/main 57f0c9c7 it prints 41 policy files; the difference is the two new contracts.
- Archscore before: `python3 tools/audit/archscore/score.py --diff origin/main origin/main` prints `Architecture score: dS +0.0000 NULL`. That is the baseline for the after score below.

## Figures

All taken at d2ba1e18 unless a line says otherwise.

- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 43 policy file(s)`, `FIXTURE ok`.
- `node tools/policy/policy_lint.mjs --budgets`, aggregate lines at origin/main 57f0c9c7, then round 1 d3e34be5, then this head:
  - corpus: ~61142 (cap 61026), then ~62423 (cap 62423), then ~62892 (cap 62892);
  - always-loaded: ~3410, ~3498, ~3498 (cap 3349 + 500);
  - role fixer: ~6085, ~6173, ~6173 (cap 5852 + 500);
  - role record: ~7233, ~7321, ~7321 (cap 7405 + 500);
  - role policy: ~9818, ~9906, ~9906 (cap 9958 + 500).
- Per-file rows, round 1 then this head: `designer.md` 46 lines / 666 tokens, then 60 / 878; `design-review.md` 35 / 521, then 53 / 778. Each cap is recorded at exactly the measured value. The rows for `orchestrator.md`, `fixer.md`, `fix-review.md` and `CLAUDE.md` are unchanged from round 1. This round's diff does not touch those files: `git diff --stat d3e34be5 HEAD` lists only the two contracts, the two decisions, `policy_budgets.json` and `policy_lint.mjs`.
- Spec match against the pin, by section, from `git show 30c57744a:dev/programme/flow-study/design-seats/<file>`:
  - `designer.md`'s "Stops you" and "A note, not a stop" (three bullets) are present;
  - `design-review.md`'s "Notes for the fixer are findings, not revise points", "Decisions are routed, not revised" and "Three notes at most" are present;
  - `Carry: <group> (item <id>)` and `Carry: dismissed:` are in both contracts. `grep -c 'Carry: dismissed:'` prints 1 for each file.
- The pin's later text against these contracts, in bytes/4: the pin's "Stops you" through the end of `designer.md` is 220, and here it is 191. The pin's "Notes for the fixer" through the end of `design-review.md` is 295, and here it is 281. The drafts whole are 1002 and 901; the contracts are 878 and 778.
- 0012 wording check: `grep -niE 'stand|void' dev/governance/decisions/0012-*.md dev/governance/decisions/0014-*.md` prints no line. The same grep at d3e34be5 printed the "Void since" line, both "the rest of this record stands" sentences and 0014's item 1, so the grep would have shown them had they stayed. `git grep -niE '0012|moratorium'` over `dev/governance/roles`, `dev/governance/rules`, `CLAUDE.md`, `AGENTS.md`, `.claude/rules` and `tools/policy` returns only the `policy_lint.mjs` entry this PR rewords and two `brief_lint.mjs`/fixture hits, which are the numeric strings 990012.
- `python3 tools/audit/archscore/score.py --diff origin/main`, after: `Architecture score: dS +0.0000 NULL`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`, rc 0.
- `node tools/policy/brief_lint.mjs`: rc 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`, under the seat venv's Python 3.14.7 (`/opt/hpo/venv-ci`): `ALL 2382 ENTITY CHECKS PASSED`, rc 0. Round 1's control, the same script before its closure record at 2c0a954c, read 2 of 2382 failed.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at d2ba1e18, from a branch named `handoff/r10-flow-design-policy`: rc 0, `PRE-PR: d2ba1e18...`. Its ancestry-reds arm read the pushed handoff ref and printed "the body answers every red this branch pushed (budget-raise-gate nightly-status)". Its closures step printed `skip`, as `PREPR_SKIP_CLOSURES` asks.
- Red check runs per pushed commit: `gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` filtered on completed failures, without `pr-contract`. At both d3e34be5 and 87c3672f the result is `budget-raise-gate` and `nightly-status`.

## Raise justification

The raise is `corpus_tokens` 61026 → 62892, plus the two new per-file entries `designer.md` 60 / 878 and `design-review.md` 53 / 778. Each value is re-recorded to what `--budgets` measures at this head. No existing file's cap moves. The owner's ruling R19 approves the corpus-cap raise. It still merges only on the owner's approving review at this head (budget-raise-gate, decision 0013). This round adds 469 tokens over round 1, the measured 62892 against 62423. That is the cost of the pin's three review sections, its "A note, not a stop" section and the carry grammar.

Payments tried:
- **Shorten the pin's added sections.** Taken. The pin's added text, in bytes/4 as measured in `## Figures`, went from 220 to 191 (`designer.md`) and from 295 to 281 (`design-review.md`). The second "Live:" sentence (8 then 4 revise points at about 20 min a round) was cut, and the rest reworded. R10-SCORES' 8 → 4 → approve was kept, because it is the measurement the rule rests on.
- **Cite the carry grammar from one contract in the other, or from `finding-propagation.md`.** Not taken. The brief puts the grammar in both contracts, and `finding-propagation.md`'s form omits `(item <id>)`, which rule 19 requires.
- **Drop the pin's owner-reported bullet list down to one line.** Not taken. Each bullet is a separate disposition (carry on, carry on with the judge's re-run, stop), and merging them loses the stop case.
- **Round 1's payments stand.** These were the `fixer.md`/`COMMON.md` shortening, and the spent prose deleted in `orchestrator.md`, `fixer.md` and `fix-review.md`. This round's diff touches none of those files.
- **Move prose into an uncapped file.** Not a payment: `corpus_tokens` does not move when prose moves (`ratchet-budgets.md`).
- **Leave the cap and stay inside the band.** Not possible. The base cap plus `_band` is 61526, against a measured 62892.

Architecture score: dS +0.0000 NULL

## Red checks

- `budget-raise-gate`: red by design until the owner's approving review at this head. It reads three raises in `policy_budgets.json`: `corpus_tokens` and the two new per-file entries. No cheaper detector is owed: the gate is already the earliest detector for an unapproved raise and runs at push time, and approval is the owner's to give, not something a push can supply (R19, decision 0013). Carry: dismissed: owner approval pending
- `nightly-status`: red on this branch's commits d3e34be5 and 87c3672f. It reports `main`'s current `record` conclusion, which is in `governance.yml`'s `nightly-status` job, onto every pull request. So it grades `main`, not this diff. This diff touches no `.github/` workflow, no test lane and no delivery row (`fix-review.md` step 11: not this pull request's unless its diff reaches what it reads). No cheaper detector is owed by this PR. Carry: dismissed: grades main, not this diff

## Forward-carry

- The verdict grammar R10-FLOW-DESIGN-STAGES must parse and mechanise is fixed by `design-review.md` step 7: `Design review: approve <sha>` or `Design review: revise <sha> <class>`, at `design-verdict/<group>`, with the design at `design/<group>`. The `decision: orchestrator|owner` markers and the three-note cap are new parse targets from this round. Its pack carry already says its templates cite these contracts, and it merges after this group. Carry: dismissed: pack carry already binds it

## Friction

- fixer.md: cost: the session's default `python3` is 3.11 without the pinned dependencies. `tests/entities.py` needs the seat venv `cloud-setup.sh` builds (`/opt/hpo/venv-ci`) first on PATH. Carry: dismissed: environment setup, not policy

## Carry index

`carry_audit.py` hashes an item's whole text, marker included, so no item can quote its own id. Each item above ends in its own marker. These lines repeat each marker with the id the audit assigns to that item at this body.

- Carry: dismissed: owner approval pending (item 515c0519)
- Carry: dismissed: grades main, not this diff (item 350c023f)
- Carry: dismissed: pack carry already binds it (item e82d539c)
- Carry: dismissed: environment setup, not policy (item 973624f8)

## Approval

Awaiting the owner's approving review at the head. The change is authorised by the owner's ruling 2026-10-21 (R16–R19, `RULINGS-201-3.md` at pin 30c57744a) and the addendum revoking 0012 (#201 comment 6322712314). That ruling is not the approval: every changed policy and budget path is code-owned, so `main-protect-checks` and `budget-raise-gate` merge it only on the owner's own review at this head.

## Attribution

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_014iZFvrox3TRXCy5qFMSSAF
