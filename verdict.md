Fix review: merge ef157f1551c0ec3981ad4286fd81f00ab00d3796

bus-nonce: 3b3470d78647dd41df53ae3f9e867cf6
pending-ci: gate

Round 2 of #3821. Cloud reviewer seat, Linux, Chromium at /opt/pw-browsers, Node with `--max-old-space-size=6144`. Round 1 blocked b1ee994a6e as `mutation-vacuous` with three survivors. This round reviews the delta (fix-review.md step 12). `git diff 1bd0f355b9 ef157f1551` touches 3 files. In the card file the delta is two doc comments re-split, with no code change. The rest is `tests/card.mjs` (+29/-9) and `tests/card_browser.mjs` (+115). `review_carry.py 1bd0f355b9 ef157f1551` prints `FRESH-REVIEW`, as expected after a blocked round.

## Findings

none

## Evidence

- Head `ef157f1551c0ec3981ad4286fd81f00ab00d3796`; `git ls-remote` reads the branch tip there at the final re-read. Merge base 86859b9594. origin/main is a8efe1d1c2. `git merge-tree --write-tree origin/main ef157f1551` exits 0 with `LEDGER-MERGE: resolved tests/closures.json`, so there is no conflict. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Round 1's three survivors are now killed. Each was re-applied to a `git archive` copy of the head by ev/mutant_driver.sh (`tests/plan_view.py`, then `node tests/card.mjs`) and ev/mutant_driver_browser.sh (`node tests/card_browser.mjs`):
  - unmutated: `card.mjs` reads ALL CARD CHECKS PASSED, 1467 ok lines, rc 0. `card_browser.mjs` reads ALL BROWSER CHECKS PASSED, rc 0, with `tile and stat rows: 108 measured, 6 with unevenly wrapped labels, 0 misaligned`.
  - nochunkprune: deleting `if (chunk < cut) this.chunks.delete(chunk);` (card file line 7344) gives 1 CARD CHECK(S) FAILED, rc 1: "history: a card panned daily for 30 days holds no more than the 48 h span's chunks, and its rows plateau".
  - notypescale: deleting the `dlg.style.setProperty("--hpo-type-scale", ...)` write (line 11424) gives 1 FAILED, rc 1: "the dialog scales its chrome's type tokens with its font: 1 at the 14 px base, font / base at the cap".
  - typescaleconst (my null control on that check): writing a constant `"1.0000"` also gives 1 FAILED with the same check, so a constant write cannot pass it.
  - nosubgrid: replacing `display: grid; grid-template-rows: subgrid;` (line 5257) with `display: block;` makes `card_browser.mjs` fail, 1 BROWSER CHECK(S) FAILED, rc 1. It reads `6 misaligned`, each `.hl-stats row [Voraussichtliche Einspar / Optimierungswert] values 14.0 px apart` at 375 px in de-DE. The guard `uneven > 0` reads 6 at head and under the mutant, so the check is not vacuous.
  These match the body's survivor table and `## Null control`.
- Round 1's other mutation targets (hitmax, foldmax, prunecut, trkey, critfill, keeplast, emptyloc, fitold, hitedge, noprune, noph) were killed at b1ee994a6e. The delta changes no card code line, so those results stand. They were not re-run.
- Claims: `node tests/card_drift.mjs 86859b95946e` reads `card_drift: 44 state(s) moved and claimed, 1 identical`. `tests/golden/card_claimed_drift.txt` reads `claims-for: 10.1.1`, the same as `VERSION`. `tests/golden/claimed_drift.txt` is untouched, and `python3 tests/env_drift.py --claims-only` exits 0.
- The three-dot diff does not touch `VERSION`, `manifest.json` or `RELEASE_NOTES.md` (ev/version_untouched.txt is empty).
- CI at this head: `merge_train.py classify ef157f1551 --pr 3821` was polled from 17:19 to 17:51Z and read `WAIT ... pending: gate red: none` every time (ev/classify_poll.log), so this verdict carries `pending-ci: gate`. In a later read of the live check runs (between 17:39Z and 17:45Z) showed `tests / closures` still in_progress and every other owed-reds context (ev/owed_reds.txt) concluded success or skipped. `governance / instrument-self-tests` concluded success, which clears the packet's `introduced-red: unreadable` refusal. `gate` read failure at 17:09:09Z, before its units had concluded, and classify reads it as pending. Prior rounds' owed reds are answered under the body's `## Red checks`. The new `tests / fast (3.14)` comment-ratchet prediction is answered by 3ece86974e, and `fast` reads success at this head.
- Finder harness figures were re-derived in round 1 at b1ee994a6e (D4-s1-01, D4-s3-01/02/04, D9-s2-01, D6-s4-01). The delta moves no production code, so they carry; they were not re-run this round. Not re-derived in either round: D4-s3-03's base 78, D4-s3-05's base 14/41 and D4-s1-03's base 72.
- Forward-carry: the body has `none`. Its one residual, 132 pipes cut by targets drawn above the twin, carries a valid `dismissed:` (packet carry_audit: 1 routed, 0 unrouted).
- The round-2 seat comms ran under topic rev-3821.
