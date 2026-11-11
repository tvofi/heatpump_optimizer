# R9-P11: root-cause analysis (round-9 RCA seat)

Class P11: the only oracle for an external counterpart is a test double shaped by
what the code needed. N = 6 (judge 6, sweep S4). Baseline `1936d5ca` (v6.7.1).
Prototype: `handoff/r9-rca-p11@82e645c3`, cut from `origin/main@db878b29`.
`tests/ha_contract.py` and `tests/hastub/**` are byte-identical at the two SHAs
(`git diff --quiet 1936d5ca origin/main -- tests/ha_contract.py tests/hastub`), so
every result below holds at both.

## Root cause

### Cause, reproduced at 1936d5ca

The six instances reproduced with the finder harnesses from `handoff/audit-r9-evidence`
and the S4 enumerator (`handoff/audit-r9-sweep-s4`), using `/home/claude/venv314`:

| finding | command | result at 1936d5ca |
|---|---|---|
| D1-s1-51 | `stub_store_codec.py` | `divergent=6 of_6` |
| D1-s1-52 | `stub_naive_clock.py` | `divergent=6 of_6`, `stub_now_naive=1` |
| D1-s2-71 | `l3_update_interval.py` | `unreadable_cells=4 of 4`, null control `4 of 4` readable |
| D6-s1-81 | `D14/sweep/P11/enumerate.py` | real-shaped config gives `EUR`; `SEK` only with the double's `currency=None` |
| D10-s1-03 | same | `reauth_falls_through_to_fetch_failed: True`, `ConfigEntryAuthFailed` referenced nowhere |
| D14-s4-02 | `p7_replay_clock.py` / `--zone-clock` | `replay_wrong_sites=0` / `=10` |

Real Home Assistant 2025.2.0 (`hacs.json`'s floor) was installed in a scratch venv
(`uv pip install homeassistant==2025.2.0`, Python 3.13) to measure the upstream side.
It prints `Config(object(), dir).currency == "EUR"`, `dt_util.now().tzinfo is
DEFAULT_TIME_ZONE` (UTC by default), and `update_interval` on `DataUpdateCoordinator`.

**The named cause is not "the stub was never checked".** A checker for exactly this
exists: `tests/ha_contract.py` (#578, 2026-09-07) runs one set of contracts against the
stub on the gate and against real Home Assistant nightly (`tests/nightly_ha.py`, invoked
from `tests.yml`). Every hastub symbol in this class had a disposition and a passing
contract. The instances got through three holes in what that checker measures:

1. **A contract can pass by asserting nothing** (D1-s1-52). `util.dt.now` is FAITHFUL,
   and its only contract is guarded by `if dt_util.DEFAULT_TIME_ZONE is not None:`. The
   stub's default clock sets that to `None`, which is also the divergent state. So the
   contract asserts nothing on the stub and passes. Upstream always configures a zone,
   so the contract holds there too.
2. **A test hook changes what a FAITHFUL symbol returns, and no contract runs under the
   hook** (D14-s4-02). `util.dt.freeze` is HOLDER ("a test-facing clock pin with no
   upstream counterpart"; HOLDER is defined as "makes no decision; no contract owed").
   Yet `freeze` decides what `now()` and `utcnow()` return, and it passes through a
   fixed-offset or naive datetime that upstream never returns.
3. **A stub parameter is accepted and then dropped** (D1-s2-71). The stub signature is
   `DataUpdateCoordinator.__init__(..., update_interval=None, ..., **_ignored)`, and the
   body never reads `update_interval`. SIMPLIFIED's teeth (`absent`) check only the
   members someone listed, and nothing checks an accepted-and-dropped parameter. #1002
   (#924) rewrote this stub under `fixer.md` step 13 and introduced this shape.

The other three instances lie outside anything the checker covers, and its docstring
says so: "WHAT THIS DOES NOT COVER".
- **Store codec, D1-s1-51.** The divergence is behaviour inside a method (stdlib `json`
  against orjson), and upstream's Store needs a running hass.
- **Tibber reauth, D10-s1-03.** `ConfigEntryAuthFailed` is "a symbol upstream has that
  the stub does not model at all" (informational only).
- **Currency, D6-s1-81.** The double is not in `tests/hastub` at all: the test is
  `resolve_currency(object()) == "SEK"` (`tests/entities.py`), and `harness.Hass` sets
  `currency = "SEK"`.

### Class search: what else the same cause reaches

Each search has a runnable enumerator in this folder.
- **Vacuous contracts (`vacuity.py`).** Of 59 contracts run on the stub, 3 reach no
  assert. Two have no assert at all and verify by not raising or by an explicit `raise
  AssertionError`. They are legitimate. The third is `util.dt.now`, which is the only
  guarded-vacuous one.
- **Hook re-runs (the barrier's arm 2).** These found one sibling no finder named: with
  the clock frozen at a fixed offset, stub `utcnow()` returns a `+01:00` datetime, where
  upstream always returns UTC. That fails `util.dt.utcnow: returns an aware datetime in
  UTC (frozen at a fixed offset)`. It uses the same `freeze` hook as D14-s4-02, so the
  same stub fix repairs it.
- **Dropped parameters (`dropped.py`).** 24 parameters across the stub are accepted and
  never read. 23 are deliberate: the `*a, **k` no-ops, `Store(hass, version)` with
  migration declared absent, and `async_get_translations`. `update_interval` is the only
  one that production passes and reads back.
- **Member parity (`parity.py`, real HA).** This was considered and rejected as a check.
  328 upstream class members are missing from FAITHFUL/SIMPLIFIED stub classes and not
  in `absent`. Restricting to names production uses still leaves 77, mostly instance
  attributes that a class `dir()` cannot see. Too noisy to gate.
- **Doubles outside `tests/hastub`.** A crude regex finds 13 ad-hoc hass/config doubles
  in `tests/*.py`: 9 are inside `ha_contract.py`, plus `harness.py`, `open_meteo.py` and
  the `object()` call sites. The barrier does not reach these.
- **Historical ledger.** `tools/audit/bugclasses.json` records P11 as `open`, with 10
  instances (v6.6.12 bugs 1, 3–7, two `@callback` listeners, #1290, #511). No historical
  instance is credited to this barrier, because none was re-run through it.

## Process state: (c)

**(c): the process was followed and did not produce the intended result.**

`fixer.md` step 13 says: "`tests/ha_contract.py` records what each stub symbol is … and
runs its contracts against both the stub and, nightly, the real package … If your work
depends on a symbol's upstream behaviour, add or read its contract". The seats obeyed it:
- the stub symbols in this class all carry dispositions;
- `util.dt.now` has a FAITHFUL contract, which passes on both providers;
- #1002 rewrote `DataUpdateCoordinator` with a documented `absent` tuple and contracts.

The checker's own completeness rule was also met: "every FAITHFUL symbol carries at least
one contract" passed. The product was still wrong, because the rule measures that a
contract **exists**, not that it **constrains the stub**. The file says this itself:
"Completeness forces a *disposition*, never a correct contract."

It is not (b), because nothing was skipped. It is not (d), because the dt.now guard and
the dropped parameter date from the checker's own landing (#578) and #1002. No
precondition changed later. A firmer instruction to "write better contracts" would be the
(c)-as-(b) error that `root-cause.md` names.

For currency and Tibber the checker declares the area out of scope, which amounts to (a)
for that part. The class as a whole is recorded as (c), because 3 of the 6 instances and
the barrier's reach sit inside a process that exists.

## Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, per release:

- **Standing cost.** On the stub, `tests/ha_contract.py` took 0.29–0.37 s unmodified and
  0.57–0.91 s with the prototype (5 runs each, same box), so about +0.3–0.6 s per run.
  Runs per release, upper bound: 632 first-parent `main` commits over the 24 releases
  after v6.3.18 is 26 forced-full gates per release (`git rev-list --count --first-parent
  v6.3.18..v6.7.1`). The 213 PRs in those releases (`RELEASE_NOTES.md`) give about 9 per
  release; assuming at most 10 scoped runs each gives about 90. Nightly adds about 30.
  That is about 150 runs × 0.6 s ≈ **90 s per release**.
- **Defect cost.** The v6.6.12 P11 fixes #1619, #1621, #1622, #1624 and #1626 took 15 h
  of first-commit-to-merge wall-clock across 6 bugs, so **≥ 2.5 h per instance**. That
  is a lower bound: it excludes diagnosis, user impact and audit seats.
- **P(recurrence), barrier-reachable only.** 3 of round 9's instances (D1-s1-52,
  D1-s2-71, D14-s4-02) use a route the barrier closes, over the 24 releases since the
  checker landed, so 0.125 per release. The whole class is 13 instances over those 24
  releases (#1290, 6 in v6.6.12, 6 in round 9), or 0.54 per release.
- **Result.** 0.125 × 150 min ≈ **18.8 min per release** of expected defect cost,
  against **1.5 min per release** of standing cost. The barrier passes, by about 12×.

## Countermeasure: class barrier (prototype)

The barrier is three arms added to `tests/ha_contract.py`, stub side, on the existing gate
path. Each closes one of the three holes above.

1. **Non-vacuity.** `_run_one` traces each contract and fails a pass that reached none
   of its `assert` lines. This also runs against real Home Assistant, so it holds
   nightly as well.
2. **Hook re-runs.** Each HOOK entry lists the FAITHFUL symbols a hook feeds, and
   `_run_hooked` re-runs their `expect="both"` contracts with the hook in each state the
   suite uses. For `freeze` that means frozen naive and frozen at a fixed offset.
3. **Declared drops.** `stub_dropped` finds, by AST, every parameter the stub accepts and
   never reads. Each must be listed in `DROPPED`, and a listed drop that is read again
   fails.

Evidence (commands run from the worktree root with `PYTHONPATH=tests/hastub`):

- **Fails on the defect.** At `1936d5ca` and at `origin/main` it reports `5 of 83
  contracts FAILED`:
  - `util.dt.now … [vacuous: reached none of its 2 assertions]`;
  - `every parameter the stub drops is declared [...DataUpdateCoordinator(update_interval)]`;
  - `util.dt.now … (frozen naive)`;
  - `util.dt.now … (frozen at a fixed offset)`;
  - `util.dt.utcnow … (frozen at a fixed offset)`.

  With `HASTUB_TZ=Europe/Stockholm`, the replay lane's configuration, `util.dt.now …
  (frozen at a fixed offset)` fails with `AssertionError`. That detection comes from the
  hook arm alone, not from vacuity.
- **Passes once fixed.** `fixed-sim.patch` applies what F10.1 owes:
  - `now()` aware by default, with a frozen value normalised into the zone;
  - `utcnow()` derived from `now()`;
  - `self.update_interval` stored;
  - the `now` contract rewritten to assert `tzinfo is DEFAULT_TIME_ZONE` when a zone is
    set, and awareness unconditionally.

  With it, the run reports `ALL 83 contracts PASSED`, both with no zone and with
  `Europe/Stockholm`.
- **Null control on upstream.** Against real Home Assistant 2025.2.0 (`--contracts-only`),
  both the prototype and the fixed contract file report `ALL 54 contracts PASSED`, with
  zero vacuous contracts. The strengthened `now` contract holds upstream.
- **Does not go green by skipping.** In-memory mutants from `skipctl.py`:
  - HOOKS emptied: `FAIL the hook re-runs ran`;
  - drop scan reads nothing: `FAIL the drop scan read the stub`, plus a stale-drop
    failure;
  - vacuity arm blinded (`_assert_lines` returns nothing): the three vacuity failures
    disappear and the other two stay. So the arm is load-bearing.
- **Ratchet and closures.** `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  `tests/closure.py no-copies`: clean. The only new imports are stdlib (`inspect`,
  `textwrap`). No new file, so no classification is owed.

**What the barrier does not eliminate, and which goes to tvofi.** Three of the six
instances have no mechanical barrier within the bound:
- **D1-s1-51, behaviour inside a method.** Only a written contract catches it, and
  `fixer.md` step 13 already makes F10.1 owe one.
- **D10-s1-03, an unmodelled upstream symbol.** Making every unmodelled name in a
  touched module need a disposition was measured too broad (see member parity).
- **D6-s1-81, a double outside `tests/hastub`.** Closing this route means building
  `harness.Hass` from a stub `core.Config` with upstream defaults, where real `currency`
  is `EUR`, and refusing ad-hoc hass doubles in tests. That ripples through every golden
  fixture pinned at `SEK`.

S4's proposal (per-instance contracts, nightly) is sound for these three, as instance
contracts. It does not eliminate the class: `util.dt.now` already had exactly such a
contract and a disposition, and it passed while asserting nothing. S4's premise that the
nightly real-HA run needs building is also wrong: `nightly_ha.py` already runs this file
against both providers. **tvofi decides** between two options for the outside-hastub
route:
- accept per-instance contracts there as the recorded answer;
- commission the harness-double refactor as its own item.

## Plan fold

- **Landing PR: F10.1, not F10.3.**
  - The barrier's only file is `tests/ha_contract.py`, which F10.1 already edits. It is
    neither code-owned (`.github/CODEOWNERS` has no entry for it or `tests/hastub`) nor
    policy.
  - It fails on the current tree until the stub fixes F10.1 owns are in (dt.now,
    update_interval, freeze/utcnow), so it has to merge with them.
  - Nothing it catches is fixed in F1.1, F1.7 or F8.3, and it needs no tvofi gate.
- **Lines.** The prototype is +168/−5 test lines in `tests/ha_contract.py`, with 0
  production lines. F10.1 adds about +10 test lines in `tests/hastub/homeassistant/util/dt.py`,
  `helpers/update_coordinator.py`, and the `now` contract rewrite, as `fixed-sim.patch`
  shows. No `*_budgets.json` raise is needed.
- **Scope added to F10.1.**
  - The `utcnow()`-under-aware-freeze sibling, which the barrier found.
  - `freeze` normalising into `DEFAULT_TIME_ZONE`. This is the stub half of D14-s4-02,
    and it covers all 100 `dt_util.freeze(` sites at once.
  - F1.1 keeps G3-V2's "step `run_fixture` in UTC" and should re-run `p7_replay_clock.py`
    after F10.1.
  - The golden ripple from an aware-by-default clock is already flagged in F10.1's notes.
    The freeze normalisation rides on the same ripple.
- **Edges.**
  - F10.3 drops P11 from its "Class barrier" line.
  - F10.3's `after` edges on F1.7 and F8.3 were justified by P11 ("Waits … on F1.7
    because the P11 barrier does"). They can go unless another reason holds; I found
    none in F10.md.
  - F1.1 gains `after: F10.1` for D14-s4-02's re-measurement.
  - F1.7 (the `ConfigEntryAuthFailed` stub symbol and its contract) and F8.3 (a stub
    `core.Config` currency contract, if chosen) keep their per-instance contracts under
    `fixer.md` step 13.

Evidence in this folder: `vacuity.py`, `dropped.py`, `parity.py`, `skipctl.py`,
`fixed-sim.patch`.
