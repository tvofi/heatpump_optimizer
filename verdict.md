Fix review: blocked 55508355c592dd3fb9734c541f705dd54fc19773 class-open: Home Assistant's frame.report_usage writes a log record up to ERROR through a logger its call names nowhere, neither refused nor in the event-loop census, and by the body's own split it belongs with the refused handlers

bus-nonce: 6f5e0e80e3802b23a53380d6098a21a8

Round 7. This is a later round over the reviewed head f2d21754. The PR's own delta is `git diff f2d21754 55508355`: three commits (ffbf4f1f, adfb82bd, f77af41b), merged in at 55508355. They touch only `tests/entities.py`. There is no production delta, so the scope does not widen. From the fourth round, `fixer.md` owes a re-cut. The body already carries a `## Re-cut` section.

## Block

The delta draws a line. In the body's words, "a handler's effect is the record, as `warnings.warn`'s is", so the two asyncio handlers are refused. Methods that "log as a side effect of other work" go to the residue, and that includes "Home Assistant's and aiohttp's helpers". One Home Assistant helper falls on the refused side of that line, and the delta leaves it unread:

- `homeassistant.helpers.frame.report_usage(what, ..., level=logging.WARNING)`. Its docstring says "Report incorrect code usage". For a custom integration, `custom_integration_behavior` defaults to `ReportBehavior.LOG`. The call then reaches `_report_usage_integration_frame`, which does `_LOGGER.log(level, "Detected that %sintegration ...")` with the caller's `level` (`ev/ha_frame_2025.11.3_326-360.txt`, read from the `homeassistant==2025.11.3` wheel, sha1 in `ev/ha_wheel_sha1.txt`; `hacs.json` declares 2025.2.0). Writing the record is the call's whole job. The level is the caller's to set, and `logging.ERROR` passes the spelling arm.
- At this head, `ev/probe_r7_ha.py` reads `ha_report_usage barrier=0 alias=[]` for `report_usage('x', level=logging.ERROR)`. It reads the same for `frame.report_usage('uses x')` inside `_async_update`. The control `ctl_warning` reads `barrier=1` (`ev/probe_r7_ha_5550.txt`).
- `report_usage` deduplicates per call site (`_REPORTED_INTEGRATIONS`), so it cannot flood. That matters for the N-log-flood barrier. It does not matter for the reach check's claim, which is "every logger the package can reach from text written in its shipped tree is either a `_LOGGER.<level>(...)` call that the barrier reads or is refused". The coordinator handover is a self-latched logger too, and it is allowed by name with its reason, not left unread.
- `grep -rnE "report_usage|frame\.report" custom_components/` prints nothing. So this is a predicate's unguarded domain, not a live site.
- This is the one seam this review found. The census enumerates `asyncio.SelectorEventLoop` alone. Nothing enumerates the Home Assistant or aiohttp helpers that the residue names, so I owe no hunt past this one. Ways out: refuse `report_usage` by spelling, as the delta refuses the handlers; or allow it by name with its reason (the per-site latch), as the coordinator handover is; or redraw the split so that a dependency API whose job is the record is residue too, and state why the handlers differ.
- No Home Assistant runs on this seat. The record is read from the helper's source, not observed in a live run. That is the reviewer's harness, disclosed as such.

## Prior finding: resolved

Round 6's shapes are refused at this head. `ev/probe_r7.py` reads each one at both ends (`ev/probe_r7_5550.txt`, `ev/probe_r7_f2d2.txt`):

- `exc_handler`, `exc_handler_default` and `exc_handler_per_cycle` read `alias=[]` at f2d21754. At this head they read `asyncio.get_running_loop().call_exception_handler`, `asyncio.get_running_loop().default_exception_handler` and `self.hass.loop.call_exception_handler`.
- Shapes this review added are refused at the head and read `[]` at f2d21754: `getattr(loop, 'call_exception_handler')`, `operator.methodcaller('default_exception_handler', ...)`, `B.call_exception_handler` from an imported `BaseEventLoop`, `b'call_exception_handler'`, a fullwidth `ｈandler` and `dict(call_exception_handler=1)`.
- The controls are unchanged at both ends: `ctl_warning barrier=1 alias=[]`, `ctl_re_compile barrier=0 alias=[]` and `ctl_set_handler` (`loop.set_exception_handler(None)`) `barrier=0 alias=[]`.

## Findings

- Residual: `_r11_loop_unread` is computed over `_r11_loop_logging | _R11_LOOP_LOGGING_RESIDUE`, so a residue name that is not in the census still passes `_r11_loop_unread == _R11_LOOP_LOGGING_RESIDUE`. Mutant N4 adds the non-logging `run_forever` to the residue, and the reach check stays `ok` (`ev/mutants_r7.txt`). On CPython 3.12.3 the census lacks `_stop_serving`, yet it passes for the same reason (`ev/census_r7.txt`). So a residue entry that a Python release makes stale is never refused. This is the safe direction: an unread logging method still fails (N5). Carry: dismissed: over-naming the residue cannot hide an unread logging method, and the open direction fails under N5; the body's "a logging method a Python release adds fails" holds, and a removal is not claimed

## Evidence

- Mutation (`ev/mutants_r7.sh`, the round-6 reviewer's `ev/reach_drv.py` with `asyncio` added to its namespace, because the section now reads the module-level import): unmutated, `ok` for `R10 N-no-expiry barrier`, `R10 N-log-flood barrier` and `R11 N-log-flood barrier reach`. The reach check prints `FAIL` under N1 (`| handlers` dropped from `reached`), N2 (the handler alternation dropped from `names_one`), N3 (`default_exception_handler` dropped from `handlers`), N5 (`_run_once` dropped from the residue) and N6 (the census regex never matches). N4 survives, as the Findings entry above records. Results: `ev/mutants_r7.txt`.
- Census (`ev/census_r7.txt`): CPython 3.14.7 and 3.13.18 each return the body's seven names: `_run_once`, `_stop_serving`, `call_exception_handler`, `create_datagram_endpoint`, `create_server`, `create_unix_server`, `default_exception_handler`. CPython 3.12.3 returns the same names less `_stop_serving`. CI pins 3.13 and 3.14.
- `grep -rnE "exception_handler|create_server|create_datagram_endpoint|create_unix_server|_run_once|_stop_serving" custom_components/` prints nothing at this head. This matches the body.
- `git merge-tree --write-tree origin/main 55508355` at origin/main 63c6d1cf exits 0 (`ev/merge_tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md`, both claim files and `tests/closures.json` are untouched three-dot against the merge base 053c33bc. `tests/structure_budgets.json` adds only the two new rows, reviewed in earlier rounds; the delta does not touch it (`ev/untouched.txt`). `python3 tests/structure.py` at this head prints `STRUCTURE RATCHET PASSED` (`ev/structure_r7.txt`).
- The body's `## Head` names 55508355, the head reviewed here.
- Figures I could not re-derive: `ALL 2737 ENTITY CHECKS PASSED` and `1 of 2737 ENTITY CHECKS FAILED` (the full `tests/entities.py` run), and `long_units_head=1622`. These are the fixer's and are left to CI's runs at this head. The heavy gate was not re-run (tvofi 2026-09-30).
- CI at this head: `merge_train.py classify` printed `WAIT 55508355... pending: gate red: none` on every run (`ev/classify.txt`). With no red, no `## Red checks` answer is owed. The owed-reds set is in `ev/owed_reds.txt`.
- The finder's harness: the packet reads `none named`. This review's harness is the probes under `ev/` and the reach driver, and it is the reviewer's, disclosed as such.
- Closing self-audit: `carry_audit.py check` printed `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc 0. Its `--body` was the body's `## Friction` section alone; the packet's run over the whole body at this head routed that section's one item.
- Head re-read before return: `fix/r11-seam-ratchets` is still at 55508355.
