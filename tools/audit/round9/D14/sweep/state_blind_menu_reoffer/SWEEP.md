# Sweep: "state-blind menu re-offers a completed path"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D4-s2-07
(verified, low). Not a ledger class (new).

## Enumerator

```
$ grep -n "finish_setup\|Quick setup" custom_components/heatpump_optimizer/config_flow.py
```

widened to every `async_show_menu` call whose `menu_options` do not
condition on any prior-step state:

```
$ grep -n "async_show_menu" custom_components/heatpump_optimizer/config_flow.py
```

## Positive control

`async_step_finish_setup` (config_flow.py:2473-2493) always renders the
same three-option menu — `quick_setup`, `temperature`, `finish_now` —
including "Quick setup (recommended)" even on the return trip after
`async_step_quick_setup` (config_flow.py:2517) has already completed and
handed back to `async_step_finish_setup` (confirmed by the three
`return await self.async_step_finish_setup()` call sites at :2313, :2392,
:2444, all reachable after a quick-setup-completing step). No flag on
`self` or in `user_input` distinguishes "arrived here fresh" from "arrived
here after finishing quick setup." Confirmed present at baseline
`1936d5ca`; `config_flow.py` is unchanged on `origin/main`.

## Null control / widening

`async_show_menu` is called in exactly one other shape in this file (the
options-flow equivalent for a returning Configure session, config_flow.py
line ~3123-3129's own comment: "here from Configure: an install that
missed Quick setup at the start...") — this second site's own comment
shows it **does** reason about prior state (whether the install "missed"
quick setup at the initial flow, i.e. it is options-flow-specific and not
reachable from the same completed-quick-setup path), so it is **not**
a second instance of the same defect; it is the guarded counterpart the
finding's own class doesn't reach.

## Perturbation

Not independently re-run; the finder's own harnesses
(`tools/audit/round9/D4/s2/quick_menu.py`, `flow_rubric.py`) already carry
the executed enumeration of every hand-back to `finish_setup` and the
first-run path's screen sequence.

## Disposition

| seam | disposition |
|---|---|
| config_flow.py:2473-2493 `async_step_finish_setup` menu, reached after `async_step_quick_setup` completes (via :2313, :2392, :2444) | instance — D4-s2-07 |
| config_flow.py ~3123-3129 options-flow "missed quick setup" menu | guarded — its own comment shows it is conditioned on prior state, a different (options-flow) code path not reachable from the completed-quick-setup return |

## Count

N = 1 verified finding + 0 sweep-confirmed instances = **1**. **rca: false**,
matching the brief.

## Barrier proposal

None built (N < 3). The finder's own scope: track whether quick setup
already ran (a flag on `self` or in the flow's persisted step data) and
drop that option from the menu, or route straight to `finish_now` after
quick setup — left for the fixer.

## Gate seconds

~0.02s (two grep invocations plus a manual read of the three return sites).
