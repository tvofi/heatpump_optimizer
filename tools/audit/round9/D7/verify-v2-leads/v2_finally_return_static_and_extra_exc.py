"""verify-v2 (independent lens, D7-s3-51): re-check tests/nightly_ha.py:_async_check_a4's
finally-block return by (1) a static AST walk that finds every `return` lexically inside a
`finally` block anywhere in the file (the finder's harness targets this one function; I check
the whole file for a "seam_rule"-quality independent grep), and (2) a dynamic run with exception
types the finder's harness did NOT use (ValueError, asyncio.TimeoutError) to show the swallow is
not particular to CancelledError/KeyboardInterrupt, plus one exception that IS caught inside the
inner try (a plain Exception on the FIRST refresh) as a null control -- the finding's own claim is
about a BaseException the inner handler does not catch, so a plain Exception should NOT need the
outer finally's masking behaviour to reach a normal check_a4_recovered call; the swallow instead
happens because of a *second*-refresh failure regardless of what raised on the first.

Metric definition (mine): (a) count of `return`/`break`/`continue` statements whose nearest
enclosing block is a `finally` handler, walked over the whole tests/nightly_ha.py AST (PEP 765
lints all three; the finder measured returns only) -- independent structural evidence that this is
a real control-flow hazard, not a single cherry-picked line; (b) of 3 extra dynamic arms
(ValueError, asyncio.TimeoutError, RuntimeError on the first refresh; recovery refresh raising in
every arm), how many still swallow via the same code path.

Run from cwd=/home/claude/ev2:
    python3 tools/audit/round9/D7/verify-v2-leads/v2_finally_return_static_and_extra_exc.py
Expected (mine): finally_early_exits=1 (the one at nightly_ha.py:1274, `return` inside the
`except Exception` nested in the outer `finally`); swallowed_extra=3 of 3 (ValueError,
TimeoutError, RuntimeError on the first refresh all still get masked by the SAME finally-return
when the recovery refresh then raises) -- corroborating the finder's mechanism claim (any
first-refresh outcome, if the recovery refresh then raises, is swallowed) independently of their
exact BaseException choice.
Baseline / tree: evidence branch 96b89163.
"""
import ast
import asyncio
import os
import sys
import types

ROOT = os.getcwd()
PATH = os.path.join(ROOT, "tests/nightly_ha.py")
if not os.path.isfile(PATH):
    print("ERROR: run from cwd=/home/claude/ev2", file=sys.stderr)
    sys.exit(2)

src = open(PATH).read()
tree = ast.parse(src)

early_exits = []
for node in ast.walk(tree):
    if isinstance(node, (ast.Try,)):
        for stmt in ast.walk(ast.Module(body=node.finalbody, type_ignores=[])):
            if isinstance(stmt, (ast.Return, ast.Break, ast.Continue)):
                early_exits.append((node.lineno, stmt.lineno, type(stmt).__name__))

print("early-exit statements lexically inside a `finally:` body:")
for owner_line, stmt_line, kind in early_exits:
    print(f"  try@line {owner_line}: {kind} at line {stmt_line}")
print(f"RESULT finally_early_exits={len(early_exits)} count")

# --- dynamic: three exception types the finder's harness (CancelledError, KeyboardInterrupt)
# did not exercise, each on the FIRST refresh, with the recovery refresh always raising.
sys.path.insert(0, "tests")
code = compile(src, PATH, "exec")
mod = types.ModuleType("nightly_ha_probe_v2")
mod.__file__ = PATH
exec(code, mod.__dict__)
mod.break_price_source = lambda broken: None
mod._a4_records = lambda hass, entry: []


class Hass:
    async def async_block_till_done(self):
        return None


def arm(first_exc):
    calls = {"n": 0}

    class Coord:
        last_update_success = False

        async def async_refresh(self):
            calls["n"] += 1
            if calls["n"] == 1:
                raise first_exc
            raise RuntimeError("recovery refresh failed")

    entry = types.SimpleNamespace(runtime_data=Coord(), entry_id="e")
    try:
        asyncio.run(mod._async_check_a4(mod.Checks(), Hass(), entry))
        return 1  # returned normally: the exception was swallowed
    except BaseException:
        return 0  # propagated: not swallowed


extra_arms = [ValueError("boom"), asyncio.TimeoutError(), RuntimeError("first refresh failed")]
results = [arm(e) for e in extra_arms]
for exc, r in zip(extra_arms, results):
    print(f"arm first_exc={type(exc).__name__:16s} swallowed={bool(r)}")
print(f"RESULT swallowed_extra={sum(results)} of {len(results)} count")

# null control: recovery refresh SUCCEEDS -> no masking should occur regardless of the first
def arm_recovery_ok(first_exc):
    calls = {"n": 0}

    class Coord:
        last_update_success = False

        async def async_refresh(self):
            calls["n"] += 1
            if calls["n"] == 1:
                raise first_exc
            return None

    entry = types.SimpleNamespace(runtime_data=Coord(), entry_id="e")
    try:
        asyncio.run(mod._async_check_a4(mod.Checks(), Hass(), entry))
        return 1
    except BaseException:
        return 0


ctl_results = [arm_recovery_ok(e) for e in extra_arms]
print(f"RESULT control_swallowed_extra={sum(ctl_results)} of {len(ctl_results)} count "
      "(recovery refresh succeeds: expect 0 -- ValueError is caught by the inner handler and "
      "recorded as a normal check failure, not propagated, so a 1 here would not itself be a bug)")

print("RESULT thread_factor=1.000")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except Exception:
    print("RESULT load1=n/a")
