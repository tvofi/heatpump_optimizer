R10-LIVE-BUNDLE-READS (issue #3120), repair round 2. Closes #3120.

The fix (round 1, unchanged): `tools/replay/debug_ingest.py` `load_bundle` unwraps `data.debug` when the top level is a Home Assistant "Download diagnostics" file (`unwrap_download`), and stage 4 compares the store window and the rows over the samples both hold, each stamp once (D15-s1-03, D15-s1-01). Design choice, said so a reader does not take it for a bug: the comparison is over the intersection, and it still fails (not vacuous) when the intersection is empty.

This round settles the block of verdict/3186 (class-open: `dev/audit/rounds/round10/D15/s1/intake.py`). With `load_bundle` unwrapping, the finder's harness lost its wrapper: `bundle_unwrapped` read 0 on every download and `--perturb unwrap` did nothing. The repair:
- `debug_ingest.read_download(path)`: the file as handed, gunzipped and parsed, wrapper intact. `load_bundle` is now `unwrap_download(read_download(path))`, so there is still one loader and no second gzip/json path.
- `intake.py` reads the download through `read_download` (on a tree before it exists, `load_bundle` is that reader, so the harness still runs at the base); `bundle_unwrapped` is measured on the file as handed again. Its wrapped M3 arm is now what `load_bundle` hands `ingest` (the tool's own path), and `--perturb unwrap` flips that unwrap, so the arm moves at both ends. Header updated to say so.
- The verdict's finding: `intake.py` M4 called `store._store_name`, which the tree names `store_name`; it crashed at base and head, so the store metrics never printed. Fixed; they print at both ends.

Alternatives, and why each lost: reading the raw file inside `intake.py` (a second gzip/json loader beside `load_bundle`, duplicated concept); dispositioning the seam in the body and leaving the harness blind (its M1 and M3 wrapper arm would stay meaningless for the next live bundle); keeping the old "unwrap" perturbation semantics (at the head it is a no-op by construction).

LOCAL-SAFE: this round read no live bundle. Every figure below is from the synthetic download `debug_ingest._download(debug_ingest._tail_repeat_bundle())` the reviewer used, or the bare `_tail_repeat_bundle()` as the null control, written to a scratch file outside the tree. The round-1 live-bundle reads (carries 1, 3, 4, 5 and L-a, L-b) are not re-taken and not restated here: they stand as recorded in the round-1 body (handoff-body ref 9ab3e10c, code 06234008), and this diff does not touch the code they measured beyond `load_bundle`'s extraction, which is behaviour-identical (the wrapped-download arm of `gate_checks()` is green).

Carry dispositions (roster carries of R10-LIVE-BUNDLE-READS, numbered from 1): carry 1 (R10-HEAT-METER, L9 `unhealthy_input`) done, no code change; carry 2 (R10-REPLAY-REAL-DAY carry 4) dismissed as the duplicate of carry 1 the roster marks; carry 3 (L6 house meter age) done, no code change; carry 4 (R10-SCORES `--bundle` scale drift) done; carry 5 (D15-s1-01, D15-s1-03, L-a, L-b) fix landed, L-a dismissed with its reading, L-b reproduced and by design; carry 6 (coordinator lane note) honoured, no `coordinator.py` edit. The verdict's own carry (the `_store_name` crash, `Carry: R10-LIVE-BUNDLE-READS`) is closed in this diff.

Handed to the orchestrator, not landed by this seat (a fixer writes no roster): round 1's three items for R10-ROUND-PLAYBOOK (a version change across a gap is a restart whatever its length; the "Round-11 D15 inputs" carry is done in this group and may be discharged; re-read `unhealthy_input` on the next bundle) are on handoff/audit-r10-roster at 4d89ce26ccfd20bbfc8fc0b675245370ead6deb3, as the verdict records, to land as roster ops before merge.

## Head

df48d4e7a3d0698bce3002023767bc3d6bc6b1fe

## Mutation proof

Round 1 (re-run this round through `debug_ingest.gate_checks()` at the head): failing first, the wrapped download fails 6 of 12 stages at the base and the tail-repeat bundle fails bias-rederived; mutants unwrap removed, de-duplication removed, `shared = sorted(held)`, each go red as the verdict's ev/mutants.txt records (M1, M2, M3).

New pin, this round: `gate_checks()` arm `debug ingest: read_download keeps the wrapper the harnesses measure`. Mutant: `read_download`'s `return json.loads(raw)` changed to `return unwrap_download(json.loads(raw))`. `gate_checks()` then reads 7 of 8, FAILING: `['debug ingest: read_download keeps the wrapper the harnesses measure']`. Restored; 8 of 8, `git diff` shows only the fix.

The harness repair, mutated the other way: the head's `--perturb unwrap` arm is itself the mutant of the tool's unwrap (it feeds `ingest` the raw download), and moves `ingest_fails_wrapped` 0 -> 6 at the head (Figures).

## Null control

The bare synthetic bundle (`_tail_repeat_bundle()`, no wrapper) through the repaired harness: `bundle_unwrapped=0`, and `--perturb unwrap` leaves `ingest_fails_wrapped` unchanged at both ends (base 1 -> 1, head 0 -> 0), so the perturbation moves only when a wrapper exists. `gate_checks()`'s pre-existing arms (clean bundle, `--corrupt accuracy` refused, planted credential) read the same as round 1.

## Figures

Finder's harness: `dev/audit/rounds/round10/D15/s1/intake.py` (D15-s1-01, D15-s1-03), the repaired copy at the head, run at both ends: base `a9c2f90fc77be2e7a870f3f2735dcd0f79b5f475` (the merge base) and the head, from each tree's root, `PYTHONPATH=tests/hastub python3 <intake.py> --bundle S [--perturb unwrap]`, with S the synthetic download above. Counts only.
- base, S: `bundle_unwrapped=1`, `ingest_fails_wrapped=6`, `ingest_fails_unwrapped=1` (bias-rederived), `bias_delta_tail=0.25`, `bias_delta_by_t=0.0`, `store_docs=1`, `store_off_domain_fields=0`; no traceback (the committed harness crashed in M4 at both ends: verdict ev/finder_harness_intake.txt).
- base, S, `--perturb unwrap`: `ingest_fails_wrapped=1` (6 -> 1, the finder's documented movement).
- head, S: `bundle_unwrapped=1` (the committed harness read 0 here: the block), `ingest_fails_wrapped=0`, `ingest_fails_unwrapped=0`, `bias_delta_tail=0.0`, `bias_delta_by_t=0.0`, store metrics print.
- head, S, `--perturb unwrap`: `ingest_fails_wrapped=6` (0 -> 6; the committed harness's arm was a no-op here).
- bare bundle, both ends, with and without `--perturb unwrap`: `bundle_unwrapped=0`; wrapped arm equal to the unwrapped arm (base 1, head 0).

`debug_ingest.gate_checks()` at the head: 8 of 8 ok (`PYTHONPATH=tests/hastub python3 -c 'import sys;sys.path[:0]=["tools/replay","tests","custom_components"];import debug_ingest as d;print([n for n,ok,_ in d.gate_checks() if not ok])'` prints `[]`).

Seams for the class (fixer.md step 8). Rule: `git grep -n "load_bundle" tools tests dev`, re-run at the head; every line it returns:
- `tools/replay/debug_ingest.py` `def load_bundle`: the loader; now `unwrap_download(read_download(path))`. Closed in this diff.
- `tools/replay/debug_ingest.py` `_via_file` (`(reader or load_bundle)(path)`): the gate's own file round-trip; reads through `load_bundle` by default and `read_download` for the new arm. Closed in this diff.
- `tools/replay/debug_ingest.py` `main` (`ingest(load_bundle(args.bundle), ...)`): the `--bundle` path the fix is for. Closed (round 1).
- `tools/replay/debug_replay.py` (`bundle = debug_ingest.load_bundle(args.bundle)`): gains the unwrap; it wants the bundle, not the wrapper. Closed (round 1).
- `dev/audit/rounds/round10/D15/s1/intake.py` `main` (`getattr(di, "read_download", di.load_bundle)` and `di.load_bundle(a.bundle)`): the finder's harness; repaired in this diff, as above.
- `dev/audit/rounds/round10/JUDGE-INPUT.json` (two lines), `dev/audit/rounds/round10/intake/out/normalised-reports.json` (two), `dev/audit/rounds/round10/reports-B11.json` (two): the finding's `seam_rule` and `proposed_fix_scope` as recorded; a record, not a reader. No change.
- `dev/programme/rosters/wave-r10-groups.json` (the R10-LIVE-BUNDLE-READS roster text): describes the fix; not a reader. No change.
Correction of the round-1 body: its caller list named `dbg_bundle_gen.py`, which does not call `load_bundle`, and omitted `intake.py`; the list above is the rule's output.

Readers of the harness's wrapper metric and unwrap arm, rule `git grep -n "bundle_unwrapped\|perturb unwrap\|D15/s1/intake"` at the head: `intake.py` itself (repaired); `dev/audit/rounds/round10/D15/s1/REPORT.md` (the finder's measurement record of the base-era `6 -> 1`, which the repaired harness reproduces at the base; a record that recounts, left as written); the round-10 JSON records named above and `tests/closures.json` (the file's classification entry). No other reader.

Gate: `tests/closure.py select --diff <merge base>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, running `tests/entities.py`: ALL 2607 ENTITY CHECKS PASSED. `tests/structure.py`: STRUCTURE RATCHET PASSED. `tests/harness_headers.py`: ALL 112 HARNESS HEADER CHECKS PASSED. `tools/pr/prepr.sh`: rc=0 at the head. Toolchain: `cloud-setup.sh --check` OK; numpy 2.5.4 and scipy 1.18.1 match `tests/requirements-ci.txt`. No production file under `custom_components/` changed, so no golden can drift; claim files, `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched. origin/main is 616868bdc5ca54d9555cfc89715f05a33527661e at 2026-11-04T10:46Z, unmoved since the prepr.sh run, so no second run; it merges with this head without conflict (`git merge-tree --write-tree origin/main HEAD`), so no merge was made (fixer.md step 6).

## Red checks

- tests / nightly-status: red on main's ancestry, not this PR's; the job reports main's nightly run, and this diff reaches nothing it reads (two files under `tools/replay/` and `dev/audit/`). No cheaper detector exists for it on this branch: the cause is upstream of the diff, and the nightly's own seat owns it.

## Forward-carry

- The verdict's surviving mutant M5 (`"schema" not in doc` guard dropped): equivalent on the bundle's reachable domain (every bare bundle carries `schema`, `debugger.py` `BUNDLE_SCHEMA`; none has a top-level `data`). Carry: dismissed: equivalent mutant on the bundle's reachable domain

## Friction

none
