# D6 — verify-v3-leads (V3: reach and class)

## D6-s1-81 — README's SEK currency fallback unreachable under real Home Assistant

**Executed numbers.** Downloaded the two required HA core wheels myself: `/home/claude/venv314/bin/python -m pip` has no `pip` module, and the system `pip3` resolves against CPython 3.11, which PyPI refuses for `homeassistant==2025.2.0`/`homeassistant` (both require Python >=3.13). Worked around with `python3 -m pip download --no-deps --python-version 3.14 --only-binary=:all: -d /tmp/hpo-wheels-verify <spec>`, which pulled `homeassistant-2025.2.0-py3-none-any.whl` and `homeassistant-2026.2.3-py3-none-any.whl`. Re-ran `tools/audit/round9/D6/leads/l4_currency_fallback.py --wheels /tmp/hpo-wheels-verify`: baseline `fallback_reached=0 of 2` (both wheels: `Config.currency default='EUR' -> resolve_currency='EUR'`); `--perturb`: `2 of 2`. Exact match. load1 2.30, thread_factor 1.000.

**Independent measurement.** Wrote `tools/audit/round9/D6/verify-v3-leads/v3_currency_wheel_recheck.py`: a plain line-scan of `homeassistant/core_config.py` inside each wheel (bypassing the finder's AST walk of `Config.__init__`), confirming `self.currency: str = "EUR"` verbatim on both 2025.2.0 and 2026.2.3. Also confirmed `README.md`'s "SEK when the instance has none" sentence and `currency.py`'s `FALLBACK_CURRENCY = "SEK"` are both present as claimed.

**Attacks.** This finding is exactly the real-HA-vs-stub axis the V3 lens exists to check, and the direction is unambiguous: real HA core, at both the hacs.json floor and current stable, always initializes `Config.currency` to `"EUR"` — never falsy — so `currency.resolve_currency`'s SEK fallback is reachable only through `tests/harness.py`'s `FakeHass` (which pins `currency="SEK"` itself), confirmed by the null control (`stub_resolves_to=SEK`). No wrong money or comfort result follows: real HA never leaves currency unset, so the fallback is unreachable dead code, not a live misfire — hygiene/low is correct.

**Class.** `P11` (the only oracle for an external counterpart is a test double the implementer wrote from what the code needed) — exact match: the README's SEK claim was written to agree with the stub, not with upstream.

**Metric definition.** HA core versions for which `resolve_currency` on core's own `Config.currency` default returns `FALLBACK_CURRENCY`.

**Vote: verify.** Severity low, class P11, seam_rule_enumerates true.
