Fix review: merge 0ef91ac0abaa1a097104283ffd123d0b8d29322d

bus-nonce: 58d8221d896547212e60c98b781e69a4
pending-ci: tests / coverage-ratchet, tests / fast (3.14), tests / mutation, tests / typing, validate / validate-hacs

Round 1, full review. Docs-only head: a bugclasses.json `_rca` entry, the RCA document and the delivery row.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main <head>` exits 0, no conflict (ev/merge-tree.txt).
- RESULT scope: the three-dot diff touches no VERSION, manifest or RELEASE_NOTES path.
- RESULT claims re-read at fdb526895c: `_chg_seq` at tests/features.py:62313, `saturday` shift at 62335, assertion `_chg_partial[3] == [1, 0] and _chg_partial_sat[3] == [0, 1]` at 62436; `minutes_ago` uses `datetime.now(UTC)` at tests/harness.py:606; nightly cron `37 0 * * *` at nightly.yml:42; `zone_cmd` with `Zone@` faketime form at host_zone_features.py:155; `_chg_seq` introduced by 8fa60a926d (2026-11-11), day-type assertion added by b6696bd6e6 (2026-11-11 10:01Z). All match. The nightly Kolkata step is at line 517, the document says "about 508", which is within its own hedge.
- RESULT counts: 83 `dt_util.now()` reads in tests/features.py matches the document. Current tree total over tests/*.py is 144, the document says 136 at its base; not re-derived at fdb526895c, and the body's Figures section says none.
- Not re-derived: the Saturday/Sunday/Wednesday probe runs (section 1, 3), faketime cost of 10-20 s (labelled an estimate), the 13.7 runner-hours (labelled an upper bound), the 30 open PRs. The document itself says these are unverified or estimates; the verdict does not rely on them. Mutation proof and null control are n/a for a record, and the body says so.
- RESULT carry_audit: the packet reports `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`.
- Red checks: the digest had no red; classify printed `WAIT ... pending: gate red: none`. Classify still printed WAIT after about 25 minutes of polling (ev/classify.txt), so pending-ci is set.
- Forward-carry: the body's carry to R11-INTAKE-R10-RESIDUE is a live group per the document's section 5; the countermeasure is not built here and states its demonstration owed (section 5 item 4).
- Process: the RCA names state (c), a cost test with numbers and estimates labelled, a recommended countermeasure and the refused alternatives, as defect-root-cause.md asks.
