# BLOCKED: r11-pre-briefs-census-p2 (body_push.sh exit 4, REFUSED CARRY-LANDED)

Question: will the relay land the two carries below on the round's roster and re-run `bash tools/audit/seat/body_push.sh r11-pre-briefs-census-p2 <body>`? The code head is pushed and frozen; nothing else is open on this seat.

- Code head: `refs/heads/handoff/r11-pre-briefs-census-p2` at 93f45781beff18f67719c0586f9673634c9519ca (one file, `tools/audit/enumerate.py`), `tools/pr/prepr.sh` rc=0 at that head, `PR-BODY: 0 error(s)`.
- Body: kept by `body_push.sh` at `refs/heads/handoff-wip/r11-pre-briefs-census-p2-body`, 3f5b3c3e2efaa89322d8db9fc2b4853e3f8e7e3b.

`body_push.sh` output:

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-PRE-BRIEFS-CENSUS at 93f45781beff, 1 live, 1 dispatched carries, 0 refused
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item e72411f5: not in its brief or carries: '- `python3 -I tools/audit/product_reads.py --self-test` is red on `main`: it exits 1 at `54cb721164`'
CARRY-MISSING R11-INTAKE-R10-RESIDUE body item c9cc8bee: not in its brief or carries: '- `tools/audit/seat/plant_recall.py` `population` reads the text `--population` prints and takes a l'
CARRY-LANDED: 2 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-briefs-census-p2-body 3f5b3c3e2efaa89322d8db9fc2b4853e3f8e7e3b
```

Item e72411f5 is a red on `main`, not of this diff: `python3 -I tools/audit/product_reads.py --self-test` exits 1 at `54cb721164` (the merge of #3665) and at `origin/main` 38bf516bdd, because that instrument's `operation` read and its self-test were built on the `d16-writes --cells` format `4632a10bff` replaced; the step `self-tests-outside-seat` runs it. The body's `## Forward-carry` carries the measurement.
