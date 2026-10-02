Fix review: merge 13ee1432d31d2a17aa1b1a352c414bb0a629bad3

bus-nonce: 0cf2496398e2f9afce8d25d06465bae8

Round 4. PR #1864 (R9-WEB-3), head 13ee1432d31d2a17aa1b1a352c414bb0a629bad3. I re-read the live head at 2026-10-02T23:55:02Z, after CI had finished, and it had not moved. The authored delta is e83fc996: tests/closure.py +3 lines, a `docs/site/docs.css` entry on INERT_EXCEPT; tests/closures.json +1 line, docs.css in `tests/doc_claims.py`'s closure. Evidence is in ev4/; HEAD.txt names the head.

## Round-3 owed item: closed

- RESULT CI closures (`SCOPE_CASE: full`, Linux): `closure: committed closures cover every file this run touched`. There is no UNDER-SCOPED and no INERT READS line, and closures-autofix was skipped.
- The INERT_EXCEPT route is the one `docs/index.html` already takes. The arm opens docs.css on every run, so the file is a dependency, not inert. Without the exception, a docs.css edit would be classified as unread.
- RESULT `tests/closure.py select --diff <merge base>` locally: `MODE: FULL`. That is expected, because the diff now touches tests/closure.py.
- tests/closure.py is code-owned. The body's `## Approval` names it, so tvofi's approving review covers it.

## At this head

- RESULT local runs:
  - `tests/doc_claims.py`: `ALL 155 checks PASSED`
  - `tests/entities.py` (venv): `ALL 2081 ENTITY CHECKS PASSED`
- RESULT waitci: `DONE total=35`, NOTGREEN `nightly-status` only. That check is main's red, and the diff reaches nothing it reads, as rounds 1-3 established.
- Green at this head: briefs, closures, pr-contract, fast (3.14), coverage, coverage-ratchet, typing, browser and mutation. `mutation` drew no mutant, because no production line changed.
- RESULT `git merge-tree --write-tree origin/main(16551007) HEAD`: clean. stderr reads `LEDGER-MERGE: resolved tests/closures.json`, so the driver resolved it.
- Main has moved past this head's merge base. The next main merge carries this verdict under `orchestrator.md` section 11, or comes back as its resolution delta.
- Body: re-cut minimal for round 4. `## Head` names e83fc996 as the code head, inside 13ee1432. `## Red checks` names briefs, both closures causes and nightly-status, each with its answer.

## Carried from earlier rounds (unchanged by this delta)

- Build arm:
  - 9 pages built, docs/backlog.md excluded.
  - The fixer's 12 planted controls are red against a green baseline.
  - Build mutation: 9 of 10 sites killed. The survivor is the zero-pages site, which is unreachable.
- Arm mutation: 32 of 33 killed. Three of those runs end in a crash that reddens doc_claims.py; I ruled them killed. The one survivor is a control-loop test mutant, which I accepted.
- Round-3 CSS patterns: 4 targeted mutants, all killed.
- Third-party refusal: covers icon, preload, iframe, script, image and srcset on the product page and every built page, plus the linked stylesheet (`@import`, `url()` in any case, `image-set()`).
- The mermaid 12.1.0 exact pin is consistent with the lockfile; I checked it statically and did not run `npm ci`.
- Classification: `tools/site/**` in tests/layout.json and `/tools/site/ @tvofi` in CODEOWNERS.
- Forward-carry: the R9-WEB-2 brief carries npm ci, the generator run and the mermaid copy.
- VERSION, the manifest, the release notes and the goldens are untouched.

## Not blocking

- `tests/closures.json` still carries `inert_reads["tests/doc_claims.py"] = ["docs/site/docs.css"]` from round 3. With docs.css now on INERT_EXCEPT, `is_inert` is False for it, so no recording will list it again. The entry is stale.
  - It errs on the safe side: the fast path treats a change to docs.css as read, and docs.css is in the closure anyway.
  - Nothing checks for extra entries in `inert_reads`.
  - Dropping the entry is a one-line cleanup for a later re-derive; it does not need another round here.
