import json, re
cards = json.load(open('/mnt/project-files/audit-r9/fix/CARDS.json'))['cards']
by = {v[0]: (k, v[1]) for k, v in cards.items()}
assert len(by) == 35 and all(v[1] for v in by.values())
old = open('fixplan-wt/handoff/round9/TVOFI-ASKS.md').read()
asks_part = old[old.index('## (a)'):old.index('## Orchestrator')].rstrip()
# recommendation, and where each answer is applied
R = {
 'A1':('Approve','F11.5 (fixer.md step 8)'), 'A2':('F11.5','F11.5 carries A1'), 'A3':('Approve','F11.5 (fixer.md step 15)'),
 'A4':('Approve','F11.5 (D1.md step 2)'), 'A5':('Approve','F11.5 (fixer.md, #775)'), 'A6':('Approve','F11.5 (root-cause.md section 2)'),
 'A7':('Approve','F11.5 (fixer.md step 8)'), 'A8':('Approve','F11.5 (tests/README.md)'),
 'A9':('Skip','F11.5 (defect-root-cause.md), clause aligned to C10\'s derived set'),
 'B1':('Allow','F10.2'), 'B2':('Allow','F10.2, rows only for the cheaper members C9 picks'), 'B3':('Allow','F11.3'),
 'B4':('Allow','F11.5'), 'B5':('Allow','F10.4'),
 'C1':('Per seam (yes)','new F9.3: P1 declared-domain barrier, strongest model, after F1.6; covers D1-s3-06, D1-s4-01, D1-s5-02, D1-s4-03; F3.2, F3.3 and F1.6 briefs carry it'),
 'C2':('Per pair','F1.10 (P3 arm b), unchanged'), 'C3':('Per PR','F1.11 (P6 arm S in the per-PR gate)'),
 'C4':('Accept (per case)','F8.3 (D6-s1-81 per-instance contract); F1.7 unchanged'),
 'C5':('Not now','new F10.5: nightly kill-ledger writer, tvofi-gated; the writer App and credential are a Mac/tvofi action'),
 'C6':('No','new F10.6: comparison-bound operator, cost measured before it is enabled'),
 'C7':('Not now','F10.3 records the multi-line residual'), 'C8':('Subset','F10.2'),
 'C9':('Sample','F10.2 samples cheaper valve-axis members and records the residual blind spot'),
 'C10':('Accept (registration)','F11.3 derives the check set from CHECKS, codeowners_gap.py and stamp rule 4'),
 'C11':('Accept','F11.4 records the residual as accepted'), 'C12':('Option 3 (extend)','F10.4 (I5 arms)'),
 'C13':('Outage','F1.9 (FI-sw3 treated as an outage)'), 'C14':('Fold in','F11.4 carries the driver fixes'),
 'C15':('Keep','D8-s2-01 refused against A3(e); F7.3 dropped; #1689 closed as not planned'),
 'C16':('Change','D11-s1-01 refused by tvofi, recorded in #1648; F11.2 drops the decision-0008 edit; no policy edit'),
 'C17':('Refusal','F11.2 (budget_raise_gate.py)'),
 'C18':('No','new F11.6: diff-equivalence verdict carry (D13-s1-02), split from F11.3'),
 'D1':('Keep','F6.3, unchanged'), 'D2':('Keep F6.1b','F6.1b merged into F6.1, over the five-item cap by recorded exception'),
 'D3':('Keep (ungated)','F1.10, F1.11 ungated, unchanged'),
}
DIFFERS = {'A9','C1','C5','C6','C9','C10','C16','C18','D2'}  # answer differs from the recommendation
def norm(x): return re.sub(r'[^a-z0-9]', '', x.lower().split('(')[0])
order = [f'A{i}' for i in range(1,10)] + [f'B{i}' for i in range(1,6)] + [f'C{i}' for i in range(1,19)] + ['D1','D2','D3']
rows = []
over = []
for k in order:
    cid, ans = by[k]; rec, where = R[k]
    differs = k in DIFFERS
    if differs: over.append(k)
    rows.append(f"| {k} | {ans} | {rec} | {'**yes**' if differs else 'no'} | {where} | `{cid}` |")
out = f"""# Round 9: tvofi's decisions on the fix-plan asks (2026-09-26)

## DECISIONS

tvofi answered all 35 asks on decision cards at 19:16Z (message
`cmsg_01EL5jLi4rokGBbkaevYXSJV6CQVMDN96YfVMTcN5QGSx2`: "answer all cards, then file the issues and start
fixing"; the superseded card `cmsg_01EL5jLi4rokGBbkaevYXSJVJ2dpNicWumFP91ncYqNNqz` is ignored). Each row is
the card's answer as recorded in `CARDS.json`, the orchestrator's recommendation it answered, and where
the plan applies it (`FIX-PLAN.md` section 13; the roster and lane briefs carry each into its PR).
Where the answer differs from the recommendation, it is applied as given: {', '.join(over)}.

| item | tvofi's answer | recommended | differs | applied in | card |
|---|---|---|---|---|---|
{chr(10).join(rows)}

Counts: (a) 9, (b) 5, (c) 18, (d) 3; 35 answered, 0 open; {len(over)} differ from the recommendation.

**Correction to the ask as put.** C15's parenthetical read "climate stays available without an indoor
thermometer". A3(e) is the opposite: the `tests/entities.py` A3(e) pin keeps the climate entity
unavailable with no thermometer, which is what D8-s2-01 reports. "Keep" keeps the tree's behaviour and
refuses D8-s2-01; nothing in the tree changes.

**What the answers leave to a person.** F10.5's writer identity (decision 0011) needs its App created,
installed and its credential stored: a Mac/tvofi action, not a fixer's. Every allowed budget raise
(B1-B5) and every approved policy draft (A1-A9) still merges only on tvofi's approving review at the PR's
head (budget-raise-gate, decision 0013; code ownership).

## The asks as put (2026-09-26, before the answers)

The drafts are in each RCA write-up (`/mnt/project-files/audit-r9/rca/<slug>/RCA.md`, also on
`handoff/r9-rca-<slug>`).

{asks_part}
"""
open('fixplan-wt/handoff/round9/TVOFI-ASKS.md','w').write(out)
print(over)
