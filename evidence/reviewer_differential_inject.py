# Reviewer's own differential harness for #3401 (not the fixer's): for each world,
# the pre-flight's answer (PreFlight.entry under the train's --mandate) beside the
# REAL path's answer (policy_approve posts into the fake, then policy_gate re-reads,
# as Train.land does). A world where the pre-flight PASSes and the real path parks
# is the defect the brief hunts.
    def real(world: dict, train_mandate):
        base = fake(world)
        def run(argv, cwd=None, stdin=None):
            if argv[:3] == ["gh", "pr", "view"] and "--jq" in argv and ".headRefOid" in argv:
                return 0, world.get("pr_head", H0)
            if argv[:3] == ["gh", "pr", "review"]:
                world.setdefault("posted", []).append(argv)
                body = Path(argv[argv.index("--body-file") + 1]).read_text()
                world["reviews"] = list(world.get("reviews", [])) + [{
                    "user": world.get("gh_user", {"login": _g.OWNER_LOGIN, "id": _g.OWNER_ID, "type": _g.OWNER_TYPE}),
                    "state": "APPROVED", "commit_id": world.get("pr_head", H0),
                    "submitted_at": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "body": body}]
                return 0, ""
            return base(argv, cwd, stdin)
        with tempfile.TemporaryDirectory() as d:
            t = mt.Train("o/r", Path(d), train_mandate, "", (), 1, run=run, sleep=lambda s: None)
            files = world.get("files")
            item = {"pr": 7, "verdict": H0, "branch": "fix/x"}
            try:
                t.policy_approve(7, world.get("pr_head", H0), item, files)
                t.policy_gate(7, world.get("pr_head", H0), files)
                return "PASS", ""
            except mt.Stop as s:
                return "PARK", s.why
    import copy as _copy
    MD = {**POL, "reviews": [], "mandate": mandate(NOW)}
    ORV = lambda sha, st, cite=False, mins=0: dict(owner_review(sha, NOW + datetime.timedelta(minutes=mins), cite=cite, state=st))
    NOT_OWNER = {"login": _g.OWNER_LOGIN, "id": 1, "type": "User"}
    scen = [
        ("N1 no --mandate", dict(MD), None),
        ("N2 revoked mandate", {**MD, "thread": [revoke()]}, str(mt.MID)),
        ("N3 mandate scope code-owned", {**MD, "mandate": mandate(NOW, scope="code-owned")}, str(mt.MID)),
        ("N4 expired mandate", {**MD, "mandate": mandate(NOW, from_min=-120, until_min=-1)}, str(mt.MID)),
        ("N5 owner CHANGES_REQUESTED at head", {**MD, "reviews": [ORV(H0, "CHANGES_REQUESTED", mins=-5)]}, str(mt.MID)),
        ("A1 owner CHANGES_REQUESTED on an older commit", {**MD, "reviews": [ORV(H1, "CHANGES_REQUESTED", mins=-5)]}, str(mt.MID)),
        ("A2 owner CR then owner APPROVED (uncited) on older commit", {**MD, "reviews": [ORV(H1, "CHANGES_REQUESTED", mins=-9), ORV(H1, "APPROVED", mins=-5)]}, str(mt.MID)),
        ("A3 owner APPROVED (uncited) at head", {**MD, "reviews": [ORV(H0, "APPROVED", mins=-5)]}, str(mt.MID)),
        ("A4 stale agent approval at head citing another (absent) mandate", {**MD, "reviews": [dict(ORV(H0, "APPROVED", mins=-5), body="Agent approval (the orchestrator, not tvofi in person) under mandate 4100000999.")]}, str(mt.MID)),
        ("A5 mandate not yet in force", {**MD, "mandate": mandate(NOW, from_min=+30, until_min=90)}, str(mt.MID)),
        ("A6 mandate edited", {**MD, "mandate": {**mandate(NOW), "updated_at": (NOW).strftime("%Y-%m-%dT%H:%M:%SZ")}}, str(mt.MID)),
        ("A7 mandate written by a look-alike account", {**MD, "mandate": {**mandate(NOW), "user": NOT_OWNER}}, str(mt.MID)),
        ("A8 mandate comment absent (404)", {**MD, "mandate": None}, str(mt.MID)),
        ("A9 --mandate label naming two ids", dict(MD), f"mandate {mt.MID} and mandate 4100000999"),
        ("A10 --mandate label naming no id", dict(MD), "the owner said so"),
        ("A11 reviews unreadable", {**MD, "reviews_fail": True}, str(mt.MID)),
        ("A12 a budget file beside the policy", {**MD, "files": POL["files"] + ["tests/structure_budgets.json"]}, str(mt.MID)),
        ("A13 look-alike account CR at head (not the owner)", {**MD, "reviews": [dict(ORV(H0, "CHANGES_REQUESTED", mins=-5), user=NOT_OWNER)]}, str(mt.MID)),
        ("A14 owner DISMISSED (no CR) at head", {**MD, "reviews": [ORV(H0, "DISMISSED", mins=-5)]}, str(mt.MID)),
        ("A15 revocation by look-alike account (not a revocation)", {**MD, "thread": [dict(revoke(), user=NOT_OWNER)]}, str(mt.MID)),
        ("A16 owner CR at head, later a mandated agent approval at head", {**MD, "reviews": [ORV(H0, "CHANGES_REQUESTED", mins=-9), ORV(H0, "APPROVED", cite=True, mins=-5)]}, str(mt.MID)),
        ("P1 positive: live mandate, no review", dict(MD), str(mt.MID)),
        ("P2 positive: mandate programme-end window", {**MD, "mandate": mandate(NOW, until_min=None)}, str(mt.MID)),
    ]
    slip = 0
    for name, w, tm in scen:
        if w.get("mandate") is None and "mandate" in w:
            w = {k: v for k, v in w.items() if k != "mandate"}
        pf = go(_copy.deepcopy(w), train_mandate=tm)
        rw = _copy.deepcopy(w)
        rl = real(rw, tm)
        bad = pf[0] == "PASS" and rl[0] != "PASS"
        slip += bad
        print(f"  SCEN {name}: preflight={pf[0]}({pf[1]}) real={rl[0]} posted={len(rw.get('posted', []))}"
              f"{'  <-- SLIP' if bad else ''}\n      pf-why: {pf[2][:230]}\n      real-why: {rl[1][:230]}")
    check(f"REVIEWER: no world where the pre-flight PASSes and the real path parks ({slip} slips)", slip == 0)
