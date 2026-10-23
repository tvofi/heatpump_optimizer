# The contract workflow is the ONE file that DEFINES the `pr-contract` job
# (policy_lint.mjs, #1514). A reusable-workflow CALLER of that job -- a job
# `pr-contract:` whose body is `uses: ./.github/workflows/pr-contract.yml` --
# defines nothing: it runs the definer. The umbrella (R10-CI-LAYOUT-P2, #2495)
# adds such a caller to ci.yml, and a text match on `\n  pr-contract:\n` read
# it as a second definition (FIXTURE VACUOUS, 2 files). `policy-docs` grades
# with the BASE's policy_lint.mjs, so the reader must learn this on main before
# the caller lands. Plants: a caller, a caller carrying `with:`, a tree holding
# a definer and a caller. Nulls: the real job, including one whose STEPS use
# actions (a step `uses:` is not a call) and one followed by another job's call
# (the body ends at the next job); two real definers are still two (the
# "exactly one" refusal stands); and the tree itself names exactly one definer.
_PCJ_DEFINER = ("on: pull_request\njobs:\n  pr-contract:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - uses: actions/checkout@v4\n      - run: node x.mjs\n"
                "  later:\n    uses: ./.github/workflows/other.yml\n")
_PCJ_CALLER = ("on: push\njobs:\n  pr-contract:\n    needs: [prelude]\n"
               "    uses: ./.github/workflows/pr-contract.yml\n  gate:\n    runs-on: x\n")
_PCJ_CALLER_WITH = ("jobs:\n  pr-contract:\n    if: ${{ !cancelled() }}\n"
                    "    uses: ./.github/workflows/pr-contract.yml\n"
                    "    with: { pr: '1' }\n")
_PCJ_OTHER = "jobs:\n  tests:\n    runs-on: x\n    steps:\n      - run: true\n"
import shutil as _pcj_shutil  # noqa: E402
_PCJ_ROOTS = {}
for _k, _files in {"one": {"a.yml": _PCJ_DEFINER, "ci.yml": _PCJ_CALLER},
                   "two": {"a.yml": _PCJ_DEFINER, "b.yml": _PCJ_DEFINER}}.items():
    _d = Path(tempfile.mkdtemp())
    (_d / ".github" / "workflows").mkdir(parents=True)
    for _n, _t in _files.items():
        (_d / ".github" / "workflows" / _n).write_text(_t)
    _PCJ_ROOTS[_k] = str(_d)
_PCJ = json.loads(subprocess.run(
    ["node", "--input-type=module", "-e",
     _PL_IMPORT + ".then((m) => { const t = JSON.parse(process.argv[1]); "
     "console.log(JSON.stringify({"
     "definer: m.definesJob(t.definer, 'pr-contract'),"
     "caller: m.definesJob(t.caller, 'pr-contract'),"
     "caller_with: m.definesJob(t.caller_with, 'pr-contract'),"
     "other: m.definesJob(t.other, 'pr-contract'),"
     "tree: m.contractWorkflowFiles(),"
     "plant_one: m.contractWorkflowFiles(t.one),"
     "plant_two: m.contractWorkflowFiles(t.two)"
     "})) })",
     json.dumps({"definer": _PCJ_DEFINER, "caller": _PCJ_CALLER,
                 "caller_with": _PCJ_CALLER_WITH, "other": _PCJ_OTHER,
                 **_PCJ_ROOTS})],
    capture_output=True, text=True).stdout or "{}")
for _d in _PCJ_ROOTS.values():
    _pcj_shutil.rmtree(_d, ignore_errors=True)
R.check(
    "policy_lint: a reusable-workflow caller job `pr-contract` (`uses:`) is not a "
    "definition of the contract job, so ci.yml's caller cannot make the wiring pin vacuous",
    _PCJ.get("caller") is False and _PCJ.get("caller_with") is False
    and _PCJ.get("plant_one") == ["a.yml"],
    f"parsed={_PCJ}; a `uses:` caller was read as the job's definition",
)
R.check(
    "and the real job, steps using actions included, still defines it; another job "
    "does not; the tree has exactly one definer (null controls)",
    _PCJ.get("definer") is True and _PCJ.get("other") is False
    and _PCJ.get("tree") == ["pr-contract.yml"]
    and _PCJ.get("plant_two") == ["a.yml", "b.yml"],
    f"parsed={_PCJ}",
)
