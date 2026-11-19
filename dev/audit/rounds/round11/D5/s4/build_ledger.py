#!/usr/bin/env python3
"""Build D5-s4's M4 ledger (text_ledger.py's TSV) from the executed checks of this directory.

Every D5 unit of the seat's cells gets one row. A unit is `no-claim` when it carries no proposition
(a rule line, a section banner of <=4 words, a lint pragma). Every other unit is a `claim` row whose
command is the executed check that judged it:
  semantic.py / py_numbers.py / card_numbers.py -- behaviour or cited number driven: verdict true
      (or false where that harness fails);
  comments.py --file F -- the mechanical checks (C2 names resolve against code, C7 numbers against
      the constant, C5 length): a unit whose cited name resolves nowhere in code is `false`;
      otherwise the behavioural claim was not driven this round: `unverifiable`, truth says so.
Run:  PYTHONPATH=tests/hastub /root/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s4/build_ledger.py OUT.tsv
then: python3 tools/audit/text_ledger.py check --dim D5 OUT.tsv --plant --seat D5-s4 --repo R --ref 92d38ecb...
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B11. Counts only.
"""
import os, re, sys
sys.path.insert(0, "tools/audit"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_ledger as TL  # noqa: E402
import comments as CM  # noqa: E402

H = "dev/audit/rounds/round11/D5/s4/"
PY = "PYTHONPATH=tests/hastub python3 "
CC = "custom_components/heatpump_optimizer/"
# (file, phrase in the unit, harness, what it drove)
DRIVEN = [
    ("log_latch.py", "A transition latch for a persisting", "semantic.py", "WARNING/DEBUG/INFO transitions"),
    ("log_latch.py", "Whether condition ``key`` holds", "semantic.py", "transitions, None owner, exc_info ERROR, returns active"),
    ("log_latch.py", "Drop every condition held", "semantic.py", "forget_held warns afresh"),
    ("log_latch.py", "No stable owner means no transition", "semantic.py", "None owner logs every call"),
    ("plan_step.py", "``now`` floored onto the plan's step grid", "semantic.py", "floor, fold, tzinfo"),
    ("plan_step.py", "One plan step in hours", "semantic.py", "PLAN_STEP_HOURS*60 == PLAN_STEP_MINUTES"),
    ("silent_mode.py", "Per-step electrical ceiling in kW", "semantic.py", "None at 1.0/no window, floored"),
    ("silent_mode.py", "``caps_extra`` tightened by", "semantic.py", "same object when nothing caps"),
    ("pump_schedule.py", "Whether the hot-water circulation loop", "semantic.py", "no windows -> run; lead"),
    ("pump_schedule.py", "Whether the space circulation pump must run", "semantic.py", "freezing rail"),
    ("pump_schedule.py", "no plan yet", "semantic.py", "empty plan -> (True, True)"),
    ("pump_schedule.py", "(heat now, heat next step)", "semantic.py", "empty plan -> (True, True)"),
    ("plan_slots.py", "Collapse a per-step power schedule", "semantic.py", "zero-overlap slot has no shared_kwh"),
    ("modbus_prefill.py", "Day bitmaps put Monday on bit 7", "py_numbers.py", "_DAY_BITS"),
    ("open_meteo.py", "Physical ceiling used to reject nonsense", "py_numbers.py", "1361 + 39"),
    ("optimizer.py", "Strength of the pull towards the comfort", "py_numbers.py", "two-zone = half"),
    ("pump_arbiter.py", "two 0.1 K entity steps", "py_numbers.py", "FEEDBACK_STOP_MARGIN_K"),
    ("pump_arbiter.py", "Past the fork's 8 s sent-value window", "py_numbers.py", "ECHO_GRACE_S > 9"),
    ("quick_setup.py", "The volume \"buffer tank: yes\" writes", "py_numbers.py", "BUFFER_STORE_MIN_VOLUME 100"),
    ("slab_seed.py", "The warmest a floor-loop return may read", "py_numbers.py", "9 K + 3 K"),
    ("store.py", "No writer stores a number this large", "py_numbers.py", "ABSURD > epoch ms"),
    ("sysid.py", "The 95 % critical value for a one-degree", "py_numbers.py", "chi2.ppf(0.95,1)"),
    ("sysid.py", "The 95 % two-sided normal quantile", "py_numbers.py", "norm.ppf(0.975)"),
    ("tariff.py", "Metering window in minutes", "py_numbers.py", "window_minutes default 60"),
    ("www/heatpump-optimizer-card.js", "What `ha-card` takes off the host", "card_numbers.mjs", "2*(1+12)"),
    ("www/heatpump-optimizer-card.js", "The Configure button every card ends with", "card_numbers.mjs", "164 at 11 in 152"),
    ("www/heatpump-optimizer-card.js", "The type disc on a card's outer top corner", "card_numbers.mjs", "18 across"),
    ("www/heatpump-optimizer-card.js", "The cap exists so a pathological 60 px", "card_numbers.mjs", "28*257/900"),
    ("www/heatpump-optimizer-card.js", "fixed 900x380 coordinate system", "card_numbers.mjs", "VIEW_W x VIEW_H"),
    ("www/heatpump-optimizer-card.js", "How far back the plan chart may be panned", "card_numbers.mjs", "48 h / 12 h"),
    ("www/heatpump-optimizer-card.js", "The integration's own staleness rule", "card_numbers.mjs", "3 intervals / 90 min"),
    ("www/heatpump-optimizer-card.js", "The savings table's in-cell magnitude bar", "card_numbers.mjs", "0.16 in window"),
    ("www/heatpump-optimizer-card.js", "The card's corner radius, in viewBox units", "card_numbers.mjs", "--hpo-radius-m 12px"),
]
# Units whose cited code name resolves nowhere (comments.py C2, triaged by hand: the rest were
# notation, DOM APIs, ranges, f-string-composed keys or paths that resolve).
FALSE = {
    ("sysid.py", "prior_rel = prior_w / data_w"):
        "prior_w and data_w exist nowhere in code; the line below computes prior_rel = s_noise / prior_sd",
    ("sysid.py", "``T_prev`` sits on BOTH sides"):
        "no T_prev exists in code; the regression's previous sample is usable[i - 1].room_temp",
}
NOCLAIM = re.compile(r"^[\s#/*:=\-]*(?:noqa|type: ignore|pragma|eslint|istanbul|pylint|fmt:|isort)\b|^[\s#/*:=\-]*$", re.I)


def main(out):
    files = TL.seat_files(CM.SEAT, "/home/user/heatpump_optimizer", CM.BASE)
    CM.ARGS = type("A", (), {"repo": "/home/user/heatpump_optimizer", "ref": CM.BASE})()
    mech = {r["unit"]: r for r in CM.check_units(".", files, [])}
    rows, used = [TL.HEADER], set()
    for f in files:
        for uid, line, kind, text in TL.units_of(f, TL.read(".", f), "D5"):
            body = " ".join(CM.clean(text, kind).split())
            words = re.findall(r"[^\W\d_]{2,}", body)
            rel = f[len(CC):]
            if NOCLAIM.match(body) or len(words) <= 4 and not re.search(r"[.:;]\s|[=<>]", body):
                rows.append([uid, str(line), "no-claim", "", "", "-", ""]); continue
            hit = next((d for d in DRIVEN if d[0] == rel and d[1] in text), None)
            fl = next((v for (ff, p), v in FALSE.items() if ff == rel and p in text), None)
            m = mech[uid]
            res = (f"unresolved={','.join(m['unresolved']) or '-'};long={','.join(map(str, m['long'])) or '-'};"
                   f"num={'mismatch' if m['num'] else '-'}")
            if fl:
                used.add(fl)
                rows.append([uid, str(line), "claim", PY + H + f"comments.py --file {f}", res, "false", fl])
            elif hit:
                used.add(hit)
                cmd = (f"node {H}{hit[2]}" if hit[2].endswith(".mjs") else PY + H + hit[2])
                rows.append([uid, str(line), "claim", cmd, f"ok: {hit[3]}", "true", ""])
            else:
                rows.append([uid, str(line), "claim", PY + H + f"comments.py --file {f}", res, "unverifiable",
                             "mechanical checks only (names resolve, cited numbers agree); behaviour not driven this round"])
    missing = [d for d in DRIVEN if d not in used] + [v for v in FALSE.values() if v not in used]
    with open(out, "w") as fh:
        fh.write("\n".join("\t".join(c.replace("\t", " ").replace("\n", " ") for c in r) for r in rows) + "\n")
    print(f"RESULT rows={len(rows) - 1} count")
    print(f"RESULT driven_true={sum(r[5] == 'true' for r in rows[1:])} count")
    print(f"RESULT false={sum(r[5] == 'false' for r in rows[1:])} count")
    print(f"RESULT unmatched_mappings={len(missing)} count")
    for d in missing:
        print("   unmatched", d)


if __name__ == "__main__":
    main(sys.argv[1])
