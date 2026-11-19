p = 'dev/audit/rounds/round11/D1/s2/staleness.py'
s = open(p).read()
s = s.replace('''"problem": (r.problem if r else None),''', '''"problem": (r.problem if r else None), "max_age": (r.max_age_minutes if r else None),''')
s = s.replace('''    at(25 + 360)''', '''    at(25 + 420)''')
s = s.replace('''# forward 6 h''', '''# forward 7 h''')
s = s.replace('''    elif r["value"] is not None:
        try:
            if abs(float(r["value"]) - float(res["new"])) > 0.05 and res["new"] != res["h"].get("text"):
                kinds.append("stale_after_return")
        except (TypeError, ValueError):
            pass''', '''    elif res["new"] != DOMAIN_OF.get(res["slot"], TEMP)[1] and r["value"] is not None \\
            and r["value"] == res["h"]["value"]:
        kinds.append("stale_after_return")
    s = res["s"]
    if s["ok"] and s["age"] is not None and isinstance(s["max_age"], (int, float)) and s["age"] > s["max_age"]:
        kinds.append("stale_not_flagged")''')
s = s.replace('''"neg_age_after_jump", "cycle_fail", "harness_error"):''', '''"neg_age_after_jump", "stale_not_flagged", "cycle_fail", "harness_error"):''')
s = s.replace('''  neg_age_after_jump   (j) a negative age published''', '''  neg_age_after_jump   (j) a negative age published
  stale_not_flagged    (s) reading ok past its own max_age_minutes''')
open(p, 'w').write(s)
