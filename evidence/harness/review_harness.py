"""Reviewer's own harness for #2060 (not the finder's: the finding has no committed harness).
Scenarios over merge_pin_shards + apply_pins' head gate, using the real artifact 11547045879."""
import importlib.util, json, shutil, sys, tempfile
from pathlib import Path
mod_path, art = sys.argv[1], Path(sys.argv[2])
spec = importlib.util.spec_from_file_location("mt", mod_path); mt = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(Path(mod_path).parent)); spec.loader.exec_module(mt)
HEAD = (art / "head").read_text().strip()
def shard(d, status, pins=None, head=HEAD):
    d.mkdir(parents=True); (d / "status").write_text(status + "\n")
    if pins is not None: (d / "pins.json").write_text(json.dumps(pins))
    if head is not None: (d / "head").write_text(head + "\n")
def run(name, build, apply_head=HEAD):
    td = Path(tempfile.mkdtemp()); root = td / "root"; build(root)
    st = mt.merge_pin_shards(str(root), str(td / "out"))
    pins = sorted(json.loads((td/"out"/"pins.json").read_text())) if (td/"out"/"pins.json").exists() else []
    # apply_pins head gate only (stop before ledger writes): re-implement its first three checks by calling it on a copy is unsafe; read the merged head instead
    mh = (td/"out"/"head").read_text().strip() if (td/"out"/"head").exists() else None
    gate = "n/a" if st != "measured" else ("skip-head-moved" if mh != apply_head else "would-apply")
    print(f"RESULT {name}: merged={st} pins={len(pins)} head_gate={gate}")
    shutil.rmtree(td)
real = json.loads((art / "pins.json").read_text())
run("real-lone-flat(37763212023)", lambda r: shutil.copytree(art, r))
run("real-in-subdir", lambda r: shutil.copytree(art, r / "mutation-pins-1"))
run("lone-flat-stale-head", lambda r: shard(r, "measured", real, head="0"*40))
run("lone-flat-nothing-killed", lambda r: shard(r, "skip-nothing-killed", {}))
run("lone-flat-measure-failed", lambda r: shard(r, "skip-measure-failed", {}))
run("lone-flat-measured-corrupt-pins", lambda r: (shard(r, "measured", None), (r/"pins.json").write_text("{bad")))
run("lone-flat-no-status(crash)", lambda r: (r.mkdir(), (r/"head").write_text(HEAD+"\n")))
run("empty-root", lambda r: r.mkdir())
run("missing-root", lambda r: None)
def n3(r):
    shard(r/"mutation-pins-1", "measured", {"a": {"killed_by": "t"}}); shard(r/"mutation-pins-2", "skip-nothing-killed", {}); shard(r/"mutation-pins-3", "measured", {"c": {"killed_by": "t"}})
run("3-shards", n3)
def n2stale(r):
    shard(r/"mutation-pins-1", "measured", {"a": {"killed_by": "t"}}); shard(r/"mutation-pins-2", "measured", {"c": {"killed_by": "t"}}, head="1"*40)
run("2-shards-mixed-heads", n2stale)
def n3miss(r):
    shard(r/"mutation-pins-1", "measured", {"a": {"killed_by": "t"}}); shard(r/"mutation-pins-3", "skip-measure-failed", {})
run("3-shards-one-missing", n3miss)
