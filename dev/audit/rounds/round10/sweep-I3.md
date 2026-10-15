# Round 10 class sweep: I3

I3 is the class where a required governance or CI check is skipped, runs on a stale ref, or has a boundary that can be bypassed (`dev/audit/config/bugclasses.json`, status `barriered`, barrier `field_coverage.mjs`). This sweep covers D14 method steps 3 and 4 for the two round-10 findings in the class, at base `9355f107d` (handoff/audit-r10-register).

## The two findings

- D11-s1-01 (verified, low): the pre-edit hook checks only top-level text fields, so a MultiEdit can write a new `## ` heading into RELEASE_NOTES.md off main and the hook exits 0.
- D13-s1-01 (weakened, hygiene): in the window, 23 of 197 merges carry no review verdict the parser can read, and `policy_lint.mjs --stats` cannot split those merges by class.

## Arm A: hook refusal against each tool shape the matcher admits

**Detector:** `python3 dev/audit/rounds/round10/D14/I3/hook_shape_seams.py`. It derives the seams rather than listing them by hand:

- The tool set comes from the PreToolUse matchers in `.claude/settings.json`.
- The refusal targets come from the hook's own program block: the STAMPED tuple, the RELEASE_NOTES.md branch, and the `.cursor/rules/` prefix.
- The field each tool writes its text to comes from that tool's `tool_input` shape: `new_string`, `content`, `edits[*].new_string` or `new_source`.

It runs the hook's real `decide` program on each pair, using a branch other than main.

| control | command | result |
|---|---|---|
| baseline | (none) | seams=16, escapes=1 |
| positive | baseline | re-finds D11-s1-01: `RELEASE_NOTES.md MultiEdit ESCAPE` |
| null (clean fixture: `edits[*].new_string` flattened) | `--clean` | escapes=0 |
| perturbation (one line: drop `"new_string"` from the inspected tuple) | `--perturb` | escapes=2 (Edit escapes as well) |

How each seam is dispositioned:

| seam | disposition |
|---|---|
| RELEASE_NOTES.md x MultiEdit | **instance**, the judged site of D11-s1-01. Probe: the ESCAPE line above. |
| RELEASE_NOTES.md x Edit, Write | guarded: `new_string` and `content` are read. |
| VERSION, manifest.json, `.cursor/rules/**` x Edit, Write, MultiEdit | guarded: these are refused on the path alone, and every admitted shape carries `file_path`. |
| any target x NotebookEdit (4 seams) | not applicable: NotebookEdit addresses `.ipynb` only, and no target is a notebook. |
| matcher gap: Bash (it can write any of the targets, and the matcher does not admit it) | guarded downstream: the hook fails open by design (see its header). `tools/release/stamp.py` refuses a branch that moved VERSION, the manifest or a RELEASE_NOTES heading, and `rules_sync.mjs --check` in policy-docs refuses a hand-edited `.cursor/rules` file. |

## Arm B: merge verdict coverage

**Detector:** `GITHUB_TOKEN=$(gh auth token) node dev/audit/rounds/round10/D13/s1/yield.mjs --since 1913f0dd7`. This is the finding's own seam_rule, and the seam is a single site.

- **Positive control:** the detector reports window=197 and prod_coverage_full=174, so 23 merges carry no verdict. This re-finds D13-s1-01.
- **Perturbation:** `--reshape-one` moves the count by one; this is recorded in D13/s1/REPORT.md.
- **Null control:** inherited from that harness.

One defect in the harness itself: at this base, `yield.mjs` throws `TypeError` in `verdictsOf` after printing the window and prod lines, before the per-class COVER lines. The count above comes from `prod_coverage_full`. This is a defect in the instrument, not a new seam, and it goes to D13's brief.

| seam | disposition |
|---|---|
| `policy_lint.mjs:statsHistogram`/`statsCoverageLine`, which reads merges with no verdict and has no per-class split | **instance**, the judged site of D13-s1-01 |

## Result

- instances counted beyond the findings: **0**. Both instances are judged sites.
- `barriered`: false. The class barrier, `field_coverage.mjs`, does not register the pre-edit hook's per-tool payload shapes or verdict coverage. A proposed barrier is to run `hook_shape_seams.py` as a case in `pre-edit.sh --self-test`, which policy_lint `--hooks` already drives. That costs under 2 s of gate time.
