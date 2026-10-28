Fix review: merge 59bf9622a8ad38e5b7673a2a4835892a05e8a5ef

bus-nonce: 080bd4f2cf3e4434e32e50b9e390165b

Round: review of the head after the verdict/2906 repair commit (the "fixed commit and instant" count). Reviewed head 59bf9622a8ad38e5b7673a2a4835892a05e8a5ef.

## Findings

- The note cites `tests/closure.py:1221-1225` as the `for argv in spawned:` loop; at this head and at origin/main that loop is line 1242 (1221-1225 is the audit-hook runner's `sys.argv = [script, *extra_args]`). The citation is wrong by about 20 lines in a record later seats read as established. Carry: dismissed: a triage record's line cite, content-addressed by the quoted code and the mechanism it names is correct; the seat that records #2910's outcome (below) may correct it.
- The DEFER's mechanism text (`ci_predict.py:795` prints its green line with "(a data-file read is not seen)") is stale on origin/main: #2910 (R10-RCA-CLOSURE-ARGV, merged after this head's base) ships the host rule in `tools/pr/ci_predict.py`/`prepr.sh` and the caveat now reads "(a data-file read is not seen{seen})" at line 921. The route the note defers to has therefore delivered its countermeasure; the note does not say so, and its "what would change the answer" clause is overtaken. Carry: dismissed: the note is a dated record at origin/main `edd7e0e14` and its verdict DEFER matches the outcome; recording #2910 as the route's answer belongs to R10-RCA-CLOSURE-ARGV's own RCA file, which already exists on main.

## Evidence

- Diff is two new docs files (`dev/programme/delivery/2906.md`, `dev/programme/triage/s6-batch47.md`), no production code, so there is no production line to mutate; step 1 and the mutation proof are not applicable. No finder's harness is named (packet: "none named").
- `git merge-tree --write-tree origin/main 59bf9622a8ad38e5b7673a2a4835892a05e8a5ef` exits 0 (origin/main b6f6ceca4); no conflict, no claim file touched.
- VERSION (7.0.5), manifest and RELEASE_NOTES untouched by the three-dot diff; no golden or claim file, closure, budget or INERT entry moved.
- Re-derived: `git log edd7e0e14... --since=2026-10-01T00:00:00Z --no-merges --format=%s -- tests/closures.json | wc -l` = 314; the `grep -ic 'argv\|command line'` over those subjects = 0. Commits 28b0fa0f3, d218ef378, 2b84db687, edd7e0e14 exist; 28b0fa0f3's subject and fd36e08a1/d218ef378 touches match the note. `prepr.sh:672-675` and the `PREPR_RECORD_CLOSURES` opt-in and 2b84db687's "10-25 minutes" match. The `proposal-triage.md` quote is verbatim.
- Not re-derived: V149's text in `proposals.md` (no such file in the tree at this head; it is the orchestrator's off-tree file) and the filer's 3.9 s per self-test figure.
- Role-file drift check (`git diff merge-base...origin/main -- dev/governance/roles/`) is empty.
- Forward carry: the body routes to R10-FLOW-BOARD (present in wave-r10-groups.json); carry_audit at head: 2 items routed, 0 unrouted.
- CI at 59bf9622a8ad38e5b7673a2a4835892a05e8a5ef as read from the check-runs API at review time: gate-relevant checks (arch-score, budget-raise-gate, delivery-status, policy-docs, briefs, closure-scope, mutation, hassfest, CodeQL) success; env-matrix, instrument-self-tests, prelude, browser, closures, coverage and fast (3.14) were still running or queued and none red. No red check, so step 11 owes nothing. The merge train keys on those finishing green; this verdict does not claim them.
- Head re-read before posting: still 59bf9622a8ad38e5b7673a2a4835892a05e8a5ef.
