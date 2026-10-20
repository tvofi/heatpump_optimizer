DESIGN REVIEW: CHANGES-REQUIRED

# Independent adversarial review — the orchestration machinery

Design under review: `handoff/orch-machinery` at
`2b159e4662f87e4cbfdb96c6b00bdffa9bc49ed1`
(`dev/audit/design/orch-machinery/DESIGN.md`, `EVIDENCE.md`).
Reviewed from a detached worktree at that SHA; every command re-run by this seat
and recorded in `EVIDENCE.md` (sections V1–V17). Live state was re-read at
12:07Z–12:20Z, after the design's 11:38Z–11:56Z window, so where a live figure
moved I report both.

## What moved the verdict

Two load-bearing claims were perturbed and did not survive:

1. **Change 1, the disposal figure.** S1, §3.2 and E2 say "201 re-owed at a
   different sha". E2's command compares ref **names** and cannot see a sha. A
   sha comparison shows **199 of 202** disposed refs were last owed at exactly
   the sha they were disposed at; only **3** moved (the three live moving
   branches). The reader-never-opens-disposal defect is real and reproduced; the
   201-entry "disposal cannot stick" argument is not (B1).
2. **Change 3, the worked example.** §6.4 defines "blocked on owner disposition"
   as *no act the in-force mandate covers*, then says S3's 14 gates "become 10
   ready and 4 owner". The mandate's published text (`#201` comment 6175172275:
   scope `all`; covers codeowner, policy and budget-raise approvals) covers all
   14, and the four the design calls owner acts are all `code-owned:`/`policy:`.
   The correct output under the design's own rule is **14 ready, 0 owner**; the
   10/4 split is the gate-string test S3 criticises (B2).

Had either claim held, this review would read APPROVE with corrections. Neither
does. The structure survives — one ledger, one supervised beat, a reconciler,
fail-closed adapters are the right shape, and most of the evidence is honest and
reproducible — but the design cannot be implemented as written without decisions
it leaves open and three false seam/scope claims.

---

## Blocking findings

### B1 — the "re-owed at a different sha" figure is false (blocking)

**Design:** S1, §3.2 (`cloud-disposed` row), §5 E2.

**Command:** compare the last OWED sha per ref with the disposed sha
(`EVIDENCE.md` V2a), against E2's own `comm` on ref names.

**Result:** `owed+disposed: 202; last-owed sha == disposed sha: 199; different:
3` — `handoff/audit-r10-plan`, `handoff/audit-r10-roster`,
`handoff/r10-ci-layout-p0`. E2's `comm` returns 201 but proves only co-occurrence.
The relay's move rule fires for the three moving branches; it is not a
201-entry failure. Correct the figure and restate why the ledger is still
required: the tick never opens `cloud-disposed` (reproduced, V3), and at my read
200 of the 202 disposed refs sat at exactly their disposed sha (the other two
are the live plan/roster state refs, which move), so a reader that opened the
file would silence them — while the board prints 30,000 lines over 229 subjects. That is the verifiable argument, and it
is stronger than the one made. (The first cut of my own remote-existence check
mis-keyed the refs; the corrected figures are in V2.)

### B2 — the owner-gate worked example contradicts its own rule and the mandate (blocking)

**Design:** S3, §6.4 ("S3's 14 become 10 ready and 4 owner").

**Command:** read the mandate (`gh api …/issues/comments/6175172275`), then
classify the 14 open gates (`EVIDENCE.md` V8, V8b).

**Result:** the mandate is "scope all … covers codeowner, policy and budget-raise
approvals". All 14 gates are `mandated…`, `code-owned:` or `policy:`; under "no
act the in-force mandate covers" the answer is 14/0. The 10/4 split is produced
by asking whether the gate's free text names the mandate — S3's defect in a new
form. The reconciler's gate predicate must be defined (class × mandate coverage,
with the mandate's scope parsed), and the worked example re-derived.

### B3 — `RECORD-INVALID` over-fires on 7 of the 8 short commits (blocking)

**Design:** S2, §6.4 ("A `resume.commit` that is not 40-hex is a
`RECORD-INVALID` line").

**Command:** `git cat-file -t` and `git merge-base --is-ancestor` for each of the
8 (`EVIDENCE.md` V8c).

**Result:** 7 resolve unambiguously and are ancestors of `origin/main`; only
`c35302773738` does not resolve in this clone (it may exist on an unfetched
ref). The record is right and the length test is
wrong — the design says so in S2 and then proposes to relabel the records.
Resolve the prefix (refuse only an ambiguous or unresolvable one) and verify
ancestry.

### B4 — R10-ROSTER-OPS already owns a reconciler; the design adds a second (blocking)

**Design:** §6.4, §8 ("Seam: R10-ROSTER-OPS supplies `set-after` and the new
fields' ops; this design supplies the reconciler and the rendering"), §1's
inventory.

**Command:** read the R10-ROSTER-OPS brief at the roster tip the design's own
E14 cites, and the commit that put it there (`EVIDENCE.md` V17).

**Result:** at `541868d6f` — the tip in the design's own `beat.tip` — the brief
adds `roster_sync.py --apply`, run by `state_docs.py beat`, deriving
`resume.stage` from a MERGED or OPEN PR on `resume.branch` and writing it through
`roster_edit.py`'s lint gate. That is the design's §6.4 reconciler, one mechanism
deriving and writing and the other deriving and printing. The seam claim is
false against the revision the design measured, and the repository refuses
parallel mechanisms. Decide the single owner (consume `roster_sync`'s output, or
make the reconciler the writer) before either lands.

### B5 — the R10-CI-LAYOUT seam is real, not "none" (blocking)

**Design:** §6.7, §8 Phase 3 ("Seam: none with R10-CI-LAYOUT (workflows are
outside this surface)").

**Command:** `selftest_wiring.py`'s rule and its CI call; R10-CI-LAYOUT's `files`
list (`EVIDENCE.md` V16, V17).

**Result:** `beatd.py`, `ledger.py` and `plan_page.py` each carry `--self-test`,
so `selftest_wiring.py --check` refuses them unwired; wiring means a `run:` line
naming `tools/audit/seat/<file>` and `self-test` in `.github/workflows/*.yml`.
`tests.yml` and `governance.yml` are exactly R10-CI-LAYOUT's files, in four PRs,
one of which re-records `script_runs_per_push`. The design must name the ordering
and the file collision.

### B6 — `beatd status` does not answer S4 (blocking)

**Design:** §6.2 ("`beatd status …` — the tree-readable liveness contract S4
lacks"), S4.

**Command:** compare the jobs in §6.2's table with S4's evidence
(`EVIDENCE.md` V9, V10).

**Result:** S4 is about **seats**: the ledger's `LIVE(8)` names eight seats and
no process exists for five of them. `beatd`'s five jobs (tick, relay, state-docs,
sync, plan-page) contain no seat; its journal says nothing about a fixer or
reviewer. The slip the design cites is unaddressed. Either say S4 is out of
scope, or add the seat-liveness mechanism.

### B7 — the relay job's 600 s timeout is below the work it runs (blocking)

**Design:** §6.2 (job table: `relay` (M03/M04, 120 s, timeout 600 s); "the
relay's handoff arm … becomes its own job with its own timeout"), S7.

**Command:** live process table and slot leases (`EVIDENCE.md` V6), plus E7's
own measurement.

**Result:** three `prepr.sh` runs were live at 10:18, 19:44 and 28:28 elapsed
when read; the design's E7 measured two at 15+ minutes. M03 runs
`update_pr.sh`/`prepr.sh` **inline**, so a 600 s cap kills the handoff arm under
the load it was measured in, every pass, leaving a half-updated worktree that the
next pass retries. The job table also lists M03 and M04 as one `relay` job,
contradicting the text's "separate jobs": the probe arm is starved behind a
15-minute handoff arm. Separate the two, and set the bound above a measured
duration or move the long work out of the beat.

### B8 — the migration reintroduces the double start S5 names (blocking)

**Design:** §8 Phase 1 ("the three hand-launched daemons retired in one switch,
with the journal as the liveness contract"), §6.2 ("`beatd` writes no `alive`
file").

**Command:** read the in-tree sweep template (`EVIDENCE.md` V9/V10 context).

**Result:** `tools/audit/seat/sweep_template.md` step 5 restarts a tick **seat**
when `{{tick_alive}}` is older than `{{tick_stale_min}}`, and starts it running
`orchestrator_tick.py`. After Phase 1 nothing writes `tick_alive`, so the sweep
will start a second tick mechanism against the same board — the S5 double start,
now permanent. The migration must edit the sweep (or have `beatd` write the
liveness file the sweep reads).

### B9 — `absorbed` can silently drop after-edges (blocking)

**Design:** S8b, §6.4.

**Command:** read `roster_lib.DONE_STAGES` / `open_groups` (`EVIDENCE.md` V8
context).

**Result:** `absorbed` joins `DONE_STAGES`, so the group's `after`-edges stop
constraining. The proposed check — "the absorbing group is open or done itself"
— verifies the destination exists, not that its edges carry the absorbed group's
prerequisites. The design itself observes "which nothing checks" and then adds a
weaker check. A slip recorded as `absorbed` remains a slip lost. Require that
every one of the absorbed group's `after`-edges is present on the absorbing
group (or its transitive closure) before the disposition is accepted.

### B10 — most ledger kinds have no closer, and a vanished subject never closes (blocking)

**Design:** §6.3 (kind list; "Producers open; actors close"; supersede rule),
§8 Phase 1 (the 210-entry import).

**Command:** the log/disposal analysis (`EVIDENCE.md` V2, V2a) and the relay
source.

**Result:** the design names a closer only for `handoff-no-pr` (the PR appears)
and `orphans`. `reviewer-fire`, `record-owed`, `train-stop` and `stage-mismatch`
have none: the reconciler opens `stage-mismatch` every pass and nothing closes a
resolved one, which is S1 (a level written as a per-pass event) rebuilt in the
new file. A subject that vanishes also has no rule: **19** of the 32
never-disposed subjects are gone from `origin`, so nothing will ever close them.
Two always-owed refs (`handoff/audit-r10-plan`, `handoff/audit-r10-roster`) are
long-lived state refs the relay's `handoff-no-pr` rule treats as handoff
branches,
so even a perfect ledger carries permanent obligations unless the rule gains an
exemption. Add, per kind, the closing actor and the resolution predicate, plus a
`subject-absent` close; otherwise the "one level" promises a clean board it
cannot reach. The one-time import must also close at the *current* sha (the
disposal file carries no kind; the import must infer `handoff-no-pr` vs
`probe-ref` and state what it does with a ref it cannot classify).

### B11 — the ledger and the reconciler have no unreadable contract (blocking)

**Design:** §6.1 principle 3, §6.5 (which lists only `cloud_relay`,
`state_docs`, `bus.sh`).

**Command:** source read of the current tail (`orchestrator_tick.py:relay_owed`
has an explicit `OSError -> unreadable` branch) and the proposed replacement
(`EVIDENCE.md` V3).

**Result:** a missing or unreadable `obligations.tsv` will fold to an empty open
set and print a clean board — a pass it did not earn, the S6 class. The
reconciler is the same: an unreadable `ls-remote` or PR list prints no
mismatches. `beatd`'s job table is a third: an unreadable table must refuse to
start, not run zero jobs. Principle 3 says the adapter returns UNREADABLE and
the runner fails the pass; name the branches for the two new readers and keep
the current `FileNotFoundError` vs `OSError` split (first run is not a failure;
an unreadable file is).

### B12 — three of the five plan-page defects are already repaired at the cited file (blocking)

**Design:** §6.7 ("Self-test: the five recorded defects, each failing-then-passing"), S8, E10.

**Command:** read `~/hpo-orch/r10s3/plan/gen.py` (12293 bytes, mtime 13:54, md5
`446ce441…`, unchanged since the design's last read), plus both `.bak` files
(`EVIDENCE.md` V11).

**Result:** at the file E10 cites: defect 1 (hardcoded `R10-ARCH-DOCS` override)
is present; defect 2 (scratch `EDGES` preference) is **removed** — the file says
"used to … One source: the roster", and both backups carry it; defect 3 (wrong
issue count) is **corrected** (`--state open` minus `#201`); defect 4 (commit
prefix as PR number) is **corrected** (`"merged"` for a non-digit); defect 5 is
**partial** (status says "folded", the pill class is still `done`). The proposed
arms for 2, 3 and 4 therefore cannot fail on the pre-fix behaviour, because the
pre-fix behaviour no longer exists at the cited file. Re-derive the five against
the file that will be ported, or state them as mutation pins with a mutant that
actually flips the rendered output.

### B13 — the stage-vs-ref rule misses the suffix ref in the design's own nine (blocking)

**Design:** §6.4 ("`not-started` + a `handoff/`/`fix/` ref or an open PR at its
branch"), S2, E8's nine.

**Command:** re-implement the stated rule, then the prefix match (`EVIDENCE.md`
V8, V8a).

**Result:** `R10-CI-LAYOUT`'s branch is `handoff/r10-ci-layout`; the ref is
`handoff/r10-ci-layout-p0`. A branch-exact rule prints no mismatch; the design's
nine include CI-LAYOUT, so the evidence used a prefix match the design does not
state. Define the matching rule (topic, or `<topic>-<suffix>`) and re-derive the
list; my re-run gives 10 mismatches now, a different set, so the exact nine are
UNVERIFIED regardless.

### B14 — the policy list is incomplete and the cost summary contradicts it (blocking)

**Design:** §8 policy table, §6.8 ("policy lines 0"; "1 owner-approved schema
change").

**Command:** compare the elements that change a seat's behaviour with the table.

**Result:** §6.8 claims zero policy lines per element and one schema change;
§8 lists five proposals. Elements missing from the table: (i) `roster_edit.py
--reconcile` and the `STAGE-MISMATCH` / `GATE-READY` / `RECORD-INVALID`
vocabulary a seat must act on — a new op in a file R10-ROSTER-OPS is editing;
(ii) the plan of record moves to `handoff/round<N>/state/PLAN.html` plus the
mirror, so every brief/sweep that names the plan path changes; (iii) lock
contention behaviour ("the loser re-deriving rather than retrying blindly") for
roster, plan ref and `open_pr`; (iv) `cloud_relay.sh pass` returning non-zero
changes every caller's rc contract. Each is policy under CLAUDE.md's "changes
what a seat must do" test and needs the owner's approval before merge.

### B15 — the inventory misses a second writer to `#201` and other mechanisms (blocking)

**Design:** §2 (composition rule), §1.1.

**Command:** the tree (`EVIDENCE.md` V15) plus the named-mechanism greps.

**Result:** the record beat, `record_row.py` and its two jobs, `wt_sync`,
`daemonize`, the state mirror, `handoff_push`/`delivery_row`, `proof_watch` and
the tick's OWED arm are present (PASS). Missing: `governance.yml`'s
`delivery-status` (a PR-time check, 5-minute bound) and **`delivery-status-publish`**
(a push-to-main job with `issues: write` that edits `#201`'s delimited **body**
region) — a second writer to a named state surface, which M35's "one comment per
record act" does not describe; `tests/delivery_status.py` (the credential-free
ledger builder); `codeql-triage-poll.sh` (a tracked 36-iteration poll with a
hardcoded head sha and job id); and the tick's `MERGE-READY` arm
(`orchestrator_tick.py:645-677`, reading `review/*` verdict refs), which M02's
reads column omits. The composition rule as written ("every instrument that
produces, consumes or repairs one of the four state surfaces") would also sweep
in `tests/delivery_status.py` and `carry_audit.py`; state the trigger qualifier
and apply it.

### B16 — `relay-post` is a second store for a fact `bus.sh` owns (blocking)

**Design:** §6.3 (kind list includes `relay-post`; "bus.sh orphans feeds the
same ledger").

**Command:** `bus.sh`'s posted state (`EVIDENCE.md` V15 context) and the
`cloud_relay` confirm arm.

**Result:** `bus.sh` already records posted verdicts in `$HPO_BUS_STATE/posted`
(and `posted-signed`), and `cloud_relay.sh` writes `POSTED`/`OWED <utc> <pr> …`
for the same fact. The design moves only `orphans` into the ledger and leaves
`relay-post` beside `bus.sh`'s record, with no named closer. Under principle 2
one writer per fact: make `bus.sh confirm` the ledger's closer, or drop the
kind. Relatedly, the design never retires the relay's OWED **log** writes; if the
relay keeps appending OWED lines, the 30k-line log remains a second store.

---

## Non-blocking findings

### N1 — E1's tree figures are off by one (non-blocking)

`ls tools/audit/seat | wc -l` is **52** at the design's own read head, not 53;
and "38 with a `--self-test`" includes `INSTRUMENTS.md`, a document — 37 scripts.
The 22,793-line and 46-row figures reproduce. The composition arithmetic "the
difference from 46 is the folds and the additions" leans on the wrong 53
(`EVIDENCE.md` V1).

### N2 — E9's liveness command does not produce its output; a time is local under a `Z` label (non-blocking)

`tail -1 SEATS.md` returns the 07:10Z "Owed openers remain" line; the quoted
`LIVE(8)` line is at 162 of 893. The ledger's mtime is 09:12 **local** (07:12Z),
not 09:12Z. Also E2's kind breakdown calls the single `reviewer-fire` line a
"relay verdict"; the token is `reviewer-fire` (`EVIDENCE.md` V9, V2). The
conclusions survive.

### N3 — the `state-docs` job cannot be M06 as tabled (non-blocking)

M06 is `state_docs.py beat --watch-ref --tip-file`, an internal loop; §6.2's
`state-docs` job (300 s interval, 300 s timeout) must run the one-shot M07 form,
or the timeout kills the loop every pass. Say which invocation the job runs.

### N4 — Phase 3 keeps two plan artifacts for a week (non-blocking)

"The scratch generator is retired when the tree page has rendered a week" leaves
two plan-of-record artifacts at different paths during the overlap — a parallel
mechanism the design elsewhere refuses. Name the read path for the overlap and
the retirement condition in observable terms.

### N5 — the new-file cost omits CI wiring and the instrument inventory (non-blocking)

Three new self-testing files need a workflow `run:` line each
(`selftest_wiring.py --check`), an `INSTRUMENTS.md` entry (the inventory's
convention), and `tests/entities.py` / `tests/structure.py` to stay green.
None is in §6.8's cost.

### N6 — "210 disposed refs" is 210 lines, 203 distinct refs (non-blocking)

Seven duplicate disposal lines. Say "refs" or "lines" consistently; the ledger
import must be idempotent (`EVIDENCE.md` V2).

### N7 — the ledger's shift in what the board means needs a reader note (non-blocking)

The current board prints every historical OWED line; the ledger prints the open
set. A reader who compares today's 30,000-line board with tomorrow's ~30-line
board needs the contract change stated where the sweep reads it, not only in the
design.

---

## Per-change verification table

Statuses are over re-run commands only. PASS = reproduced; FAIL = the command
gave a different answer or the design states no testable answer; UNVERIFIED =
the state moved or the evidence does not carry the program.

| # | claim (design section) | verdict | finding |
|---|---|---|---|
| 1.1 | Board is a projection of the relay log; 30k OWED lines / 229 subjects (§S1, E2) | PASS | |
| 1.2 | `relay_owed` keys on `f[2]`; disposal survives; POSTED cancels (§S1, E3) | PASS | |
| 1.3 | "201 re-owed at a different sha" (§3.2, E2) | FAIL | B1 |
| 1.4 | Self-tests pass with the defects present (E12) | PASS | |
| 1.5 | Every ledger kind and every vanished subject has a closer (§6.3) | FAIL | B10 |
| 1.6 | The ledger fold fails closed on an unreadable input (§6.1, §6.5) | FAIL | B11 |
| 1.7 | One writer per fact: no second store beside `bus.sh`/the log (§6.3) | FAIL | B16 |
| 2.1 | Six launches of one logical tick loop (§3.3, E4) | PASS | |
| 2.2 | `alive` has no writer process; no scheduled task (E9) | PASS | |
| 2.3 | `cloud_relay.sh pass` returns rc 0 with both reads failing (E4) | PASS | |
| 2.4 | Prepr has no timeout and no progress line; `Terminated: 15` artifacts (E7) | PASS | |
| 2.5 | The two preprs' live ps rows, 15+ min (E7) | UNVERIFIED | |
| 2.6 | A live slot holder is stolen at expiry; null control (E6) | PASS | |
| 2.7 | Tick cadence 8.2 passes/h, median ~400 s, max gap 2,654 s (E5) | PASS | |
| 2.8 | The relay job's timeout is above the work it runs (§6.2) | FAIL | B7 |
| 2.9 | `beatd status` answers S4 (§6.2) | FAIL | B6 |
| 2.10 | The migration keeps the sweep's liveness read working (§8) | FAIL | B8 |
| 3.1 | Roster 93 groups / 47 open / 14 gates / 8 short commits (E8) | PASS | |
| 3.2 | The nine stage-vs-ref mismatches (E8) | UNVERIFIED | B13 |
| 3.3 | I5-DOCS refs + board line; UPDATE-PR-SIGNALS display; 36 missing branches (E8) | PASS | |
| 3.4 | The live `open_pr.sh` for r10-i5-docs, 11:33–11:50Z (E8) | UNVERIFIED | |
| 3.5 | 14 gates become 10 ready / 4 owner (§6.4) | FAIL | B2 |
| 3.6 | Non-40-hex `resume.commit` is `RECORD-INVALID` (§6.4) | FAIL | B3 |
| 3.7 | `absorbed` cannot drop after-edges (§6.4) | FAIL | B9 |
| 3.8 | The stage rule matches the refs its own evidence counts (§6.4) | FAIL | B13 |
| 3.9 | The reconciler fails closed on an unreadable read (§6.4) | FAIL | B11 |
| 4.1 | 46 rows, contiguous M01–M46 (§2, E1) | PASS | |
| 4.2 | 53 entries / 38 self-test files / 22,793 lines (§1, E1) | FAIL | N1 |
| 4.3 | The asked-for mechanisms are in the inventory (§2) | PASS | |
| 4.4 | The inventory names every writer/reader of the four surfaces (§2) | FAIL | B15 |
| 5.1 | `plan_table.py`/`roster_lib` already carry the model walk (§6.7) | PASS | |
| 5.2 | The sweep's publish path no longer exists (E10) | PASS | |
| 5.3 | 27/93 groups' edges differ from the scratch file (E10) | PASS | |
| 5.4 | The five recorded defects are real at the cited `gen.py` (§6.7, E10) | FAIL | B12 |
| 5.5 | The five arms fail on the pre-fix behaviour (§6.7) | FAIL | B12 |
| 6.1 | `roster_edit.py` has no `set-after` (§6.7) | PASS | |
| 6.2 | R10-ROSTER-OPS supplies only ops; the reconciler is this design's (§8) | FAIL | B4 |
| 6.3 | No seam with R10-CI-LAYOUT (§8) | FAIL | B5 |
| 6.4 | The design adds no op to `roster_edit.py` (§6.7) | FAIL | B4 |
| 7.1 | Each migration phase is independently runnable (§8) | PASS | |
| 7.2 | A crash mid-Phase 1 leaves one tick mechanism (§8) | FAIL | B8 |
| 7.3 | A crash mid-Phase 3 leaves one plan artifact (§8) | FAIL | N4 |
| 8.1 | The design lists its policy changes (§8) | PASS | |
| 8.2 | The policy list is complete (§8) | FAIL | B14 |
| 8.3 | §6.8's "policy lines 0 / one schema change" matches §8 | FAIL | B14 |
| 9.1 | The §6.8 per-pass cost figures (§6.8) | UNVERIFIED | |
| 9.2 | New self-tests are wired into CI (§6.2, §6.7) | FAIL | B5, N5 |

**Counts: 47 rows — PASS 19, FAIL 24, UNVERIFIED 4.**

---

## What the design gets right, and should keep

- The diagnosis of S1 (a level derived from an append-only history) is exactly
  right and independently reproduced: `relay_owed` keys on `f[2]` and never
  opens `cloud-disposed`; the board is a projection of a 30k-line history, and
  202 of its subjects carry a disposal the reader never opens, 200 of them at
  the ref's current sha at my read.
- S6's fail-open, S7's missing timeout and live-slot steal, and the six tick
  launches are all reproduced. The evidence, where it is honest, is unusually
  good.
- One supervised beat with per-job locks, timeouts and a runner-written journal
  is the right shape for S5. Separating the reader from the writer is right.
- The shared model builder is feasible: the roster walk already lives in
  `roster_lib.py`, and `plan_table.py` is already a renderer over it.
- Rejecting a monolith, CI, webhooks, a database and "make the tick a seat" is
  argued, not asserted.

The blocking findings are corrections and decisions, not a refutation of the
structure. Fix B1/B2/B3 (false figures and over-firing predicates), B4/B5/B15
(seams and inventory), B6–B11 (the mechanisms that do not yet bound, close or
fail closed), and re-derive B12/B13 against the tree and the file as they are —
then this design is implementable.
