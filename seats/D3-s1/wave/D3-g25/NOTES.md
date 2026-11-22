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
