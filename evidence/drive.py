"""Reviewer's own drive (not the fixer's): head vs mutant over the selftest's fakes."""
import sys, json, tempfile, pathlib, copy
root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root/"tools/audit/seat"))
import outside_intake_selftest as s
src = (root/"tools/audit/seat/outside_intake.py").read_text()
MUT = {"head": None,
 "one_thread_pr_reviews_drop": ('        if r["kind"] == "pr":\n            cs +=', '        if False:\n            cs +='),
 "scan_disc_kind": ('        if t.n in disc:\n            t.kind = "discussion"', '        if False:\n            t.kind = "discussion"'),
 "owed_reply_ge": ('"reply" if t.last_out > max(disposed, t.last_ours) else None', '"reply" if t.last_out >= max(disposed, t.last_ours) else None'),
}
w0 = s.world(s.load(root/"tools/audit/seat/outside_intake.py", "probe"))
print("fixture discussions:", json.dumps(w0["discussions"])[:600])
for name, edit in MUT.items():
    d = tempfile.mkdtemp(); p = pathlib.Path(d)/"tools/audit/seat/outside_intake.py"; p.parent.mkdir(parents=True)
    p.write_text(src if edit is None else src.replace(*edit))
    m = s.load(p, "oi_"+name)
    w = s.world(m)
    # (a) refuse the outside review comment on our PR #3240 (fixture line: owed=triage)
    rc, msg = m.dispose(s.Fake(w), "o/r", 3240, s.roster(), s.LIVE, "not in scope", True, s.Poster())
    # (b) outside comment at the exact second of our answer on #3225
    w2 = s.world(m); ans = s.comment(3225, {"login": "hpo-approver[bot]", "type": "Bot"}, "2026-11-06T22:00:00Z", m.answer_body("R10-COMBI-TANK"))
    w2["comments"] += [ans, s.comment(3225, s.OUT, "2026-11-06T22:00:00Z", "same second")]
    l2 = [l for l in m.listing(s.Fake(w2), "o/r", s.SINCE, s.roster(), s.LIVE(), s.NOW)[0] if "#3225" in l]
    # (c) discussion kinds in the main listing
    l3 = [l for l in m.listing(s.Fake(w), "o/r", s.SINCE, s.roster(), s.LIVE(), s.NOW)[0]]
    print(f"[{name}] refuse#3240 rc={rc} msg={msg!r} | same-second#3225={l2} | listing={l3}")
