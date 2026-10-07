Lands the R9-EG-B7 enumerator `tools/audit/harnesses/eg_b7_seam_hubs.py`. `Closes #1744`: that group halted by measurement, since no coordinator seam's cut fell, so no extraction was made. This lands the instrument that produced the halt, so a later seat can re-run it instead of trusting a comment.

The file is `301abb21` (branch `handoff/r9-eg-coordinator-seams`, not on main) with one change: the repository root is found by the harness convention (`repo_root`, marker walk) instead of a depth-counted `parents[3]`, which `tests/harness_headers.py`'s RO-7 depth-root scan refuses in this directory. Nothing under `custom_components/` or `tests/` changes. `dev/audit/README.md`'s kept-instruments table is the only harness index, but that file is policy (`POLICY_GLOBS`), so a row there owes an `## Approval`; it is left for the owner to add, and this PR touches no policy file.

Classification: `tools/audit/` is `INERT` in `tests/closure.py` (prefix), so the file needs no closure entry. `tests/harness_headers.py` lists every file in that directory under `inert_reads` in `tests/closures.json`; `scale_writer_seams.py` (3725f062) landed alone, and this PR does not hand-edit the recording (Linux-derived), leaving it to the closures autofix if it asks.

## Head

Code head `045864db20e7b3b80b00a280e059a98f5400a412` (the earlier head `244dc80f` merged with `origin/main` `be0cb82134bd3a008e59127da6f2b67fb1c77e98`), measured 2026-10-07T09:18Z.

## Mutation proof

n/a: no production line changes; the diff is one harness. The instrument's own sensitivity is the Null control below.

## Null control

A quantified claim of the instrument is "owned attributes of a seam are equal at the two trees". Control: archive HEAD's `custom_components` and `tests` to a temp dir, insert `self._ctl_probe_attr = 1` as the first statement of `_dhw_confidence_band` (a `dhw` entry in `tests/seam_map.json`), and run the harness's `measure` on both trees. Unmutated against HEAD the comparison is `True`; mutated it is `False`, and the added attribute is exactly `_ctl_probe_attr`:

    owned_equal dhw unmutated-vs-HEAD True
    owned_equal dhw mutated-vs-HEAD False added ['_ctl_probe_attr']

The hub loads are not constant either: the two trees print different `dhw` (11 against 12) and `fetch` (4 against 6) totals below, so the counter reads a difference when there is one.

## Figures

Rule: a hub load is one `ast.Load` of `_opt_config`, `_thermal_params` or `_current_state` through a state root, per `tests/structure.py`'s `seam_metrics` walk (`state_root_bindings`, `is_state_root`), bucketed by the method's entry in `tests/seam_map.json`. An owned attribute is one a seam's methods store through a state root. The base tree is `31567b71` (main before #1887), archived so the function text is the same on both.

Earlier measurement, tvofi's 2026-10-06T13:18Z comment on #1744 (at handoff `301abb21`, base `31567b71`):

| seam | cut then | cut now | hub loads then | hub loads now |
|---|---:|---:|---:|---:|
| dhw | 72 | 70 | 12 | 11 |
| views | 93 | 106 | 5 | 5 |
| learning | 294 | 296 | 28 | 29 |
| fetch | 117 | 115 | 6 | 4 |
| grid | 185 | 185 | 1 | 1 |

Crossing-seam calls 144 then, 149 now; `seam_cut_total` 761 then, 772 now; `hub_solve_writes` 40 then, 2 now. Owned attributes of all five seams unchanged.

Re-measurement at `origin/main` `be0cb821` plus this diff (identical to the 06:00Z run at `3910026e`) (hub-load and ownership lines of the instrument's output; the per-attribute lists are elided here):

    $ python3 tools/audit/harnesses/eg_b7_seam_hubs.py
    tree HEAD
    hub_loads dhw 11 _opt_config=0 _thermal_params=8 _current_state=3
    hub_loads learning 29 _opt_config=5 _thermal_params=13 _current_state=11
    hub_loads fetch 4 _opt_config=0 _thermal_params=3 _current_state=1
    hub_loads grid 1 _opt_config=0 _thermal_params=0 _current_state=1
    hub_loads views 5 _opt_config=1 _thermal_params=4 _current_state=0
    hub_loads core 124 _opt_config=25 _thermal_params=47 _current_state=52
    tree 31567b71820fe8e3380be30a19b7342360c3b6b8
    hub_loads dhw 12 _opt_config=0 _thermal_params=8 _current_state=4
    hub_loads learning 28 _opt_config=6 _thermal_params=11 _current_state=11
    hub_loads fetch 6 _opt_config=1 _thermal_params=4 _current_state=1
    hub_loads grid 1 _opt_config=0 _thermal_params=0 _current_state=1
    hub_loads views 5 _opt_config=1 _thermal_params=4 _current_state=0
    hub_loads core 152 _opt_config=45 _thermal_params=52 _current_state=55
    owned dhw 3 / learning 40 / fetch 13 / grid 31 / views 3 (identical at both trees)
    owned_equal dhw True
    owned_equal learning True
    owned_equal fetch True
    owned_equal grid True
    owned_equal views True

The five seam hub-load totals equal the earlier measurement's "now" column and the base column's `dhw` 12, `learning` 28, `fetch` 6, `grid` 1, `views` 5, so main's tip has not moved the halt's numbers. The cut and crossing-call columns are `seam_metrics`, which this harness does not print; `python3 tests/structure.py` prints `seam_cut_total 766 <= 766` at this head, not the 772 of `301abb21`, because main has moved since (the cut is a function of the tree; this table's earlier column is the comment's, not re-measured here).

- `python3 tools/audit/harnesses/eg_b7_seam_hubs.py` — hub loads and owned-attribute equality, above.
- `python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/seat/tmp_paths.py --check` — `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` — `MODE: SCOPED -- 0 script(s) run, 31 scoped out.`; changed file is the harness alone (measured at the earlier head `244dc80f`, which also had the README row).

## Red checks

- `delivery-status`: red on main, not on this diff. It grades main's delivery record; main's record-autofix staged the old `docs/delivery/` path, fixed by #2011. This diff adds one harness under `tools/audit/harnesses/` and reaches no delivery file; the only record row it will own is the orchestrator's own. Cheaper detector: none needed here, since the check already runs on every PR and names the cause; the standing cost is that it reads red on every PR until #2011 merges.
- `nightly-status`: red on main for the same reason (it grades main's nightly state, which this diff cannot reach). It clears when #2011 lands and main is green; this PR changes nothing it reads.

## Forward-carry

none

## Friction

none
