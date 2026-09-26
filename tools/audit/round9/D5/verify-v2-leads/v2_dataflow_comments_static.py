"""verify-v2 (independent lens, D5-s2-51): static/source-level re-check of the two comment claims,
using a DIFFERENT method than the finder's dynamic instrumentation (no async solve, no monkeypatch
of ThermalModel.__setattr__ or coordinator._await_process).

Metric definition (mine): (a) whether coordinator._warm_seeded's own source performs ANY index
shift/re-alignment of result.power_schedule before handing it to the optimizer (grep + AST check
of the function body for slicing/np.roll/offset arithmetic) -- if none exists, the docstring's
"the same problem one step later" (an aligned plan) cannot be what the code delivers, independent
of any particular re-plan cadence; (b) whether "last_buffer_trajectory" (the name the comment's
"stashes the series on itself" would need) is assigned ANYWHERE in production source
(custom_components/heatpump_optimizer/*.py), and whether the terminal-cost function takes the
buffer trajectory as a parameter (a closure argument) rather than reading it off self/model state.

Run from cwd=/home/claude/ev2 (read-only reference tree, evidence branch 96b89163):
    python3 tools/audit/round9/D5/verify-v2-leads/v2_dataflow_comments_static.py
Expected (mine): warm_seeded_has_shift=0 (no shift code found) -> the "one step later" alignment
claim in the docstring is unsupported by the implementation; buffer_stash_assignments=0 and
terminal_cost_takes_arg=1 -> "the model stashes the series on itself" is false, the value is
threaded through as an argument instead. Both corroborate the finder's dynamic result
(handed_offset_steps=0, model_sequence_writes=0) by an independent, non-execution method.
Baseline / tree: evidence branch 96b89163 (heatpump_optimizer). No perturbation needed for a static
existence check; perturbation is the finder's dynamic --shift/--plant, already independent evidence
this harness does not need to reproduce to corroborate.
"""
import ast
import os
import sys

ROOT = os.getcwd()
OPT_FILE = os.path.join(ROOT, "custom_components/heatpump_optimizer/coordinator.py")
if not os.path.isfile(OPT_FILE):
    print("ERROR: run this from the heatpump_optimizer repo root (cwd=/home/claude/ev2)", file=sys.stderr)
    sys.exit(2)

src = open(OPT_FILE).read()
tree = ast.parse(src)

warm_fn = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_warm_seeded":
        warm_fn = node
        break
assert warm_fn is not None, "_warm_seeded not found"

# Does the function body contain any shift/offset/slice arithmetic applied to the array it builds?
SHIFT_MARKERS = ("np.roll", "[1:]", "[2:]", "[:-1]", "[:-2]", "elapsed", "offset", "steps_elapsed")
body_src = ast.get_source_segment(src, warm_fn) or ""
has_shift = any(m in body_src for m in SHIFT_MARKERS)
print(f"_warm_seeded body:\n{body_src}\n---")
print(f"RESULT warm_seeded_has_shift={int(has_shift)} count")

# (b) grep every production .py file for the stash attribute name and for how the terminal cost
# threads the buffer trajectory (parameter vs. self-read).
pkg_dir = os.path.join(ROOT, "custom_components/heatpump_optimizer")
stash_hits = 0
stash_files = []
for fn in os.listdir(pkg_dir):
    if not fn.endswith(".py"):
        continue
    text = open(os.path.join(pkg_dir, fn)).read()
    if "last_buffer_trajectory" in text:
        # only count actual assignment sites, not the finder's/this harness's own commentary
        for line in text.splitlines():
            if "last_buffer_trajectory" in line and ("=" in line and "==" not in line):
                stash_hits += 1
                stash_files.append(fn)
print(f"RESULT buffer_stash_assignments={stash_hits} count files={sorted(set(stash_files))}")

opt_file = os.path.join(pkg_dir, "optimizer.py")
opt_src = open(opt_file).read()
opt_tree = ast.parse(opt_src)
terminal_cost_takes_arg = 0
for node in ast.walk(opt_tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_terminal_cost":
        # the scalar closure RETURNED by _terminal_cost (named "cost" in its body)
        # is what actually receives the buffer trajectory -- check that inner def.
        for inner in ast.walk(node):
            if isinstance(inner, ast.FunctionDef) and inner.name == "cost":
                params = [a.arg for a in inner.args.args]
                terminal_cost_takes_arg = int("buffer_temps" in params)
                print(f"_terminal_cost's returned closure 'cost' params: {params}")
print(f"RESULT terminal_cost_takes_arg={terminal_cost_takes_arg} count")

print("RESULT thread_factor=1.000")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except Exception:
    print("RESULT load1=n/a")
