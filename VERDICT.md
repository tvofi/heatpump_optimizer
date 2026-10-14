Fix review: merge 35c5f68d9d38fa57190e2a38b2683176a7d62162

bus-nonce: 57821321440586d30663442b7ffe7525

Round 2 of PR #2210. I measured head 35c5f68d9d38fa57190e2a38b2683176a7d62162 from a detached worktree. Its merge base is origin/main 17f1c55f, and `git diff <mb>...origin/main -- dev/governance/roles/` is empty. Round 1 was blocked at bef6242f9 because M11 (the numeric-state filter) was unpinned.

1. **The delta is exactly two commits.** `git log bef6242f9..head` lists 67fe365b4 (tests/replay.py) and 35c5f68d9 (dev/programme/delivery/2210.md, one line). `git diff --stat bef6242f9 head` shows only those two files, so tools/replay/export.py is byte-identical to the round-1 head. The round-1 findings on the citation, the older core versions, the wrong-pick probes and the untouched sanitiser therefore carry unchanged.
2. **M11 is now killed.** My mutate.py at the head gives `RESULT M11_numeric rc=1 KILLED red=['tibber_price:unavailable_skipped']`. M1–M9 and M12 are still killed, and M6 is now killed by two checks. M10 survives, as before. The file was restored clean after each mutant (evidence/mutants.txt). All 10 checks are ok at the head (evidence/head_checks.txt).
3. **The new check does not measure itself.** `unavailable_skipped` runs the production `export.build_export` against a recorder sqlite that synthesize.write_install writes. Home B has an hourly row in the window, but every row is the state `unavailable`. The check expects home A's entity id with a non-zero row count, which is the scenario of my round-1 probe P2. It does not re-implement `_numeric`. Under M11 it goes red, refusing with "2 usable of 2".
4. **M10's triage holds.** The mutant changes behaviour only when the registry's `unique_id` is falsy, meaning None, an empty string or 0. HA's RegistryEntry stores `unique_id` as a str, and the entity platform registers an entity in the registry only when it has a unique id. The `or "_"` fallback makes such a row fail closed. It is reasonable to count it as an equivalent mutant, with the triage written in the body.
5. **The address residual is stated in the body**, as I observed in round 1. The exposure existed before this change through `--price-entity`.

**Checks.** `git merge-tree --write-tree origin/main head` exits 0. The head's check-runs show 15 success, 12 skipped, 1 neutral and 8 still in progress. The one failure is `nightly-status`, which by defect-root-cause.md is not this PR's to answer: the diff does not reach what it reads. The merge train's CI gate covers the runs still in progress.

**Commands (rc).**

- `run_checks.py <wt>` → 0 (10 ok)
- `mutate.py <wt> run_checks.py` → 0 (M10 survived, the rest killed; restored clean)
- `gh pr view 2210` (read) → 0; the body's head is 35c5f68d9
- the check-runs API (read) → 0
- merge-tree → 0
