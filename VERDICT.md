Fix review: blocked 7f4028cb65588d1dde4213e27f4e402b0bcf66fd conflict: head does not merge with origin/main 76dd8811d4 (#3904 merged); git merge-tree reports content conflicts in .github/workflows/ci.yml and tests/entities.py

bus-nonce: 6a13ae1f483c2b91b14cda6afa47f88a

## Block

- `git merge-tree --write-tree origin/main 7f4028cb65588d1dde4213e27f4e402b0bcf66fd` exits 1 with `CONFLICT (content)` in `.github/workflows/ci.yml` and `tests/entities.py` (ev/merge-tree.txt). Main is at 76dd8811d4, the merge of #3904 (ci5-drop). Neither path is a claim file, so the `claimnotes` driver does not apply (role step 13). This conflict is the author's to resolve. The dispatch expects the resolution to be the union of #3904 and this PR's `concurrency` arm, `_ci_umbrella_defects` loop and `_CI_PLANTS`. A rebase changes this PR's own diff, so a review of this head would not carry to the rebased one. The rebased head needs a full review.

## Evidence

- Review scope: full (packet: no previous verdict names this head). review_packet refused with `structure` (the head does not merge with main) and `red-unanswered` (`tests / fast (3.14)`). The block makes the red moot at this head. ev/review-packet.md
- CI: `merge_train.py classify 7f4028cb65588d1dde4213e27f4e402b0bcf66fd --pr 3905` prints `WAIT 7f4028cb65588d1dde4213e27f4e402b0bcf66fd pending: gate red: none` (exit 3) (ev/classify.txt). I did not wait for CI, because the head cannot merge whatever CI says.
- Diff read against the merge base 3ee06864da: the group and cancel-in-progress expressions in ci.yml, the per-sender loop over `_CI_EVENTS` × attempt (1, 2) × sender (hpo-author[bot], tvofi, `_SELF_ACTOR`) in `_ci_umbrella_defects`, and six new plants plus the rewritten `the main group cancelling in progress` plant. On reading, the CI-main arm's expression is unchanged. Not judged at this head.
- Not re-derived here: `tests/entities.py` exits on `ModuleNotFoundError: No module named 'paho'` under /opt/hpo/venv-ha, and on `homeassistant` under venv-ci (ev/entities-head-tail.txt). So I could not confirm that the pin fails first against the unchanged ci.yml, or that the plants are caught. `dev/audit/harnesses/ci3885_queue.py fetch` needs the GitHub Actions API, which this seat cannot reach, so its baseline and null arm are not re-derived either. Both are owed at the rebased head.
