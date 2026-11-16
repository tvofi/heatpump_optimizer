"""D17-s1-02 harness: a computed-default field kept at its shown value is lost when
the same submit changes the field its default is computed from.

Metric: over every config_flow._OPTION_FIELDS row whose default is a _Computed reading
another numeric field rendered on the same options page (sources discovered by
recording which keys the _Computed callable reads), the number of rows where:
the entry stores source=A (form shows the computed field = A), the user submits the
page with source=B and the computed field left at its shown A, and afterwards the
restarted coordinator's EntryConfig value for the computed field is not A.
Count key: EntryConfig.from_mapping({**entry.data, **entry.options}).<field> after the
real save, falling back to .<source> where it is None (the documented 'defaults to the
weekday value', the value the solve plans with), never the posted input.
Instrumented symbol: heatpump_optimizer.config_flow:_omit_unstored_computed, driven
through the page's real async_step_<page>.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s1/h_computed.py
Expected: RESULT computed_rows=12, RESULT computed_same_page_numeric=8,
          RESULT computed_kept_value_lost=8 (exact, a count)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-merged wraps _omit_unstored_computed so the computed default
is taken over {**current, **user_input} (the configuration the save produces):
computed_kept_value_lost goes to 0. Null control: the same walk with the source left
unchanged (B=A) loses nothing (RESULT null_kept_value_lost=0).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402

if "--perturb-merged" in sys.argv:
    def _omit_merged(user_input, current, hass):
        cleaned = dict(user_input)
        merged = {**current, **user_input}
        for row in cf._OPTION_FIELDS:
            if not isinstance(row.default, cf._Computed) or row.key in current or row.key not in cleaned:
                continue
            others = {k: v for k, v in merged.items() if k != row.key}
            try:
                computed = row.default.of(others, hass)
            except Exception:  # noqa: BLE001
                continue
            if cf._same_setting(computed, cleaned[row.key]):
                del cleaned[row.key]
        return cleaned

    mock.patch.object(cf, "_omit_unstored_computed", _omit_merged).start()


class Rec(dict):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.read = set()

    def get(self, k, d=None):
        self.read.add(k)
        return super().get(k, d)

    def __getitem__(self, k):
        self.read.add(k)
        return super().__getitem__(k)

    def __contains__(self, k):
        self.read.add(k)
        return super().__contains__(k)


def sources(row, hass):
    r = Rec()
    try:
        row.default.of(r, hass)
    except Exception:  # noqa: BLE001
        pass
    return sorted(r.read - {row.key})


def number_cfg(form, key):
    sch = form["data_schema"]
    for k, v in sch.schema.items():
        if type(v).__name__ == "section":
            for k2, v2 in v.schema.schema.items():
                if str(k2) == key:
                    return getattr(v2, "config", None) if type(v2).__name__ == "NumberSelector" else None
        elif str(k) == key:
            return getattr(v, "config", None) if type(v).__name__ == "NumberSelector" else None
    return None


async def walk(page, field, src, a, b):
    """Entry stores src=a; submit src=b with field kept at its shown value; return effective field."""
    flow, entry, hass = rig.new_flow(options={src: a})
    form = await getattr(flow, f"async_step_{page}")(None)
    ans = rig.schema_defaults(form)
    shown = ans.get(rig.field_section(form, field), ans).get(field) if rig.field_section(form, field) else ans.get(field)
    sec = rig.field_section(form, src)
    (ans if sec is None else ans.setdefault(sec, {}))[src] = b
    res = await rig.submit(flow, page, ans)
    eff = EntryConfig.from_mapping({**entry.data, **entry.options})
    val = getattr(eff, field, None)
    if val is None:  # documented fallback: unset reads as the weekday / ordinary value
        val = getattr(eff, src, None)
    return shown, res.get("errors"), val, dict(entry.options)


# In-band (A, B) per source: A is what the entry stores, B what the submit sets.
PAIRS = {"comfort_temp_day": (22.5, 21.0), "comfort_temp_night": (20.5, 19.5),
         "day_start_hour": (8, 7), "day_end_hour": (21, 22)}


async def main():
    flow, entry, hass = rig.new_flow()
    rows = [r for r in cf._OPTION_FIELDS if isinstance(r.default, cf._Computed)]
    measured = lost = null_lost = 0
    for r in rows:
        srcs = sources(r, hass)
        page = r.page if hasattr(r, "page") else r[0]
        f0, _, _ = rig.new_flow()
        form = await getattr(f0, f"async_step_{page}")(None)
        same = [s for s in srcs if rig.field_section(form, s) is not False and number_cfg(form, s) is not None]
        if len(same) != 1 or same[0] not in PAIRS:
            print(f"SKIP {page}.{r.key} sources={srcs} same-page-numeric={same}")
            continue
        src = same[0]
        a, b = PAIRS[src]
        measured += 1
        shown, err, val, opts = await walk(page, r.key, src, a, b)
        ok = (val == a) and not err
        lost += 0 if ok else 1
        _, err0, val0, _ = await walk(page, r.key, src, a, a)
        null_lost += 0 if val0 == a else 1
        print(f"ROW {page}.{r.key} source={src} stored {src}={a} submit {src}={b} keeping shown={shown} -> "
              f"effective={val} {'KEPT' if ok else 'LOST'} errors={err} stored_options={opts}")
    print(f"RESULT computed_rows={len(rows)}")
    print(f"RESULT computed_same_page_numeric={measured}")
    print(f"RESULT computed_kept_value_lost={lost}")
    print(f"RESULT null_kept_value_lost={null_lost}")
    print(f"RESULT thread_factor={rig.thread_factor()}")
    print(f"RESULT load1={rig.load1()}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    asyncio.run(main())
