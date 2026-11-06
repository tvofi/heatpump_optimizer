"""Reviewer's own driver: extract the step text with PyYAML (independent of stamp.release_step_script),
run it in real tag trees via git archive, and in planted trees."""
import yaml, subprocess, tempfile, pathlib, json, os, sys
wf = yaml.safe_load(open(".github/workflows/release.yml"))
jobs = wf["jobs"]
for jn, j in jobs.items():
    names = [s.get("name") for s in j.get("steps", [])]
    if "Refuse a tag whose tree does not carry its version" in names:
        steps = j["steps"]; break
names = [s.get("name") for s in steps]
i_tree = names.index("Refuse a tag whose tree does not carry its version")
i_create = names.index("Create the GitHub release")
print("job", jn, "step order: tree", i_tree, "create", i_create, "tree before create:", i_tree < i_create)
print("steps:", names)
tree = steps[i_tree]; print("tree step env/if/continue-on-error:", {k: v for k, v in tree.items() if k not in ("name", "run")})
script = tree["run"]
pub = [s for s in steps if s.get("name") == "Publish the release once its asset is on it"][0]
print("publish step keys:", {k: v for k, v in pub.items() if k not in ("name", "run")})
def run_in(d, tag):
    p = subprocess.run(["bash", "-e", "-c", script], cwd=d, env={**os.environ, "TAG": tag}, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip().replace("\n", " | ")
for tag in ["v7.1.0", "v7.1.1", "v7.1.2", "v7.1.3"]:
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(f"git archive {tag} VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json | tar -x -C {d}", shell=True, check=True)
        print("REAL", tag, *run_in(d, tag))
def planted(tag, version, manifest, notes):
    with tempfile.TemporaryDirectory() as d:
        t = pathlib.Path(d); (t / "VERSION").write_text(version + "\n")
        m = t / "custom_components/heatpump_optimizer"; m.mkdir(parents=True)
        (m / "manifest.json").write_text(json.dumps({"domain": "x", "version": manifest}))
        (t / "RELEASE_NOTES.md").write_text(notes)
        return run_in(d, tag)
print("PLANT ok v7.1.3", *planted("v7.1.3", "7.1.3", "7.1.3", "# R\n\n## v7.1.3\n\nx\n"))
print("PLANT notes lack section", *planted("v7.1.3", "7.1.3", "7.1.3", "# R\n\n## v7.1.1\n\nx\n"))
print("PLANT notes heading with suffix '## v7.1.3 (date)'", *planted("v7.1.3", "7.1.3", "7.1.3", "# R\n\n## v7.1.3 (2026)\n\nx\n"))
print("PLANT manifest differs", *planted("v7.1.3", "7.1.3", "7.1.2", "## v7.1.3\n"))
print("PLANT VERSION differs", *planted("v7.1.3", "7.1.2", "7.1.3", "## v7.1.3\n"))
print("PLANT VERSION missing file")
with tempfile.TemporaryDirectory() as d:
    print("   ", *run_in(d, "v7.1.3"))
# publish step: never succeeding readback, real step text, stub gh and sleep
with tempfile.TemporaryDirectory() as d:
    b = pathlib.Path(d)
    (b / "gh").write_text(f'#!/bin/bash\nif [ "$2" = view ]; then echo $(( $(cat {d}/n 2>/dev/null||echo 0)+1 )) > {d}/n; echo other.zip; exit 0; fi\nif [ "$2" = edit ]; then touch {d}/published; fi\n')
    (b / "sleep").write_text(f'#!/bin/bash\necho "$1" >> {d}/sleeps\n')
    for s in ("gh", "sleep"): (b / s).chmod(0o755)
    p = subprocess.run(["bash", "-e", "-c", pub["run"]], cwd=d, env={**os.environ, "PATH": f"{d}:{os.environ['PATH']}", "TAG": "v7.1.3", "ASSET": "heatpump_optimizer.zip"}, capture_output=True, text=True, timeout=60)
    print("PUBLISH never-readback: exit", p.returncode, "reads", (b/"n").read_text().strip(), "sleeps", (b/"sleeps").read_text().split() if (b/"sleeps").exists() else [], "published", (b/"published").exists(), "|", p.stderr.strip())
