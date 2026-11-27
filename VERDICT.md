Fix review: merge c499d7a659e1c835723ed16f254ae62f647a7d16

bus-nonce: 0ae5f2d7b43c454920047489f8de2077
pending-ci: gate

Round: first (no prior reviewed head).

## Findings

- Note: stale-figure: the body's `## Figures` line "at this head" quotes `s8:49f/0loc/3997u`; at c499d7a659e1c835723ed16f254ae62f647a7d16 `python3 -I tools/audit/check_scopes.py --repo .` prints `s8:49f/0loc/3999u` (3997 holds at the authored code head 7df39f349ae1b81dce5d8166ef7417119bda474d; the 7194ff84 main merge adds 2 units to s8). Paperwork only, no cap is near (4500). Carry: dismissed: paperwork figure, measured here, changes no later stage

## Evidence

- RESULT mutation: at #3869's head f211d7aa821747793e2c246df90e5cf5703fe5fc and #3883's head 642753ad975bc1e06a8942d971023b33ed608fa4 with their own scopes.json (the fix absent), `check_scopes.py --repo .` rc 1 `over ledger.max_units 4500: s7 holds 4520 units` / `4508 units`; `check_scopes.py --self-test --repo .` rc 1 `SELF-TEST FAILED` (the live-scopes arms False); `owner_only_channel.py` rc 1 `RESULT arms=48 failed=1`, `SCOPES null`. With this PR's scopes.json applied: rc 0 / rc 0 / rc 0, `s7:1f/0loc/4336u` and `4324u`, `SELF-TEST passed`, `OWNER-ONLY CHANNEL HELD`. Matches the body's mutation proof and null control. ev/mutation.txt.
- RESULT figures at the head: `check_scopes.py --repo .` rc 0, `s7:1f/0loc/4303u`; per-file D5 units `tests/features.py` 4303, `tests/finite_boundary.py` 160, `tests/frontend.py` 24 (`text_ledger.py --dim D5 units <file> | wc -l`), all equal to the body. ev/check_scopes_head.txt, ev/units_head.txt, ev/check_scopes_7df39f.txt.
- The re-cut is total: `tests/f*` matched exactly `features.py`, `finite_boundary.py`, `frontend.py` in the D5 universe; `fe*` plus `fi*`, `fr*` cover the same three, and `check_scopes.py` (every cell owned exactly once) passes at the head and at both PR heads with the fix applied. A one-seam class: the claim quantifies over D5 seat s7 only, and the cap check names it.
- Not re-derived: the body's figure for both PRs and this head merged together (`s7:1f/0loc/4357u`): #3869's live head 8a9fe044 conflicts with this head in `dev/audit/rounds/round3/D5/option_doc_coverage.py` (that PR's own conflict), so I measured at the body-named heads instead.
- Three-dot diff: `dev/audit/config/scopes.json` (4 lines) and `dev/programme/delivery/3924.md` (the delivery row); VERSION, manifest and notes heading untouched; no claim file touched; no production code, so no actuator write (step 16 n/a). ev/diffstat.txt.
- `git merge-tree --write-tree origin/main c499d7a659e1c835723ed16f254ae62f647a7d16`: rc 0, merges cleanly. ev/merge_tree.txt.
- Role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` empty.
- Finder's harness: none named in the packet; the red steps' own commands (`owner_only_channel.py`, `check_scopes.py --self-test --repo .`) served as the harness at both ends, as the body names.
- CI: `merge_train.py classify c499d7a659e1c835723ed16f254ae62f647a7d16 --pr 3924` printed `WAIT c499d7a659e1c835723ed16f254ae62f647a7d16 pending: gate red: none` (rc 3) on every poll, 90 s apart, 23:53 to 00:22 UTC; no red at this head; returned with `pending-ci: gate`.
