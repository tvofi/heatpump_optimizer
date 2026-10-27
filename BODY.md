Correction to triage batch 40, entry P211 (V124), which merged as #2886 at `ee5816b1`. The verdict line does not change — **ACCEPT narrowed** — but the ruling's second-arm analysis was wrong and this replaces it.

The first cut rejected V124's second arm whole: "raise the threshold, and stop the lease being shorter than the gate it protects". The threshold raise alone stays REJECTED, for the reason already in the entry — a prepr takes a pool slot held for the life of its run, not the exclusive lease (`tests/gate_lock.py:53-56`), every measured instance is a healthy run, so a bigger number treats the symptom. The lease half is different, and my first cut missed why: an expired lease does not merely fail to protect, it **refuses the command**. `renew()` raises `no live gate lease to renew` when the recorded owner is absent or expired (`tests/gate_lock.py:577`), and `_cmd_flock_wrap` (`:1123`) turns that `RuntimeError` into rc 1 without running the command; `flock_wrap` (`:861-877`) recovers only from `RenewRefused`. So a lease that lapses between two measuring commands inside one prepr refuses the second, and #2854's own body records exactly that: `tests/stress.py` and `tests/harness_headers.py` "were refused by `tests/gate_lock.py` when the 30-minute lease lapsed inside the 85-minute run".

That half is now a second carry to `R10-PREPR-CAP`, the group that owns `tests/gate_lock.py`. The repair does not lengthen `LEASE_SECONDS` and does not loosen `renew()`'s refusals: in the `flock-wrap` path, an expired own-label lease is refreshed when no ticket waits, and otherwise the path re-takes at the back exactly as `RenewRefused` already does. A command never runs without a live lease; a run that never loses its lease takes exactly today's code, which is the null control; the two self-test arms are an expired own-label lease with no waiter (refreshes and runs) and one with a waiting ticket (re-queues rather than running beside it).

**How the first cut went wrong, recorded because it is the seat's own class.** I reported that #2854's body lacked the 85-minute figure. It has it. My grep matched the containing line and the cut I read printed only its first 220 characters; I read absence off the truncated prefix and rejected a real finding on it. The orchestrator's provenance edit on #2886 caught the false claim; the mechanism is the seat habit of printing the whole answer rather than a prefix.

The diff is one markdown file under `dev/programme/triage/`. No product behaviour changes.

**Roster state, so the ops are right.** Both destinations are already `fixing` at `origin/handoff/audit-r10-roster` `8f7e252fe` (both were `done` at `32b938f3e`), so the `set-stage` halves of this batch's queue lines have landed and only the two `append-carry` ops remain: `R10-UPDATE-PR-SIGNALS` with `b40-P211.txt` and `R10-PREPR-CAP` with `b40-P211-lease.txt`. Both texts pass the gate against this file. The orchestrator un-marks them; this seat does not re-queue them.

## Head

`2a92dd656f7e01d4f358ee58df0d69735a201bd7`; the file is the whole diff against `a0e7664ea`.

## Mutation proof

The gate this file feeds is `tools/audit/seat/roster_edit.py`'s `triage_refusal` (`ruling_verdict` at 456, `triage_refusal` at 464): a roster text naming a proposal must cite `triage: dev/programme/triage/<file>.md#P<n>`, and the cited entry must read `Verdict: ACCEPT`. On the committed file, with the seat library on `sys.path`:

```
committed verdict ACCEPT
committed carry1 None
committed carry2 None
mutant DEFER verdict DEFER
mutant DEFER carry2 dev/programme/triage/s6-batch40.md#P211 is not an ACCEPT ruling (DEFER)
mutant heading verdict None
mutant heading carry2 dev/programme/triage/s6-batch40.md#P211 is not an ACCEPT ruling (no such entry)
```

Two mutants, both on the committed text in memory: the verdict flipped to `DEFER`, and the heading changed to `## P211 (relay P1):`. Both are refused, so the second carry is genuinely read against this file's verdict and this file's entry anchor, not merely against the file's presence.

## Null control

`missing file` — `the triage ruling dev/programme/triage/s6-batch40.md is not on the roster branch or origin/main`; `uncited proposal text` — `proposal-sourced text cites no triage ruling (...): 'proposal P2 adds a check'`. Both from the same run. The mutation proof's `committed carry1 None` is the positive control on the unchanged carry text.

## Figures

- `tests/gate_lock.py:577` — `renew()` raising `RuntimeError("no live gate lease to renew")` when `owner is None or owner.expired`.
- `tests/gate_lock.py:1123` — `_cmd_flock_wrap` printing `gate_lock: flock-wrap refused, {label} holds no lease: {exc}` and returning 1.
- `tests/gate_lock.py:861-877` — `flock_wrap` catching `RenewRefused` only, releasing and re-taking at the back.
- `tests/gate_lock.py:53-56` — "A pool slot is held for the LIFE of its run, not for its lease ... under load a prepr routinely runs past `LEASE_SECONDS`".
- #2854's own body, `updatedAt` 2026-10-27T18:23:17Z — "were refused by `tests/gate_lock.py` when the 30-minute lease lapsed inside the 85-minute run (`gate_lock: flock-wrap refused, fix-2854-conflict holds no lease: no live gate lease to renew`)".
- roster stages — `python3 -c "import json; gs=json.load(open('dev/programme/rosters/wave-r10-groups.json'))['groups']; print([(g['group'], g['resume']['stage']) for g in gs if g['group'] in ('R10-UPDATE-PR-SIGNALS','R10-PREPR-CAP')])"` at `8f7e252fe` prints both `fixing`; the same over `32b938f3e` prints both `done`.

## Red checks

none

## Forward-carry

none

## Friction

none
