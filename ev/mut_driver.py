import sys,subprocess,shutil
F="tools/audit/seat/review_packet.py"; O="/tmp/tmp.TYckK0SDxC/orig.py"
src=open(O).read()
M={
 "M1-1based": ("idx = range(carries) if","idx = range(1, carries + 1) if"),
 "M2-live-only": ("return prompt_carries(prompt) or live","return live"),
 "M3-round-scope-dropped": ("if t == round_topic:","if True:"),
 "M4-no-tip-ancestry": ("if is_ancestor(sha, head) and is_ancestor(sha, tip):","if is_ancestor(sha, head):"),
 "M5-no-head-ancestry": ("if is_ancestor(sha, head) and is_ancestor(sha, tip):","if is_ancestor(sha, tip):"),
 "M6-wait-green-dropped": ("if n in REQUIRED and word in (\"WAIT\", \"GREEN\"):","if False:"),
 "M7-required-dropped": ("if n in REQUIRED and word in (\"WAIT\", \"GREEN\"):","if word in (\"WAIT\", \"GREEN\"):"),
 "M8-wait-only": ("and word in (\"WAIT\", \"GREEN\"):\n            continue","and word in (\"WAIT\",):\n            continue"),
 "M9-prompt-anchor": ("r\"^Carry (\\d+):\", prompt or \"\", re.M)","r\"Carry (\\d+)\", prompt or \"\", re.M)"),
 "M10-dispatch-prompt-none": ("ref = f\"refs/heads/dispatch/fixer-{topic}\"","return None"),
 "M11-gather-snapadv-dropped": ("+ ([snap_adv] if snap_adv else [])","+ []"),
 "M12-gather-round-none": ("body, rr.removeprefix(\"origin/handoff/\") if rr else None,","body, None,"),
 "M13-carries-live-in-handoff": ("carries = handoff_carries(dispatch_prompt(a.topic), live)","carries = live"),
 "NULL-docstring": ("A count, not a\n    judgement","A tally, not a\n    judgement"),
}
for k,(a,b) in M.items():
    if src.count(a)!=1: print(k,"PATTERN-COUNT",src.count(a)); continue
    open(F,"w").write(src.replace(a,b))
    r=subprocess.run([sys.executable,F,"--self-test"],capture_output=True,text=True)
    fails=[l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    print(f"{k}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} ({len(fails)} failing) {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]}")
shutil.copy(O,F)
