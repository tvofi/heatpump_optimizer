# Proposal triage, session s8, batch 86 (P323)

The rolling batch after batch 85 (handoff `triage-s8-batch85`). Facts were read at origin/main
`851d1ce6b` and on the roster branch.

## P323: a seat ran `pkill -f` with an empty pattern; refuse pattern kills in a PreToolUse Bash hook

Verdict: ACCEPT narrowed, as a new fly-in group **R10-FLY-BASH-KILL-GUARD** (S). It adds a
PreToolUse hook on the `Bash` tool, a new script beside `.claude/hooks/pre-edit.sh`. The hook refuses a pattern kill at
command position and lets a kill by PID through.
- **Refused (exit 2), at command position only** (line start, or after `;`, `&&`, `||`, `|`, `$(`,
  a backtick, `sudo`, `xargs` or `env`):
  - `pkill` with any arguments, not only `-f` or an empty pattern;
  - `killall`;
  - `kill` fed by `pgrep`, as `kill $(pgrep ...)` or `pgrep ... | xargs kill`.
- **Why `pkill` without `-f` is refused too.** `pkill python3` matches every seat's interpreter by
  process name. Narrowing the hook to `-f` would leave the same blast radius open.
- **Allowed:**
  - `kill <pid>`, `kill $!`, `kill $(cat <pidfile>)`;
  - the word in an argument, a quoted string or a heredoc body (`grep -n pkill`,
    `git log --grep=killall`).
- **The refusal message** names the preamble rule (kill only a PID you started) and the
  alternative: capture `$!` or use a pidfile.
- **REJECTED: a firmer sentence in the seat preamble.** The rule is already stated twice (the
  preamble and the memory note), and the second instance broke it anyway. That is process state
  (b), and a third copy of the rule is not a countermeasure.

Source: the orchestrator s8's message of 2026-10-31 (~04:30Z, slip), and its liveness check.

Instances:
- 2026-10-15: the #2216 fixer's `pkill -f "tests/entities.py"` killed every seat's run of that
  script machine-wide. A gate script killed from outside reads as red, which recorded false mutant
  kills in the D3 quiet-window arms.
- 2026-10-31 ~04:30Z: the dispatch seat's `pkill -f` with an empty pattern, while restarting its
  watch loop. An empty `-f` pattern matches every process of the user. Nothing died, as the
  orchestrator checked: tick_loop, state_docs, wt_sync, cloud_relay, the roster loop, the train and
  itself.
- Adjacent class, not counted: the `pgrep`/`pkill` waiter whose `-f` matches its own command line.
  `tools/audit/seat/cloud_dispatch.py` already forbids it in the reviewer prompt.

Cost:
- **Size.** S. One new hook script of about 40-60 lines with its own `--self-test`, modelled on
  `.claude/hooks/pre-edit.sh`, including its payload-as-argument note and its fail-open rule. Plus
  one `PreToolUse` entry with matcher `Bash` in `.claude/settings.json`, and the
  `tools/policy/policy_lint.mjs` change below.
- **Per-call cost, measured on this host.**
  - A bash `case` prefilter costs about 3 ms per call: 20 calls took 0.056 s.
  - A `python3` start costs about 26 ms per call: 20 calls took 0.52 s.
  - So the hook exits 0 on any payload without the substring `kill` before starting python. Nearly
    every Bash call then pays about 3 ms.
- **No API call and no new CI job.** `policy_lint.mjs`'s hooks check already runs every wired hook's
  `--self-test`. Before the fixer starts, it checks the `structure.py` budget rows for
  `policy_lint.mjs` and `.claude/hooks/`.

Binding:
- **The gate cannot see this harm, and it is severe.** The failure kills processes outside the
  seat, not a file in the tree. An empty pattern kills every seat, the live merge train and the
  orchestrator in one call. A partial kill writes false reds into gate and mutation evidence.
- **Two instances in 16 days** under a rule that was stated twice, and the second came after the
  memory note existed.
- **The cost is about 3 ms per Bash call** plus one small hook.
- **The trade is clearly positive.** That makes this a barrier,
  rather than an RCA that records a refusal (`defect-root-cause.md`).

Carry text, which is the new group's brief (`groups/R10-FLY-BASH-KILL-GUARD.json`, citing
`triage: dev/programme/triage/s6-batch86.md#P323`):
"From triage P323 (orchestrator s8, 2026-10-31): a seat ran `pkill -f` with an empty pattern while
restarting its watch loop. The 2026-10-15 instance (#2216's fixer, `pkill -f tests/entities.py`)
killed every seat's run of that script. The seat preamble and the memory note both forbid it, so
the rule is in process state (b).
(1) Add a new hook script beside `.claude/hooks/pre-edit.sh`, the Bash hook. Wire it in
`.claude/settings.json` as a PreToolUse hook with matcher `Bash`. Model it on `pre-edit.sh`: the payload is passed as an argument, the hook fails
open on anything it cannot parse, and it exits 2 only on a positive match.
- First, a bash `case` prefilter exits 0 on any payload without the substring `kill`. Measured:
  about 3 ms per call against about 26 ms for a python start.
- Then it reads `tool_input.command` and refuses at command position (line start, or after `;`,
  `&&`, `||`, `|`, `$(`, a backtick, `sudo`, `xargs` or `env`) each of:
  - `pkill` with any arguments;
  - `killall`;
  - `kill` fed by `pgrep`.
- Heredoc bodies are not read.
- The refusal names the preamble rule and the alternative (`$!` or a pidfile).
(2) Fix `tools/policy/policy_lint.mjs`'s hooks check (`cmdHooks`). It tests every PreToolUse
matcher against its list of edit tools only, so it would report this hook's `Bash` matcher as
`MATCHER BLIND`. Key the tool set on the hook script instead: `pre-edit.sh` keeps the edit tools,
and the Bash hook is tested against `Bash`. Add the Bash hook to its `REQUIRED` list.
(3) Self-test rows:
- Refused:
  - `pkill -f ""`;
  - `pkill -f tests/entities.py`;
  - `pkill python3`;
  - `killall python3`;
  - `kill $(pgrep -f x)`;
  - `pgrep -f x | xargs kill`;
  - `cd /tmp && pkill -f x`;
  - `sudo pkill x`.
- Allowed:
  - `kill 1234`;
  - `kill $!`;
  - `kill $(cat run.pid)`;
  - `grep -n pkill file`;
  - `git log --grep=killall`;
  - `echo "never pkill"`;
  - a heredoc whose body holds `pkill -f x`;
  - `git status`, which takes the prefilter path.
(4) Mutants:
- Drop the command-position anchor, and the `grep -n pkill` row fails.
- Drop the `killall` arm, and its row fails.
- Drop the pgrep-feed arm, and the `xargs kill` row fails.
- Make `policy_lint`'s matcher test edit-only again, and it reports `MATCHER BLIND`.
(5) Classify the new script for `tests/entities.py`.
(6) Ownership and effect. `.claude/hooks/` and `.claude/settings.json` are code-owned (`@tvofi`), so
the PR merges on tvofi's approving review or under mandate 6329234399. A local seat loads hooks
from the checkout it runs in, so the hook protects local seats only once the orchestrator advances
that checkout. Cloud seats get it from their fresh checkout, and a cloud seat's kill reaches only its own
container, so the exposure is the shared local host. The interim, the orchestrator's call: this
host already runs user-level PreToolUse Bash hooks outside the tree (the main-checkout guard), and
the same script installed there protects every local seat at once, before the checkout advances.
Not in scope: the `pkill` mentions in prose in `tools/audit/seat/cloud_dispatch.py` and
`tools/audit/seat/pr_args.sh`, which are rules, not calls."
