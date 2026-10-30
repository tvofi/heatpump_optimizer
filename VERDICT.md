Fix review: merge 18c9d3193e4aafd3a7997e125fc6e164ef8343d6

bus-nonce: c311e0525066111da0f81f389b9676ca

## Round

First review of #2973.

## Findings

- `render_readme` is mischaracterised. `tests/entities.py` (the HACS-render comment near line 1287) and item 4 of the PR body say it "is not a key HACS knows". `_HACS_KEYS` leaves it out, so the new check refuses it: mutant M7 (adding `"render_readme": true` to `hacs.json`) fails "hacs.json names the release asset release.yml uploads, with zip_release". But the head's own `validate / validate-hacs` run (job 123936146126) dumps HACS's repository manifest with a `"render_readme": false` field, and main's `hacs.json` carried the key with validate-hacs green. Dropping the key is harmless, because HACS renders README.md anyway. The false part is the stated reason and the key set built on it. Correct the comment and the PR body to say it is a legacy key with no effect, and either add `render_readme` to `_HACS_KEYS` or keep it refused with that reason. Carry: R10-MARKETPLACE
- Releases before v7.1.0 carry no asset. validate-hacs shows `v7.0.5 "assets": []`. With `zip_release: true`, a Marketplace or HACS install or a downgrade to any of those versions finds no `heatpump_optimizer.zip`. The body does not mention this rollback limit. It needs a line in the README or the v7.1.0 notes, or a decision that it is acceptable. It sits with the owner's follow-ups the body already lists (the hacs/default catalog PR after the first release carrying the asset, and the 2026.11 beta install test). Carry: R10-MARKETPLACE
- No finder's harness exists. The packet prints "Finder's harness: none named". This is an owner-requested feature (option (a), 2026-10-29), not an audit finding. The instrument is the PR's own four checks in `tests/entities.py`. My mutants M1-M7 are my own instrument and are disclosed here as mine. Carry: dismissed: owner-requested feature, in-tree checks are its harness

## Evidence

- Head checked: the PR's head is 18c9d3193e4aafd3a7997e125fc6e164ef8343d6, the SHA in this verdict's first line. This is the head measured in a detached worktree. The body names it under `## Head`, with authored code head e5cdf43 and the main merge 5a28848.
- The role files are current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Rule 4 holds. `VERSION` and `RELEASE_NOTES.md` have no three-dot diff. The only `manifest.json` change is the added `categories` block, and `version` is untouched (ev/rule4.txt).
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0 with tree 881aa0a85e3b016580eb110d9a93a57b80d0d8ad. Neither claim file conflicts or is touched (ev/mergetree.txt).
- RESULT: the mutation proof holds. Seven mutants, each refused by exactly one new check (ev/mutant-*.txt):
  - M1 is the body's own mutant, a wrong `filename`. It is refused.
  - M2, `zip_release` false: refused.
  - M3, the build archives the whole repository instead of the subtree: refused by the ZIP-layout check.
  - M4, `--draft` dropped from the create step: refused.
  - M5, the asset read-back before publish deleted: refused.
  - M6, the check step's filename comparison disabled: refused by the ZIP-step check's null control.
  - M7, `render_readme` added back: refused. See the first finding.
- RESULT: the figures re-derive exactly at the authored code head e5cdf43:
  - tar: 125,265,920 B
  - ZIP: 1,404,633 B
  - unpacked: 4,317,032 B
  - At merge base e5ddba1fa: tracked bytes 119,233,983 B, of which `dev/` is 88,090,351 B; tar 125,255,680 B.
  - At the PR head 18c9d319, after the main merge, they are tar 125,317,120 B, ZIP 1,405,314 B and unpacked 4,317,629 B in 105 files, with `__init__.py` and `manifest.json` at the root.
  - The conclusion holds at both heads: the tag archive is over 104,857,600 B and the asset is far under it (ev/figures.txt).
- RESULT: scope reproduces. `closure.py select --diff <merge-base>` printed `MODE: SCOPED -- 10 script(s) run, 23 scoped out`, matching the body's 10 after the D6 commit (ev/scope-select.txt).
- Local `tests/entities.py` at the head did not finish inside the 230 s cap in this container. The four new checks printed `ok`. The FAIL lines in the log are indented retry lines of the `hb:positive_control` timing probe, which is container jitter. CI's `gate` is the measuring surface, and it is green.
- CI on the head, read from the check-runs API (ev/ci-head.txt):
  - The latest run 41017154303 has `gate`, `pr-contract`, `arch-score` and `budget-raise-gate` green.
  - `hassfest` reports 0 invalid integrations with `categories` present, which confirms item 2. `validate-hacs` is green with the new `hacs.json` keys.
  - The only concluded red is `tests / nightly-status`, which the body's `## Red checks` answers. It grades main's last nightly dispatch, and the diff touches neither `nightly.yml` nor `tests/nightly_status.py`. Under fix-review.md step 11 it is not this PR's. The body also states that it is not a required check on main-protect.
  - pr-contract run 123936487915 started after the last red concluded and is green.
- Workflow logic read by hand:
  - The draft-then-publish order means a release without its asset is never published.
  - On dispatch, publishing the draft creates the tag at `--target`, before the "Digest the tag's tree" step reads it.
  - The attestation subject is still the tag tree, as #960 approved.
  - The job's permissions are unchanged.
- Docs (D6): the README anchor `#home-assistant-marketplace-202611-and-later` and `#hacs-before-202611` match the new headings, and doc_claims ran in the green gate. The D6 C111 link count of 17 to 19 equals the two added external URLs (the badge link and the badge image). The statements that the Marketplace replaces HACS in core from 2026.11 and refuses downloads over 100 MiB (`MAX_DOWNLOAD_SIZE`) are external. I did not re-derive them here, so they are not verified by this review.
- D10: hassfest is green with `categories`. The "docs-installation-instructions" item stays met: the README now carries Marketplace and HACS sections.
- Stale `HACS (recommended)` and `render_readme` references remain only in frozen round artefacts (`dev/audit/rounds/round3/D6/claims.py`, `round4/D5/reader_paths.py`). No gated closure reads them, so they are evidence only.
