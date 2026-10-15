import subprocess,sys,pathlib
F=pathlib.Path("tools/pr/merge_main_bot.py"); orig=F.read_text()
M={
"M1-del-unread":('    if pins is None:\n        return "skip-pins-unread"\n',''),
"M2-del-running":('    if pins:\n        return "skip-pins-running " + ",".join(pins)\n',''),
"M3-no-second-decide":('        status = decide(**facts, pins=pins())','        pass'),
"M4-except-failopen":('    except (RuntimeError, KeyError, TypeError, ValueError):\n        return None','    except (RuntimeError, KeyError, TypeError, ValueError):\n        return []'),
"M5-read-completed-runs":('            if run_.get("status") == "completed":\n                continue\n',''),
"M6-count-completed-jobs":('\n                    and j.get("status") != "completed"]',']'),
"M7-regex-no-autofix":('|mutation-autofix)$")',')$")'),
"M8-regex-no-bare-mutation":('(?:mutation|mutation-pin-plan','(?:mutation-pin-plan'),
"M9-regex-no-pin-plan":('|mutation-pin-plan|','|'),
"M10-regex-unanchored-end":('|mutation-autofix)$")','|mutation-autofix)")'),
"M11-run-unwired":('            status, tree, head = plan_pr(repo_slug, p, main, repo)','            status, tree = plan_one(repo, p["head"]["sha"], main, mergeable=False, same_repo=True, pins=lambda: []); head = p["head"]["sha"]'),
"M11b-planpr-unwired":(',\n                            pins=lambda: pins_running(repo_slug, head, api=api))',')'),
"M11c-planpr-default-api":('pins=lambda: pins_running(repo_slug, head, api=api))','pins=lambda: pins_running(repo_slug, head))'),
"M11d-default-failopen":('             pins=lambda: None) -> tuple','             pins=lambda: []) -> tuple'),
"M18-no-pagination":('            if len(chunk) < 100:\n                break','            break'),
"M19-pagination-overflow-failopen":('            return None  # more than ten pages','            pass  # more than ten pages'),
"M12-pins-first":('    if not same_repo:\n        return "skip-fork"\n','    if not same_repo:\n        return "skip-fork"\n    if pins is None:\n        return "skip-pins-unread"\n    if pins:\n        return "skip-pins-running " + ",".join(pins)\n'),
"M13-regex-no-matrix-suffix":('mutation-pins(?: \\(.*\\))?','mutation-pins'),
"M14-headsha-dropped":('runs?head_sha={head}&per_page=100&page={page}','runs?per_page=100&page={page}'),
"M15-skip-queued-runs":('if run_.get("status") == "completed":','if run_.get("status") in ("completed", "queued"):'),
"M16-catch-typeerror-dropped":('except (RuntimeError, KeyError, TypeError, ValueError):','except (RuntimeError, KeyError):'),
"M17-read-pins-always":('    status = decide(**facts)\n    if status == "merge":\n        status = decide(**facts, pins=pins())','    p = pins()\n    status = decide(**facts)\n    if status == "merge":\n        status = decide(**facts, pins=p)'),
}
for k,(a,b) in M.items():
    if orig.count(a)!=1: print(f"RESULT mutant {k} NOT-APPLIED count={orig.count(a)}"); continue
    F.write_text(orig.replace(a,b,1))
    r=subprocess.run([sys.executable,str(F),"--self-test"],capture_output=True,text=True)
    fails=[l.strip() for l in r.stdout.splitlines() if l.startswith("  FAIL")]
    print(f"RESULT mutant {k} {'KILLED' if r.returncode!=0 else 'SURVIVED'} rc={r.returncode} fails={len(fails)}", ("| "+fails[0][:110]) if fails else (r.stderr.strip().splitlines()[-1][:110] if r.returncode and r.stderr.strip() else ""))
F.write_text(orig)
