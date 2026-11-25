# D3-g25 working notes (partial, kept as I go)
- 2026-11-22 ~22:10Z: all 16 probes dry-run on a clean baseline worktree ($HOME/probe-base, never the gate tree): every one moves on its first input, null input flat.
  Index guards (6584/6632/6638/6640/6644/6648/6653): baseline key absent/0.0 at step 2 of a 2-long schedule, mutant IndexError.
  Mode bands (6602/6604/6606): exact p_norm 0.4/0.7/0.9 with a 0.5..3.0 kW band; GUARD_OFF 6604/6606 collapse normal->pre_heat, pre_heat->boost.
  6565: one-step plan 300 s pre-start, baseline step 0, mutant IndexError. 6566: now = t0-900 s, baseline step 0, mutant idle.
  6651: dhw_power 0.1 -> dhw_heating_active False vs True. 6655: dhw_target_temperature 55.0 vs absent.
- Should-fail pointers: features.py short-schedule block reads step 1 and step 3+1min, never step == len; #1499 mode block grades only p_norm 0 and 1;
  pre-horizon block uses a 3-step plan and skews 5 min / 2 h only.
- Records are written by probes/_shared/write_result.py once each key's gate lands (auto loop $HOME/scratch/autoresult.sh).
- Enumerator SURVIVORS.tsv is not in the baseline tree, e3cb5c0 or origin/main: the wave list is the orchestrator's; named as given.
- 22:33Z null take 1 (gate_rc 1, 2975 s): closure.py selftest 2 (skip-not-under-scoped, git/derive artefact), entities.py 1 ("one-script re-derive ... accepted when it does", derive artefact),
  harness_headers.py 4: three round4/D6/claims.py header/byte-identical (stripped-tree artefacts) and ONE caused by this box: probes/_shared/probe_template.py
  (placeholder `SPEC = @SPEC@`) sat in the gate tree and broke the repo_root corpus ast.parse. Kept as null-take1.{json,log}.
  Fix: template renamed .tmpl, probes use tools/audit/repo_root.py's helper verbatim. The f3126 gate started at 22:33Z was stopped by SIGINT (~25 min in,
  fullgate's finally reset the tree; no record kept) and the null re-taken once, as the brief allows.
- 23:23Z null take 2 (gate_rc 1, 2889 s, load1 0.53..0.94): red only on artefact checks: closure.py selftest 2 (skip-not-under-scoped), entities.py 1 (one-script re-derive), harness_headers.py 3 (round4/D6/claims.py header + byte-identical in the stripped tree). Usable; it is this box's null.
