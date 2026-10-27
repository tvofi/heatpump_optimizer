Fix review: blocked d606ade6db7775606e3f31f8df45032a183c5e1a claim: s6-batch38.md:76-77 still says needs_lease "answers `lease` only for `MACHINE_MEASURING`, an empty scope, or an unreadable table" but tests/gate_lock.py:940-942 returns lease for an unreadable scope (needs-lease /nonexistent -> lease); :81-82 says only gate_lock.py's own self-tests pass wait=False, but tests/entities.py's executed _gl_* tests do too; and the cited grep B | grep -v gate_lock.py prints nothing
bus-nonce: e3ec61dd78564740a84bd930b21cf6fb

Measured head: d606ade6db7775606e3f31f8df45032a183c5e1a (git ls-remote refs/heads/fix/triage-s6-batch38 and refs/pull/2881/head both answered it; re-read before writing this file).
Merge base: 34cd75bf1fe506334611ba6c074c223317370e67 = origin/main at review time.
Diff: 2 files, +115 (dev/programme/triage/s6-batch38.md +114, dev/programme/delivery/2881.md +1).
See EVIDENCE.md for every command and result.

The repaired sentence holds (s6-batch38.md:42-46)
- "the `gate_lock.take`/`_gate_lock.take` matches in `tests/gate_lock.py` and
  `tests/entities.py` are self-tests against a temp `lock_dir=d`; the CLI is not one of
  those matches" -- TRUE. The matches are gate_lock.py:1855,1923 (holder-script strings
  against temp d3/d6) and entities.py:15395-16073 (_gl_* tests under TemporaryDirectory
  d/d1/d2/lock, executed at import). `_cmd_take` at 1008 calls `take(args.label,
  lock_dir=args.lock_dir, ...)` at 1009, and `--lock-dir` defaults to DEFAULT_LOCK_DIR
  (/tmp/hpo-gate.lock) at 1139-1145 -- the by-hand route. The earlier contradiction is gone.

Findings (claim / evidence / harness / metric / perturbation)
F1 (blocking, same class). s6-batch38.md:76-77, "needs_lease answers `lease` only for
  `MACHINE_MEASURING`, an empty scope, or an unreadable table (lines 918-954)".
  Evidence: tests/gate_lock.py:918-954 has FOUR lease-returning arms; 940-942
  (`except OSError: return "lease"`, an unreadable scope file) is missing from the list.
  Harness: `python3 tests/gate_lock.py needs-lease /nonexistent/scope.scope`.
  Metric: 1 of 4 arms unlisted, inside the cited range. Perturbation: an unreadable scope
  answers `lease`, which the enumeration does not contain -- the file contradicts its own
  citation. (The empty-scope and unreadable-table arms it does list are real.)
F2 (blocking, same class). s6-batch38.md:81-82, "only `gate_lock.py`'s own self-tests pass
  it [wait=False]". Evidence: `wait=False` take/take_slot arguments also occur throughout
  tests/entities.py:15395-16073, and those _gl_* self-tests execute at import (15500, 15892,
  16085). The batch's own repaired sentence names tests/entities.py as holding gate_lock
  self-tests. Harness/metric: `grep -rn wait=False` -> 2 files pass it as a take argument,
  not 1. Perturbation: the entities.py block runs `_gate_lock.take(..., wait=False)`.
  What holds: no production caller passes wait=False.
F3 (blocking, support). s6-batch38.md:49-50, grep B "piped to `grep -v gate_lock.py`, which
  adds `mutation_table.py`, `prepr.sh`, `run.sh` and `derive_closures.sh`, plus
  `prepare_baseline.sh`". Harness: run the exact pipeline -- it prints 0 lines (exit 1),
  because every line grep B matches contains the literal gate_lock.py, so `grep -v
  gate_lock.py` removes them all. Metric: 0 vs 5 claimed; the un-piped grep does produce
  prepr.sh:3142, prepare_baseline.sh:322, mutation_table.py:1987, derive_closures.sh:128,
  run.sh:343/347/350 (and two docstring mentions it omits). Perturbation: drop the pipe and
  the claim reproduces; as written it cannot. The fix is an anchored filter
  (`grep -v '^tests/gate_lock.py:'`) or no pipe.
F4 (finding, body, same class). PR body `## Figures`: "`needs_lease` (lines 918-954) answers
  `lease` only for `MACHINE_MEASURING`." False as an answer-set claim: `needs_lease('')`,
  `needs_lease('/nonexistent')` and an unreadable closures table all answer `lease`. True
  only if silently read as script classification, which the sentence does not say;
  preflight.sh:109-111 states the rule ("Unqualified quantifiers ... enumerate the SET").

Everything else holds
- closures 936.3 s / 241.1 s (recorded table); 2 x 936.3 = 1872.6 s = 31.21 min.
- LEASE_SECONDS=1800:78; RENEW_REFUSED_RC=75:120 (dispatched at 1973-1975); renew():568;
  SLOT_MIN_SECONDS=69:116; MACHINE_MEASURING:117; take() 511-566 unbounded; the only
  timeout/deadline/max_wait hits (895, 1867, 1934) are subprocess waits.
- run.sh 317 comment, leased() 329-353, needs-lease 335, slot-auto-lease 343, flock-wrap
  347, auto-lease 350; no other lease mechanics in the file.
- mutation_table.py 1986-1998 and LEASED:2342; judge_batch.py take:185, Lease entered:378,
  renew per command (196-198, called at 268); prepr.sh slot-take:3142, needs-lease asked:344;
  derive_closures.sh:128; gate-scoping.md:28-33; audit-verify.js:192.
- 208 roster groups; R10-PREPR-CAP owns prepr.sh + gate_lock.py, stage done, carry [];
  tests/run.sh in no group's files; `grep -rn judge_batch .github/` empty.
- stress.py / harness_headers.py take no lease themselves (no gate_lock reference).
- Mutation proof + null control reproduced with roster_edit.triage_refusal (ACCEPT / None /
  P999 None / DEFER refused / missing-file refused).
- Red checks "none": 38 head check-runs = 26 success, 10 skipped, 3 in_progress, 0 failed.
- Diff scope: the batch plus the PR's own delivery row; nothing outside the seam.

Could not establish
- The 38-minute wait: /tmp/hpo-gate.lock/owner is gone; the batch declares it the
  orchestrator's measurement, not re-derived. Arithmetic is consistent with two runs.
- s6-batch37.md (cited line 3) is absent at the head and on origin/main; it exists only on
  unmerged fix/triage-s6-batch37 (a63c6bfd). The r2 fix brief records the orchestrator's
  disposition ("resolves by merge order"), so noted, not re-raised.
- "Every holder above is a measurement context": enumerated for run.sh/mutation_table/
  judge_batch; for the by-hand route true by gate-scoping.md's definition, not by an
  enumerated runtime instance.

What unblocks: name all four needs_lease arms (add the unreadable scope) at s6-batch38.md:
76-77; say "only self-tests, in gate_lock.py and tests/entities.py" at :81-82; anchor or drop
the filter at :49-50; and bring the body's Figures line to the same enumeration.
