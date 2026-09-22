#!/usr/bin/env python3
"""Derive and apply the scoped gate's dependency closures.

The gate is the throughput bottleneck: a full run is about forty minutes,
and most changes cannot reach most of it. This module lets ``tests/run.sh``
run only the scripts a change can affect -- without anyone ever writing down,
by hand, what a script depends on. Measured on the real suite: a
release-notes change reaches one script, a change to the card's JavaScript
reaches six, a change to the optimizer reaches fourteen of sixteen.

The closures are MEASURED, never declared. ``closure.py record`` runs a test
script for real under two instruments at once:

  * a ``sys.addaudithook`` hook that records every ``open`` the run performs,
    every ``compile``/``exec`` of a file, and every subprocess it spawns; and
  * ``sys.modules`` at the end of the run, filtered to files inside the repo.

The union of those, expressed as repo-relative paths, is the closure. That
catches the things an import graph cannot see -- ``tests/golden/*.json``,
``strings.json``, ``services.yaml``, ``manifest.json``, ``VERSION``, the
translations, ``tests/harness.py``, the plan payload -- because the run
actually opened them. Node scripts (``tests/card.mjs``) are recorded under
``strace`` when it exists, or under ``tests/node_fs_trace.mjs`` (an
``--import`` wrap of ``fs`` and the ESM loader) on Darwin and anywhere
else ``strace`` is missing.

A hand-maintained table would rot on the first refactor and nobody would
notice. This one cannot rot silently either: the post-merge gate on ``main``
re-records every closure while it runs the full suite anyway and fails if the
committed file misses anything a real run touched (``closure.py check``).

Commands
--------
  record <script> --out-dir DIR   run one script instrumented, write its record
  merge  --in-dir DIR             fold records into tests/closures.json
  check  --in-dir DIR [--partial] fail if the committed closures under-approximate
  autofix --in-dir DIR [--partial] [--out PATH]
                                  merge UNDER-SCOPED recordings; print AUTOFIX: <status>
  autofix-report --job J --status S
                                  redden an autofix job that repaired nothing
  prune                           drop committed closure entries whose path
                 [--out PATH]     is no longer a file (#1310)
  select --files ... | --diff REF decide which scripts a change needs
                 [--workdir DIR]  ...and write the plan where run.sh reads it
  affected --files ... | --diff REF | --files-from FILE
                 [--workdir DIR]  decide whether THIS check must run for a change,
                                  and which closures it has to re-derive
  show                            print the committed closures
  selftest                        pin merge() against a silent shrink (#527)

Nothing here imports the integration; recording does, by running the tests.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLOSURES = ROOT / "tests" / "closures.json"

# #934 (D3-INST): this file is the only per-script timing table in the tree,
# and the two differential guards are recorded with deliberately cheap
# arguments (derive_closures.sh: golden.py --only __no_such_scenario__,
# env_drift.py --cache-key <ref> --all) whose wall time is sub-second, while
# the standalone run a developer sizes off this table costs minutes (the
# judge measured golden.py standalone at 160.9 s against a 0.4 s record).
# The seconds are honest for what was run; the disclosure keeps a reader
# from mistaking them for the cost of a real differential run. Both merge
# paths stamp this text so a partial (--single) repair cannot leave a
# pre-#934 comment alive in the committed file.
CLOSURES_COMMENT = (
    "MEASURED, not written by hand. Regenerate with "
    "tests/derive_closures.sh; the post-merge gate on main re-records "
    "these and fails if this file misses anything a real run touched. "
    "recorded.seconds for the two differential guards (tests/golden.py, "
    "tests/env_drift.py) time the deliberately cheap stub invocation "
    "derive_closures.sh records with (golden.py --only "
    "__no_such_scenario__, env_drift.py --cache-key <ref> --all), not a "
    "real differential run: a real one costs minutes, the record says "
    "under a second (#934)."
)

# Scripts that are shared plumbing or are driven by another script, and so are
# never selected on their own. Mirrors the exclusions in tests/run.sh.
# setup_qa_render.mjs is WIRED into the card lane (runs every gate, #101)
# but stays unselectable, the rolling.py pattern: making it selectable
# would need it recorded in the Linux-only derive lanes plus a
# coordinated closures.json update, and its dependencies are the card
# source and the payload -- both already covered by card.mjs's closure,
# which the strace re-recording on main will grow to include dom_stub.mjs
# the next time it runs.
# card_browser.mjs, the real-browser layout lane (issue #96), is excluded
# because it needs Chromium, which no other lane installs: the closures job
# could not record it without growing a browser. It runs in its own job.
# nightly_ha.py (#521) is that shape one step further out: it needs Docker and
# pulls a Home Assistant image, so no gate lane can run it and the closures job
# could not record it without both. Its own nightly job runs it.
NOT_A_TEST = {
    "harness.py", "profiles.py", "closure.py", "gate_lock.py",
    "setup_qa_render.mjs",
    "card_browser.mjs", "nightly_ha.py",
    # The nightly's reporter (#533): its own `nightly-status` job runs it on
    # every pull request, and it needs the GitHub Actions API, which this suite
    # has neither the network nor the token for. Like `nightly_ha.py` above it
    # is NOT_A_TEST and is NOT inert: `tests/entities.py` imports it and drives
    # its four states, so a change to how it classifies selects a script.
    "nightly_status.py",
    # The delivery ledger, which replaced `record_status.py` and its
    # `record-status` job: that check reported main's `record` CONCLUSION, which
    # was `failure` on 28 of main's last 40 commits because it asked whether
    # every merge has a row RIGHT NOW while the protocol promises one SOON, in
    # a batch. Its own `delivery-status` job runs this on every pull request; it
    # walks `<last tag>..origin/main`, which this suite has neither the remote
    # nor a reason to fetch, and its verdict is about the record rather than
    # about this tree. NOT_A_TEST and NOT inert: `tests/entities.py` imports it
    # and drives both sides of its threshold, so a change to how it classifies
    # selects a script.
    "delivery_status.py",
    # The two instruments beside the gate rather than in it (#195). Each has
    # its own CI job, which is never scoped and runs on every pull request
    # regardless of what this gate selects -- the `card_browser.mjs` argument,
    # one directory over. `coverage_ratchet.py` needs a coverage payload from
    # tools/audit/w5-partition/coverage_tree.sh, an instrumented re-run of the
    # whole gate, and `mutation_table.py` re-runs gate scripts against a
    # mutated copy of the tree; run.sh running either would have the suite run
    # itself. NOT_A_TEST and NOT inert: `tests/entities.py` imports both and
    # drives their operators and their kill rule, so a change to how either
    # classifies selects a script instead of selecting nothing.
    "coverage_ratchet.py", "mutation_table.py",
    # The #996 instance counter: the record seat runs it by hand against
    # the issue thread via `gh`, which this suite has neither the network
    # nor the token for, and its verdict is about the record rather than
    # about this tree. NOT_A_TEST and NOT inert: `tests/entities.py`
    # imports it and drives its counting rule, its threshold and its CLI
    # on a fixture thread, so a change to how it counts selects a script.
    "issue996_count.py",
    # The shared DOM stub (#101) and the rig around it, imported by the three
    # Node harnesses (card.mjs, setup_qa_render.mjs, card_drift.mjs): libraries,
    # never run. dom_stub.mjs was missing from this set from v6.1.2 to v6.2.7,
    # and a selectable script with no closure forces a FULL run, so every
    # scoped PR gate in between quietly ran everything.
    "dom_stub.mjs", "card_rig.mjs",
    # Preload for `_record_node` when strace is missing. Not a test.
    "node_fs_trace.mjs",
}
# dst_checks.py is a test, but features.py runs it in a subprocess; it is
# recorded so its closure can be folded into features.py's, never selected.
DRIVEN_BY_OTHERS = {"dst_checks.py": "features.py"}

# Scripts that run only under SLOW=1, and so never run in the `fast` job that
# scoping applies to. Every other path -- push to main, nightly, dispatch --
# forces GATE_SCOPE=full, so their closures could never decide anything
# either. They are excluded from selection rather than recorded because
# recording them is not free: rolling.py alone takes over an hour under the
# audit hook (measured 62 min, against 37 unhooked), which was most of the
# wall clock of a whole re-derivation, spent on an answer nothing reads.
#
# This is a different exclusion from DRIVEN_BY_OTHERS, which means "another
# script runs this one". Nothing runs rolling.py; the gate simply never
# chooses whether to.
#
# Safety: excluding a script from selection cannot cause it to be skipped
# when it would otherwise have run, because scoping never reaches it. If
# scoping is ever extended to the slow job, this set must shrink first --
# hence the assertion in tests/entities.py that every name here is in fact
# SLOW-gated in run.sh.
SLOW_GATED = {"rolling.py"}

# A dependency of a different kind: not "what can change this script's
# answer" but "what has to run first for this script to run at all".
# plan_view.py WRITES the plan payload card.mjs reads, so a scope that picks
# card.mjs and drops plan_view.py leaves the card with no payload -- or, worse
# on a developer's box, with a stale one another run left behind. Selecting
# card.mjs selects its producer too.
PRODUCERS = {
    "tests/card.mjs": ["tests/plan_view.py"],
    # The markup gate renders both sides against the same payload.
    "tests/card_drift.mjs": ["tests/plan_view.py"],
}

# ---------------------------------------------------------------------------
# Paths that no test can read, so a change to them cannot break one. This is
# the only claim in this file that a person makes rather than a run, so it is
# deliberately tiny AND it is checked: `merge` fails if any of these turns up
# inside a recorded closure, because that would mean a test does read it.
#
# Everything else that is not in any closure forces a FULL run. "No test reads
# it" is not something to assume about a file nobody measured.
#
# The list is shorter than it looks like it should be, because the check took
# entries off it:
#
#   README.md, RELEASE_NOTES.md -- tests/entities.py reads both, checking the
#     documented behaviour against the code. They are dependencies.
#   the integration's icon and brand images -- they sit inside
#     custom_components/, so they are inside env_drift.py's rule-widened
#     closure whatever anyone thinks about them, and saying otherwise here is
#     an inconsistency waiting to be believed.
INERT = (
    "LICENSE",
    # The private-advisory pointer (#801). GitHub renders it; no gate script
    # reads it. Same class as LICENSE / DISCLAIMER.md: an unclassified root
    # file forced the FULL suite and failed the orphan check on #819.
    "SECURITY.md",
    "NOTICE",
    "icon.png",
    # docs/ except the handover (HANDOVER_DIR below) and the pages a gate
    # script pins (INERT_EXCEPT below, #937 and #939) -- the same split
    # README.md, RELEASE_NOTES.md and tests/README.md needed before it.
    "docs/",
    # tests/README.md was here until #938: entities.py now reads the
    # manual's per-script size annotations and pins them against the
    # code's own counts, and a file a gate script reads is a dependency,
    # not inert -- the same correction governance.yml (#607 follow-up)
    # and nightly_ha.py (#533) needed before it. It moves to entities.py's
    # recorded closure, so an edit to the manual selects that script
    # instead of skipping.
    ".gitignore",
    # Write-once audit EVIDENCE: reports people run by hand, outside the
    # gate. Nothing under tests/ imports or opens the prose, the .out runs,
    # the .json tables or the .sh/.mjs harnesses nobody wired in, and the
    # `merge` check below proves it every time the closures are re-derived.
    # Narrowed from `tools/` (#372): that wider prefix also covered
    # tools/release/stamp.py, live release-critical code that was exempt
    # only by sharing a directory with the evidence. Narrowing to
    # tools/audit/ makes stamp.py an ordinary tracked file the recorder must
    # classify, so a test that imports it pulls its closure in on its own --
    # no exemption, no hidden call site. The prefix no longer covers the
    # round harness .py corpus itself (#995): harness_headers.py's discovery
    # opens every tools/audit/round*/D*/*.py, so those files are read by
    # the gate and `_is_header_corpus` below takes them out of this claim.
    "tools/audit/",
    # Everything below is here for one reason: a file that is neither in a
    # closure nor on this list forces the WHOLE suite, because an unmeasured
    # file is not a safe skip. That rule is right, and it was quietly costing
    # full runs. Renaming one identifier in setup_qa_render.mjs -- a script
    # people run by hand to eyeball the setup diagram -- ran all sixteen
    # scripts, stress.py included, for a change no test can see.
    #
    # `orphan_files()` below keeps this list honest: it lists every tracked
    # file that is in no closure and on no list, and tests/entities.py fails
    # when that set is not empty. So a new file has to be classified once,
    # deliberately, instead of silently making every gate full.
    ".abacus.donotdelete",
    ".claude/",
    # Cursor project rules (`.cursor/rules/*.mdc`). Agents load them; nothing
    # under tests/ reads them. Same reason `.claude/` is here.
    ".cursor/",
    # Orientation for a session that starts cold. Claude Code loads a root
    # CLAUDE.md automatically, which is the whole reason it cannot live under
    # docs/ with the rest of the prose. Nothing under tests/ reads it -- unlike
    # README.md and RELEASE_NOTES.md above, which entities.py checks against the
    # code and which are therefore dependencies rather than inert.
    "CLAUDE.md",
    # The harness-neutral twin of the entry above: ZCode and Codex auto-load a
    # root AGENTS.md instead of CLAUDE.md. It defers to CLAUDE.md and states no
    # policy of its own, and nothing under tests/ reads it either. It is still
    # measured policy -- POLICY_GLOBS matches it and policy_budgets.json caps
    # it -- only this gate has no dependency on it.
    "AGENTS.md",
    "DISCLAIMER.md",
    # The quality-scale register (#229) sat here from #229 to #951: no gate
    # script read it, so the INERT listing was honest. #951 ended that --
    # tests/entities.py now reads the register to pin its coverage-bearing
    # rows against the tree, and tests/harness_headers.py executes
    # tools/audit/round4/D10/qs_rules.py, which reads it too -- so the file
    # moved to entities.py's recorded closure, and this entry was removed
    # rather than kept beside a read (the #357 contradiction). hassfest
    # still skips it for custom repos; that is about the external checker,
    # not this gate.
    # The pull-request template. GitHub renders it into a new body; no gate
    # script reads it. It is NOT under `.github/workflows/`, so the GATE_FILES
    # prefix above does not cover it, and an unclassified file forces the whole
    # suite -- which is how a template edit would otherwise cost a full run.
    # Its headings ARE checked, by policy_lint's pr-body class against the
    # `pr-contract` job's required set, in the governance workflow rather than
    # in this gate.
    ".github/PULL_REQUEST_TEMPLATE.md",
    # GitHub reads it -- for review requests always, for the code-owner check
    # once decision 0008's rule is live; nothing in this gate opens it.
    ".github/CODEOWNERS",
    # Home Assistant blueprint YAMLs, linked from README.md and
    # docs/automations.md and imported by users through HA's blueprint
    # importer -- shipped, read by users, read by no gate script.
    "blueprints/",
    # Driven by the `browser` CI job, which is never scoped and runs on every
    # pull request regardless. It is a real test; it is simply not one of
    # THIS gate's scripts.
    "tests/card_browser.mjs",
    # The workflows that are not the gate were listed here, individually
    # rather than as a `.github/workflows/` prefix, because that prefix would
    # also swallow `tests.yml` and silently undo the forced-full rule that is
    # this gate's safety argument. Each defines its own jobs, which run on
    # every pull request regardless of what this gate selects -- the same
    # argument as `tests/card_browser.mjs` above, one directory over. None is
    # left: every one is now read by `tests/entities.py`.
    # `.github/workflows/governance.yml` was here, on the claim that nothing
    # in the gate reads it. That stopped being true when `tests/entities.py`
    # began reading it to pin the `record-status` job's wiring and its
    # permission widening -- the same correction `nightly_ha.py` needed one
    # entry down, and for the same reason: unreadable by the gate and unread
    # by the gate are different claims, and only the first was ever true. It
    # is now in `tests/entities.py`'s recorded closure, so an edit to it
    # selects that script instead of skipping. A file cannot be both INERT
    # and inside a recorded closure; `closure.py` refuses that pair, which is
    # what turned this from a judgement into a check.
    # `.github/workflows/release.yml` made the same move for #960 (D11-07):
    # an owner-approved `id-token: write` landed on its release job, and
    # `tests/entities.py` pins that grant the same way it pins the
    # governance ones -- a file a gate script reads is a dependency, not
    # inert, whatever directory it lives in.
    # `hassfest.yml`, `validate.yml` and `codeql.yml` (the last added for
    # ledger finding (e), #201) made the same move for decision 0009 step 3b
    # (#954): `tests/entities.py` counts `secrets.SEAT_AUTHOR_TOKEN` across
    # EVERY workflow file, because the property it pins -- the seat author's
    # token reaches no `pull_request` path -- is violated by a reference in
    # any of them, and each of these three runs on `pull_request`.
    # A manual QA render (writes ../setup-qa/). No gate script reads it.
    "tests/setup_qa_render.mjs",
    # tests/nightly_ha.py was here, on the argument that a lane needing Docker
    # is one "no gate script reads and none ever will". The first half held and
    # still does -- it stays on NOT_A_TEST above, and nothing in this gate runs
    # it. The second half was the mistake (#533): its REPORTING is text, and
    # `tests/entities.py` now reads it, so a stale pin or a check renamed out
    # of it fails on the pull request rather than nowhere. Its two offenders
    # from #525 stayed pinned through the #540 that removed them, every nightly
    # green, precisely because no check could see the file. Unreadable by the
    # gate and unread by the gate are different claims, and only the first was
    # ever true here.
)

# Changing the gate itself, or how the closures are derived, invalidates every
# closure at once: run everything.
GATE_FILES = (
    "tests/run.sh",
    "tests/closure.py",
    "tests/closures.json",
    "tests/requirements-ci.txt",
    # `tests.yml` ALONE, not the whole directory. This file defines the job
    # matrix, the interpreter versions, the installed dependencies and the
    # GATE_SCOPE the gate runs under, so a change to it can alter how every
    # script behaves in a way no recorded closure can capture -- which is what
    # a gate file means. The other workflows cannot: none sets a gate
    # variable and none runs a gate script, and `tests/entities.py` reads
    # every one of them, so an edit to one selects that script through its
    # recorded closure rather than forcing every closure. Under the old
    # directory prefix a documentation-only change to `governance.yml` printed
    # "changes the gate itself, so every closure is suspect" and ran the full
    # suite, `tests/stress.py` included -- about twenty-three minutes to
    # measure a solver that no policy file can reach, on the pull request AND
    # again on the push to main.
    ".github/workflows/tests.yml",
    # How the closures are DERIVED is as load-bearing as the closures: change
    # a lane here and every recording that follows is taken differently.
    "tests/derive_closures.sh",
    "tests/node_fs_trace.mjs",
)


# The one hole in `docs/` (#518). Exactly one handover may exist, and
# `tests/entities.py` reads it to say so -- which makes it a dependency, and a
# file cannot be both read by a test and declared unread. Every OTHER
# `docs/handover*.md` is left unclassified on purpose: it is then in no closure
# and on no list, so `select` refuses to skip anything (MODE: FULL) and
# `orphan_files` reports it. A second handover is therefore refused on the pull
# request that adds it, not on the push to main that follows.
HANDOVER_DIR = "docs/"
HANDOVER_STEM = "handover"


def is_handover(rel: str) -> bool:
    """Anything under `docs/` whose first path segment starts with `handover`.

    Deliberately wider than the one filename: it also catches a dated sibling
    and the `docs/handovers/` directory someone reaches for once the flat name
    is refused, which is the shape the ban would otherwise be one rename from.
    """
    if not rel.startswith(HANDOVER_DIR):
        return False
    first = rel[len(HANDOVER_DIR):].lower().split("/", 1)[0]
    return first.startswith(HANDOVER_STEM)


# tools/audit/ is INERT because it holds write-once evidence nothing in the gate
# reads. preflight.sh is the exception: tests/entities.py executes it, so a
# change to it must select that script. Left inside the prefix it would be
# declared unread while being read -- the INERT-vs-recorded contradiction #357
# exists to refuse, and the same shape that let tests/nightly_ha.py's blocking
# pin go stale in silence (#533).
#
# The same argument reaches `.claude/workflows/`. The stale-policy-corpus pins
# copy `policy_lint.mjs`, everything it imports and the vendored library that
# import graph reaches into a fixture repository, and drive `preflight.sh`
# against them, because POLICY_GLOBS is this repository's one definition of
# "what is policy" and a second copy inside a test is the defect CLAUDE.md
# names. Copying it is reading it: left inside the `.claude/` prefix these
# would be declared unread while tests/entities.py opens them on every run.
#
# This is an exact-match list and the fixture derives its own copy set by
# walking those imports, so the two can disagree: a module added to that graph
# later is copied, read, and then refused here as the #357 contradiction, by
# name. That refusal is the intended degradation -- one line to add, and never
# a file silently declared unread.

# .gitignore left INERT while a gate script reads it is the same contradiction.
# #743 gave tests/card_drift.mjs a `git` call -- claimsAreThisBranchs, the guard
# that stopped it failing branches for another lane's claims -- and every git
# invocation reads .gitignore. CI said so itself: "UNDER-SCOPED: tests/card_drift.mjs
# really reads 1 file(s) the committed closure does not list: .gitignore". It was
# declared unread while being read, so `closures` went red on main and
# closures-autofix could not repair it: merging the recording produces the
# INERT-and-recorded pair #357 exists to refuse, so the bot returns skip-still-fails.
INERT_EXCEPT = (
    "tools/audit/preflight.sh",
    # The round-harness exceptions that used to sit here -- #817's three
    # round-3 files and #951's qs_rules.py -- moved to `_is_header_corpus`
    # below when #995's dynamic discovery made the read set the whole
    # tools/audit/round*/D*/*.py corpus: exact-match entries cannot follow
    # a glob, and 212 of them was the shape of a list nobody would keep
    # honest. Same refusal either way: declaring the prefix unread while
    # the gate opens the files is #357.
    # #937: tests/entities.py reads the configuration reference to pin that
    # it names every shipped options field -- the README's promise about
    # exactly that file. The docs/ prefix stays INERT; the reference moves
    # to entities.py's recorded closure, so an edit to it selects that
    # script instead of skipping.
    "docs/configuration.md",
    # #939: same route for architecture.md -- tests/entities.py pins its own
    # numbers (module counts, the module map, the HA boundary) against the
    # tree, so the document a contributor reads before changing the code is
    # a dependency of a gate script, not inert prose.
    "docs/architecture.md",
    # #941: tests/entities.py drives the real Power Headroom sensor over
    # the fuse x tariff grid and reads the automation examples to pin that
    # they name every state the sensor publishes. Same move as the
    # reference above: the docs/ prefix stays INERT, the file moves to
    # entities.py's recorded closure.
    "docs/automations.md",
    # #1413: tests/doc_claims.py reads the remaining reader docs, the shipped
    # blueprints and the generated model figures to derive the claim set from
    # the documents and the fact set from code, failing closed on a stale-prose
    # contradiction (D5-01/D6-01/D6-03). Same route as the three above: the
    # docs/ and blueprints/ prefixes stay INERT, and each file a gate script
    # opens moves to doc_claims.py's recorded closure, so an edit to it selects
    # that script instead of skipping. A file a gate script reads is a
    # dependency, not inert prose, whatever directory it lives in.
    "docs/dashboard-card.md",
    "docs/ecl110.md",
    "docs/how-it-works.md",
    "docs/setup.md",
    "docs/img/dhw-demand-windows.svg",
    "docs/img/dhw-store-decay.svg",
    "docs/img/marginal-cop.svg",
    "docs/img/make_model_figures.py",
    "blueprints/automation/charge_ev_from_grid_headroom.yaml",
    "blueprints/automation/economy_mode_on_price_peak.yaml",
    "blueprints/automation/notify_on_manual_plan.yaml",
    ".gitignore",
    # #995, the .gitignore story one lane later: the live-header harness check
    # executes tools/audit/round4/D6/claims.py, whose re-run rewrites these two
    # caches beside it (set-iteration order churn), and card_drift.mjs --
    # recorded after it in the same lane -- answers `git diff --name-only HEAD`
    # (threeDotFiles), so git hashes the now stat-dirty pair. strace -f records
    # those opens and CI said so: "UNDER-SCOPED: tests/card_drift.mjs really
    # reads 2 file(s) ... claims.json, claims.md". The claims harness is frozen
    # evidence, so the churn is not suppressed; the pair leaves INERT the way
    # .gitignore did and enters that script's closure. Over-approximate by
    # content (a name in a diff list cannot move card_drift's verdict) and safe:
    # over-scoping costs time, under-scoping skips scripts.
    "tools/audit/round4/D6/claims.json",
    "tools/audit/round4/D6/claims.md",
    ".claude/workflows/policy_lint.mjs",
    ".claude/workflows/brief_lint.mjs",
    ".claude/workflows/counts.mjs",
    ".claude/workflows/render_md.mjs",
    ".claude/workflows/vendor/markdown-it.min.js",
    ".claude/workflows/vendor/markdown-it.LICENSE",
    # #1240 (D13-03): tests/entities.py reads the wave script itself to
    # re-derive VERDICT_CLASSES and pin that the stats histogram's block-class
    # set is the one the wave teaches -- the stale-copy class of check this
    # list exists for, same route as policy_lint.mjs above: the file a gate
    # script opens is a dependency, not inert, whatever prefix it lives under.
    # An edit to the verdict grammar now selects tests/entities.py.
    ".claude/workflows/web-fix-wave.js",
    # #1303 (D13-01): tests/entities.py reads the by-design-red exclusion list
    # and the D13 harness that consumes it, to pin that the harness reads the
    # REGISTERED artifact rather than a copy beside itself (step 11: a check
    # pins the artifact it READS). Both routes are the web-fix-wave.js one --
    # the file a gate script opens is a dependency, not inert prose. The
    # harness path is six parts (round5/D13/seat-a/dora_cfr.py), so the
    # `tools/audit/` prefix still keeps it INERT and `_is_header_corpus`
    # (five parts) does not reach it: one exact line, by name, as before. The
    # `.json` artifact is under the `.claude/` prefix and never matches
    # `_is_header_corpus` at all. An edit to either now selects
    # tests/entities.py instead of skipping it.
    ".claude/workflows/cfr_exclusions.json",
    "tools/audit/round5/D13/seat-a/dora_cfr.py",
    # The 9 fixtures that harness READS, on the same #1303 route. The check
    # drives `dora_cfr.main()` with `git` patched to raise at its first call,
    # and `main()` reads `window_merges.json` and one `checkruns_<sha>.json`
    # per merge head BEFORE that call -- so those 9 opens happen on every
    # entities.py run, and a malformed or missing `window_merges.json` reddens
    # the #1303 check before `load_exclusions` is ever reached. A read is a
    # dependency, so they leave the `tools/audit/` prefix the way dora_cfr.py
    # and cfr_exclusions.json did; they are six parts, so `_is_header_corpus`
    # (five) does not reach them either -- one exact line each, by name. The
    # other three fixtures in that directory (`prs_graphql.json`, read only
    # after `main()`'s first git call, and the two `pulls_*.json`, which
    # nothing in this route opens) stay INERT.
    "tools/audit/round5/D13/seat-a/fixtures/checkruns_1cc89e020f.json",
    "tools/audit/round5/D13/seat-a/fixtures/checkruns_2de1c18233.json",
    "tools/audit/round5/D13/seat-a/fixtures/checkruns_6fae33b1da.json",
    "tools/audit/round5/D13/seat-a/fixtures/checkruns_72cfa89288.json",
    "tools/audit/round5/D13/seat-a/fixtures/checkruns_ac8b1ecfc5.json",
    "tools/audit/round5/D13/seat-a/fixtures/checkruns_dec0b4ea2d.json",
    "tools/audit/round5/D13/seat-a/fixtures/checkruns_e7139a7f38.json",
    "tools/audit/round5/D13/seat-a/fixtures/checkruns_f50dcc90e5.json",
    "tools/audit/round5/D13/seat-a/fixtures/window_merges.json",
)


def _is_header_corpus(rel: str) -> bool:
    """The live-header harness corpus tests/harness_headers.py DISCOVERY opens.

    ``_discover()`` globs ``tools/audit/round*/D*/*.py`` and reads the head of
    every match looking for the ``live-header`` marker, so each of those files
    is a read the recorder sees -- executed or not, marked or not: a change to
    any of them can flip the executed set itself. #817 moved the first three
    out of the ``tools/audit/`` INERT prefix one exact-match line at a time,
    #951 a fourth, and #995's dynamic discovery turned the class into the
    whole corpus (212 files at landing, one more with every harness). The
    claim is the SHAPE of the read set, stated once, mirroring the glob --
    including the ``__init__.py`` guard, which the discovery check applies
    before the read, so such a file stays unopened and inside the prefix.

    Both directions stay checked. A gate read OUTSIDE this shape (a harness
    that starts reading evidence .md/.json, a directory the glob does not
    cover) lands in a closure while still INERT, and `merge`/`check` refuse
    the pair (#357). A file this predicate names that no closure covers
    shows up in `orphan_files()` and forces the FULL suite -- so neither
    widening nor narrowing this rule can rot silently.
    """
    parts = rel.split("/")
    return (
        len(parts) == 5
        and parts[0] == "tools" and parts[1] == "audit"
        and parts[2].startswith("round") and parts[3].startswith("D")
        and parts[4].endswith(".py") and parts[4] != "__init__.py"
    )


def is_inert(rel: str) -> bool:
    if is_handover(rel) or rel in INERT_EXCEPT or _is_header_corpus(rel):
        return False
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in INERT)


def orphan_files() -> list[str]:
    """Tracked files that are in no closure and on no list.

    Each one forces the FULL suite when touched, because `select` refuses to
    skip a script on the strength of a file it has never measured. That refusal
    is correct; a long list of orphans is not. This is the list, so a test can
    hold it at zero and a new file gets classified once instead of silently
    making every gate full.

    A file belongs in exactly one of four places: a measured closure (a test
    reads it), `INERT` (nothing in the gate reads it), `GATE_FILES` (changing
    it invalidates every closure), or `SLOW_GATED` (a test this gate does not
    run). Anything else is an oversight.
    """
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True
    ).stdout.split()
    if not CLOSURES.exists():
        return []
    closures = json.loads(CLOSURES.read_text())["closures"]
    covered = {f for files in closures.values() for f in files}
    selectable = set(selectable_scripts())
    slow = {f"tests/{name}" for name in SLOW_GATED}
    return sorted(
        f
        for f in tracked
        if f not in covered
        and f not in selectable
        and f not in slow
        and not is_inert(f)
        and not is_gate_file(f)
    )


def is_gate_file(rel: str) -> bool:
    return any(rel == p or (p.endswith("/") and rel.startswith(p)) for p in GATE_FILES)


def inert_closure_violations(closures: dict[str, list[str]]) -> list[str]:
    """Files declared INERT ("nothing in the gate reads this") that also
    appear inside a recorded closure ("a test does read this"). The two
    declarations contradict, and the recorded trace is the one taken from a
    running process, so a hit here means either INERT is wrong or the
    recorder over-approximated (#357). `merge` has refused a fresh
    re-derivation on this since it was written; the closures CI job runs
    `--record-only` and never calls `merge`, so nothing on that path ever
    asked the question. Called from both `merge` (a fresh fold) and `check`
    (the committed table, which is what the CI job that never reaches
    `merge` actually validates)."""
    return sorted({f for files in closures.values() for f in files if is_inert(f)})


def test_scripts() -> list[str]:
    """Every runnable test script, as repo-relative paths."""
    out = []
    for p in sorted(list((ROOT / "tests").glob("*.py")) + list((ROOT / "tests").glob("*.mjs"))):
        if p.name in NOT_A_TEST:
            continue
        out.append(str(p.relative_to(ROOT)))
    return out


def selectable_scripts() -> list[str]:
    return [
        s
        for s in test_scripts()
        if Path(s).name not in DRIVEN_BY_OTHERS and Path(s).name not in SLOW_GATED
    ]


def suite_order(names) -> list[str]:
    """The suite's order for ``names``, with the PRODUCERS edge honoured.

    ``test_scripts`` returns ``sorted()``, which is run.sh's order for almost
    every script -- but not for the card pair. ``sorted()`` puts
    ``tests/card.mjs`` ("c") ahead of ``tests/plan_view.py`` ("p"), while
    run.sh runs the plan payload's producer first, because the card reads the
    file plan_view.py writes. Honouring PRODUCERS for membership and then
    reordering into bare suite order undid it for position: the scoped
    re-record ran the card against no payload and failed (#1146). Here every
    producer is moved ahead of the consumers that need it; every other script
    keeps suite order.
    """
    scripts = selectable_scripts()
    pending = set(names)
    out: list[str] = []
    while pending:
        for s in scripts:
            if s in pending and not any(p in pending for p in PRODUCERS.get(s, ())):
                out.append(s)
                pending.discard(s)
                break
        else:
            # A cycle among producers would spin forever. PRODUCERS is a plain
            # "runs first" map with none today; emit the remainder in suite
            # order so a caller still gets a list rather than hanging the gate.
            out += [s for s in scripts if s in pending]
            break
    return out


# ---------------------------------------------------------------------------
# recording


def _pyc_source(path: Path) -> Path | None:
    """The .py a ``__pycache__`` bytecode cache was compiled from, or None.

    PEP 3147 layout only: ``<dir>/__pycache__/<stem>.<tag>.pyc`` stands for
    ``<dir>/<stem>.py``. Anything else found under ``__pycache__`` -- a
    tagless name, a nested directory, a non-.pyc file -- is not a cache the
    import machinery reads, and maps to nothing.
    """
    if path.parent.name != "__pycache__":
        return None
    parts = path.name.split(".")
    if len(parts) < 3 or parts[-1] != "pyc":
        return None
    return path.parent.parent / (".".join(parts[:-2]) + ".py")


def _rel(path: str) -> str | None:
    """Repo-relative path, or None when the path is outside the repo.

    A bytecode-cache .pyc maps to the source it was compiled from (#1309),
    so a warm-__pycache__ load attributes the same file a cold one does.
    """
    if not path:
        return None
    try:
        p = Path(path)
        if not p.is_absolute():
            p = Path.cwd() / p
        p = Path(os.path.normpath(str(p)))
        rel = p.relative_to(ROOT)
    except (ValueError, OSError):
        return None
    s = str(rel)
    if s.startswith(".git/") or s == ".git":
        return None
    if "__pycache__" in s:
        # A .pyc open is a source read in disguise (#1309). On a warm cache
        # the import machinery opens only the bytecode, never the .py -- and
        # a module loaded the way tests/entities.py loads
        # tools/audit/round4/D11/governance_cost.py and tools/release/stamp.py
        # (spec_from_file_location + exec_module, never inserted into
        # sys.modules) is invisible to the end-of-run sweep as well, so a
        # warm-box re-derivation recorded the dependency as absent and
        # check() read the miss as "safe: over-scoped". The cache file is
        # the one observable handle on that load, so attribute the source
        # it was compiled from. A cache whose source is gone, or a non-.pyc
        # file parked under __pycache__, still attributes nothing.
        src = _pyc_source(p)
        if src is None:
            return None
        p = src
        try:
            s = str(p.relative_to(ROOT))
        except ValueError:
            return None
    # The instrument is not a dependency of what it measures.
    if s in ("tests/closure.py", "tests/closures.json"):
        return None
    # A DIRECTORY is not a dependency. The audit hook sees `open` on directories
    # too -- os.scandir, os.listdir and anything that enumerates the tree -- and
    # a directory carries no content a closure can be stale against. Recording
    # them made the two recording paths disagree: #356's per-script `--single`
    # run picked up bare `golden` and `tests` entries for tests/entities.py that
    # the full re-derive does not produce, so `check` reported an
    # under-approximation naming files that do not exist, and every pull request
    # whose scoped set included that script failed `closures` (#365). Anything
    # that is not a regular file goes the same way: a path opened and unlinked
    # within the run is not a dependency either.
    try:
        if not p.is_file():
            return None
    except OSError:
        return None
    return s


def _exec_record(script: str, out_path: str, extra_args: list[str]) -> int:
    """Run `script` in this process under an audit hook and dump its record."""
    opened: set[str] = set()
    spawned: list[list[str]] = []

    def hook(event, args):  # noqa: ANN001 - audit hook signature
        try:
            if event == "open":
                p = args[0]
                if isinstance(p, (str, bytes, os.PathLike)):
                    r = _rel(os.fsdecode(p))
                    if r:
                        opened.add(r)
            elif event in ("compile", "exec"):
                pass
            elif event in ("subprocess.Popen", "os.exec", "os.posix_spawn"):
                argv = args[1] if event == "subprocess.Popen" else args[1]
                try:
                    spawned.append([os.fsdecode(a) for a in argv])
                except Exception:
                    pass
        except Exception:
            pass

    started = time.time()
    rc = 0
    sys.argv = [script, *extra_args]
    sys.addaudithook(hook)
    import runpy

    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as exc:
        rc = int(exc.code or 0) if not isinstance(exc.code, str) else 1
    except BaseException:  # noqa: BLE001 - a failing test still has a closure
        import traceback

        traceback.print_exc()
        rc = 1

    modules = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f:
            r = _rel(f)
            if r:
                modules.add(r)

    # Any repo path that showed up on a subprocess command line is a real
    # dependency too -- that is how features.py reaches tests/dst_checks.py.
    for argv in spawned:
        for a in argv:
            r = _rel(a)
            if r and (ROOT / r).exists():
                opened.add(r)

    record = {
        "script": _rel(str(Path(script).resolve())),
        "rc": rc,
        "seconds": round(time.time() - started, 1),
        "files": sorted(opened | modules),
        "spawned": [" ".join(a) for a in spawned][:200],
        "how": "audithook+sys.modules",
        "argv": [script, *extra_args],
    }
    Path(out_path).write_text(json.dumps(record, indent=1))
    return rc


_STRACE_OPEN = re.compile(r'openat\([^,]+,\s*"([^"]+)"')


def _require_strace() -> None:
    if shutil.which("strace"):
        return
    print(
        "closure: node recording requires strace, which is not available on "
        f"{platform.system()} ({platform.machine()}). "
        "Re-derive node scripts (tests/*.mjs) on Linux or anywhere strace is "
        "installed; CI's closures job records on Linux.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def _record_node(script: str, out_path: str, env: dict) -> int:
    """Record a node script's repo file reads.

    Linux CI uses strace (openat). Darwin has no strace; SIP blocks dtruss.
    The portable path is ``node --import tests/node_fs_trace.mjs``: wrap
    ``fs`` and the ESM loader. Over-approx is safe; under-approx is not.
    """
    if shutil.which("strace"):
        return _record_node_strace(script, out_path, env)
    return _record_node_preload(script, out_path, env)


def _record_node_strace(script: str, out_path: str, env: dict) -> int:
    _require_strace()
    trace = Path(out_path).with_suffix(".strace")
    started = time.time()
    cmd = ["strace", "-f", "-qq", "-e", "trace=openat", "-o", str(trace),
           "node", script]
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    files = set()
    for line in trace.read_text(errors="replace").splitlines():
        m = _STRACE_OPEN.search(line)
        if m:
            r = _rel(m.group(1))
            if r and (ROOT / r).is_file():
                files.add(r)
    trace.unlink(missing_ok=True)
    return _write_node_record(script, out_path, proc, files, "strace", started)


def _record_node_preload(script: str, out_path: str, env: dict) -> int:
    sink = Path(out_path).with_suffix(".nodeopens")
    started = time.time()
    e = dict(env)
    e["CLOSURE_ROOT"] = str(ROOT)
    e["CLOSURE_NODE_TRACE"] = str(sink)
    preload = (ROOT / "tests" / "node_fs_trace.mjs").resolve().as_uri()
    cmd = ["node", "--import", preload, script]
    proc = subprocess.run(cmd, cwd=ROOT, env=e, capture_output=True, text=True)
    files = set()
    if sink.exists():
        try:
            files = {f for f in json.loads(sink.read_text()) if (ROOT / f).is_file()}
        except json.JSONDecodeError:
            files = set()
        sink.unlink(missing_ok=True)
    Path(str(sink) + ".mod").unlink(missing_ok=True)
    return _write_node_record(
        script, out_path, proc, files, "node-fs-trace", started)


def _write_node_record(
    script: str, out_path: str, proc: subprocess.CompletedProcess,
    files: set[str], how: str, started: float,
) -> int:
    record = {
        "script": script if not Path(script).is_absolute() else _rel(script) or script,
        "rc": proc.returncode,
        "seconds": round(time.time() - started, 1),
        "files": sorted(files),
        "spawned": [],
        "how": how,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }
    Path(out_path).write_text(json.dumps(record, indent=1))
    return proc.returncode


def _warm_index() -> None:
    """Refresh git's stat cache, so a record is the script's and not the runner's.

    A closure is supposed to be a property of the script and the tree. It was
    also, silently, a property of the checkout's git index. `git diff
    --name-only HEAD` -- which tests/card_rig.mjs's threeDotFiles and
    tests/env_drift.py's three_dot_files both run -- reads the CONTENT of every
    index entry whose stat cache is stale, because a stat-only difference has
    to be verified before git may call the file unchanged, and strace records
    those reads. So on a worktree whose index is stat-stale for every entry the
    recording is the whole tracked tree: #1243's card_drift.mjs record held 976
    files (978 tracked minus the two `_rel` filters) against 78 committed, and
    976 - 78 = 898 is its "UNDER-SCOPED: tests/card_drift.mjs really reads 898
    file(s) the committed closure does not list" line. The same effect is the
    2-file case INERT_EXCEPT documents for #995, which is the case that must
    stay recorded: there the pair git hashed was stat-DIRTY, because
    harness_headers.py had just rewritten it.

    What separates the two is why the entry is stale, and only one of them is
    the script's business. `git update-index --refresh` is the same
    verification, done once, here, outside the instrument: git re-hashes what
    it must and persists the result to .git/index, so a stat-stale-but-unchanged
    entry is no longer something the recorded run has to read. Files that
    genuinely differ from HEAD stay stale, are still hashed by the run itself
    and still enter the closure -- so this cannot drop a file that appears in a
    diff list, and the #995 pair keeps entering card_drift.mjs's closure.

    It is also what made the full re-derive green and the scoped one red on the
    same tree. The full arm records tests/card.mjs -- the same three git
    commands, by the same rig -- in the step before card_drift.mjs, so the index
    is already warm by then; the scoped arm records only the diff's own scripts,
    and #1243's scoped set (entities.py, env_drift.py, golden.py, plan_view.py,
    card_drift.mjs) contains nothing that refreshes one.

    Best effort on purpose. The lanes of a full derive record in parallel, and a
    .git/index another lane is rewriting has a lock; that leaves the measurement
    exactly as it is without this function. Nothing here may fail a record.
    """
    for attempt in range(3):
        try:
            proc = subprocess.run(
                ["git", "update-index", "-q", "--refresh"],
                cwd=ROOT, capture_output=True, text=True)
        except OSError:
            return
        # --refresh exits 1 for an entry that genuinely needs updating, which is
        # the normal case here (a script that rewrites a tracked file, the
        # register caches of #995). Only .git/index.lock is worth a retry.
        if "index.lock" not in (proc.stderr or ""):
            return
        if attempt < 2:
            time.sleep(0.5)


def record(script: str, out_dir: Path, args: list[str] | None = None) -> int:
    _warm_index()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (Path(script).name + ".json")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "tests" / "hastub") + os.pathsep + env.get("PYTHONPATH", "")
    if script.endswith(".mjs"):
        return _record_node(script, str(out), env)
    cmd = [sys.executable, str(ROOT / "tests" / "closure.py"), "--exec-record", script,
           str(out), *(args or [])]
    proc = subprocess.run(cmd, cwd=ROOT, env=env)
    return proc.returncode


# ---------------------------------------------------------------------------
# merging and rules


def _is_real_file(rel: str) -> bool:
    """Keep files that exist. A trace also catches directory opens (`tests`,
    `golden`) and paths a run probed and did not find; neither is something a
    change can be made to, and a directory in a closure would match nothing."""
    p = ROOT / rel
    return p.is_file()


# The one part of the integration a behaviour capture cannot reach.
#
# `_widen` gives env_drift the WHOLE integration because no tracer can see
# which files a capture in another worktree depended on. That argument covers
# every Python file, and it does not cover the bundled card: frontend.py
# registers `www/` as a static path (a directory handed to the HTTP layer) and
# never opens the file, so nothing in a capture can read its bytes.
#
# Measured before narrowing the rule, both captures on the same tree with
# `env_drift.py --capture . <out> --all`:
#
#   null control     card asset edited (`www/heatpump-optimizer-card.js:14`,
#                    CARD_VERSION 5.4.20 -> 9.9.99): all 55 scenarios
#                    byte-identical, sha256
#                    294c98fb07f7bac0e16342a13a34c354577cf88c60bc9a1e73c52d4432890c10
#                    on both sides
#   positive control  one token, `thermal_model.py:2683`
#                    (`T_room * dt` -> `T_room * dt * 1.0001`): captures
#                    differ, sha256
#                    656df8995f3692d18d12992679aa0dda6b13e082463763e84ca460636736411c
#
# So the card cannot move a capture, and the capture would notice if it could.
# Re-measured at 48f4263 (the merge base after the fork moved); the sha256s
# above are tied to that tree and will shift the next time anyone re-runs
# this probe on a later one -- what must not shift is null == baseline and
# positive != baseline.
# Without this, every card-only pull request ran env_drift's 55-scenario double
# capture -- the most expensive script in the suite -- to prove a plan that
# could not have changed.
FRONTEND_ASSETS = ("custom_components/heatpump_optimizer/www/",)


def _is_frontend_asset(rel: str) -> bool:
    return any(rel.startswith(prefix) for prefix in FRONTEND_ASSETS)


# A second file the whole-integration rule cannot see, for a different
# reason (#357). quality_scale.yaml was simultaneously declared INERT and
# recorded inside env_drift.py's and golden.py's closures -- a contradiction
# `merge` below refuses, that the closures CI job's `--record-only` path
# never reaches, so it was never checked in the configuration that runs.
#
# Decided by measurement, not by reading, on the same tree with
# `env_drift.py --capture . <out> --all` and a direct call to
# `golden.capture()` over five scenarios:
#
#   null control      quality_scale.yaml edited (a trailing comment line
#                     appended): env_drift capture byte-identical, sha256
#                     294c98fb07f7bac0e16342a13a34c354577cf88c60bc9a1e73c52d4432890c10
#                     before and after; golden.capture() over the first five
#                     SCENARIOS keys (winter_single_dhw, winter_two_zone_dhw,
#                     winter_single_no_dhw, winter_two_zone_no_dhw,
#                     summer_dhw_only) byte-identical, sha256
#                     e8bea574c835572442b70180e7747f2ad0c718e42f34aed12af8ff34fecf1be6
#                     before and after
#   positive control  the same probe line as FRONTEND_ASSETS above,
#                     `thermal_model.py:2683` (`T_room * dt` ->
#                     `T_room * dt * 1.0001`): env_drift capture sha256
#                     changes to
#                     656df8995f3692d18d12992679aa0dda6b13e082463763e84ca460636736411c;
#                     golden.capture() over the same five scenarios changes to
#                     84bd6b951368845c5bdcaca6f420f2baafe9f37cd7880b6b4c64b6765dc69546
#
# hassfest skips the quality-scale register for custom repositories, and
# neither capture moves when it changes -- that is the measured basis this
# exclusion keeps, and it survives #951: the register left the INERT list
# when entities.py began reading it, but a DIRECT read recorded in that
# script's closure is not a WIDENED one, and env_drift.py and golden.py
# still have no reason to sit in every register-editing pull request. The
# recorder was the one that was wrong in #357, matching the accepted
# over-approximation ground #251/D3-09 was closed on. Re-measured at
# 48f4263, same caveat as above: the pair (identical / different) is the
# claim, not the exact digits.
NEVER_WIDENED = ("custom_components/heatpump_optimizer/quality_scale.yaml",)


def _widen(closures: dict[str, set[str]]) -> None:
    """Apply, in place, the rules a trace cannot know. Shared by the full fold
    and by the partial (``--single``) overlay, so that re-recording one script
    keeps its rule-widened closure current instead of replacing it with the raw
    trace -- which is how ``env_drift.py`` and ``golden.py`` came to lack
    ``tests/golden/card_claimed_drift.txt`` after it was added, and the
    closures job on main went red for every push."""
    # A script another script drives contributes its whole closure to its
    # driver, and is not selectable on its own.
    for child, parent in DRIVEN_BY_OTHERS.items():
        c, p = f"tests/{child}", f"tests/{parent}"
        if c in closures and p in closures:
            closures[p] |= closures[c]
            del closures[c]

    # PRODUCERS is "must run first" for selection, and the same edge is a
    # closure rule: plan_view.py writes the payload card.mjs and
    # card_drift.mjs read, so anything that can change the payload can
    # change what they test. card_drift.mjs had no copy of this union, which
    # is why a full fold of its 6-file raw trace silently replaced the
    # committed 66 (#527).
    for consumer, producers in PRODUCERS.items():
        if consumer in closures:
            for prod in producers:
                if prod in closures:
                    closures[consumer] |= closures[prod]

    # RULE: env_drift compares BEHAVIOUR between two checkouts, in a
    # subprocess, in a worktree outside this repo. No tracer in this process
    # can see which integration files that behaviour depends on, so the
    # closure is the whole integration -- never a file-name argument.
    ed = "tests/env_drift.py"
    if ed in closures:
        for p in sorted((ROOT / "custom_components").rglob("*")):
            rel = str(p.relative_to(ROOT))
            if (p.is_file() and "__pycache__" not in rel
                    and not _is_frontend_asset(rel) and rel not in NEVER_WIDENED):
                closures[ed].add(rel)
        for p in sorted((ROOT / "tests" / "golden").glob("*")):
            if p.is_file():
                closures[ed].add(str(p.relative_to(ROOT)))
        # The stub Home Assistant the capture runs against, for the same
        # reason. env_drift.py's own header names it: a baseline commit's
        # tracked content "fixes every byte of tests/golden.py,
        # tests/profiles.py, tests/hastub/ and custom_components/", and the
        # coordinator and config-flow captures under --all go through it.
        # The recording lane runs env_drift with a cache key and no capture,
        # so no trace here can see those reads. Until the package root
        # stopped importing the coordinator eagerly they arrived by
        # accident, through an import chain that had nothing to do with what
        # the capture depends on.
        for p in sorted((ROOT / "tests" / "hastub").rglob("*")):
            rel = str(p.relative_to(ROOT))
            if p.is_file() and "__pycache__" not in rel:
                closures[ed].add(rel)
    # golden.py stands in for env_drift in strict mode and captures the same
    # scenarios, so it carries the same closure.
    g = "tests/golden.py"
    if g in closures and ed in closures:
        closures[g] |= closures[ed]



def _fold(records: dict[str, dict]) -> dict[str, list[str]]:
    """Records -> closures, applying the rules a trace cannot know.

    Filtering happens here rather than in the tracer so that it applies
    identically to every record, including ones taken before the filter
    existed.
    """
    closures: dict[str, set[str]] = {}
    for name, rec in records.items():
        closures[name] = {f for f in rec["files"] if _is_real_file(f)}
        # The script's own file is a dependency of itself, even if the tracer
        # somehow missed the read.
        closures[name].add(name)

    _widen(closures)
    return {k: sorted(v) for k, v in sorted(closures.items())}


def _keep_committed_files(name: str, old: set[str], fresh: set[str]) -> list[str]:
    """Never shrink a committed closure -- except past a file that is gone.

    Under-approximation is the direction that makes the gate skip a script.
    A shrinking sibling used to abort the whole merge, so one unreproducible
    node lane vetoed an unrelated repair, and the refusal told you to run a
    full derive -- the path that replaced 66 with 6 (#527).

    The guard is right for a file that still exists and wrong for one that
    does not. A committed entry whose path is not a file is a PHANTOM: a path
    no run can open, so no trace can ever re-record it, and it is not a
    dependency of the script it is filed under. Keeping it is not the safe
    direction -- `select` reads the dead entry as a measurement, so a diff
    that re-creates that path is scoped to a script that never read it
    instead of running FULL for the unmeasured file (#1310). Drop phantoms,
    loudly; keep every real shrink, quietly, as before.
    """
    phantom = sorted(f for f in old if not _is_real_file(f))
    if phantom:
        print(f"closure: {name} lists {len(phantom)} file(s) that do not "
              f"exist; dropping them.", file=sys.stderr)
        for p in phantom:
            print(f"    {p}", file=sys.stderr)
        old = old - set(phantom)
    dropped = sorted(old - fresh)
    if not dropped:
        return sorted(fresh)
    print(f"closure: {name} would drop {len(dropped)} file(s) the committed "
          f"closure listed; keeping them.", file=sys.stderr)
    for d in dropped:
        print(f"    {d}", file=sys.stderr)
    return sorted(old | fresh)


def prune(out: Path = CLOSURES) -> int:
    """Drop committed closure entries whose path is not an existing file.

    `merge` drops phantoms as it writes (#1310), but a table that predates
    the guard -- or one edited by hand -- carries them until a full
    re-derivation folds every script. This repairs the committed file in
    place, touching only the entries no run can re-record, so it needs no
    recordings and no lane. Same predicate the recorder filters with
    (`_is_real_file`), applied to the table `select` actually trusts.
    """
    if not out.exists():
        print(f"closure: {out} is missing", file=sys.stderr)
        return 1
    payload = json.loads(out.read_text())
    closures = payload.get("closures", {})
    total = 0
    for name in sorted(closures):
        files = closures[name]
        real = [f for f in files if _is_real_file(f)]
        phantom = sorted(set(files) - set(real))
        if phantom:
            print(f"closure: {name} drops {len(phantom)} phantom entry(ies):",
                  file=sys.stderr)
            for p in phantom:
                print(f"    {p}", file=sys.stderr)
            total += len(phantom)
        closures[name] = sorted(real)
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"closure: pruned {total} phantom entry(ies) from {out}")
    return 0



def merge(in_dir: Path, out: Path, allow_failures: bool = False,
          partial: bool = False) -> int:
    records = {}
    for f in sorted(in_dir.glob("*.json")):
        rec = json.loads(f.read_text())
        name = rec["script"]
        records[name] = rec
    # DRIVEN_BY_OTHERS scripts ARE recorded (their closure folds into their
    # driver's), so they stay in the expectation; SLOW_GATED ones are not
    # recorded at all, so demanding them here would fail every re-derivation.
    expected = [s for s in test_scripts() if Path(s).name not in SLOW_GATED]
    missing = [s for s in expected if s not in records]
    if missing and not partial:
        print(f"closure: no recording for {', '.join(missing)}", file=sys.stderr)
        return 1
    if not records:
        print("closure: nothing recorded to merge", file=sys.stderr)
        return 1
    # A recording that ended early records only what the run reached before it
    # stopped, which is an UNDER-approximation -- exactly the direction that
    # makes the gate skip a script it should have run. Refuse it.
    broken = sorted(k for k, r in records.items() if r["rc"] != 0)
    if broken and not allow_failures:
        print("closure: these scripts failed while being recorded, so their",
              file=sys.stderr)
        print("closure is only what they reached before stopping:", file=sys.stderr)
        for b in broken:
            print(f"  {b} (exit {records[b]['rc']}) -- see the run output",
                  file=sys.stderr)
        # The flag belongs to THIS command, not to derive_closures.sh, which
        # rejects it as an unknown argument (#1071). A script whose own checks
        # pin the classification being re-recorded can only be recorded this
        # way round: record, merge with the flag, then a plain --single once
        # the committed file already lists the files and rc is 0.
        print("Fix them, or record and merge in two steps if you have checked",
              file=sys.stderr)
        print("that the run still exercised every import and every file read:",
              file=sys.stderr)
        print("  ./tests/derive_closures.sh --record-only --out-dir D", file=sys.stderr)
        print("  python3 tests/closure.py merge --in-dir D --partial --allow-failures",
              file=sys.stderr)
        return 1
    if partial:
        # Overlay just what was recorded onto the committed file: the
        # `--single` path (#90). Every other script's closure stays exactly
        # as committed -- untouched is more trustworthy than stale, and the
        # closures job on main re-derives everything on its own schedule.
        if not out.exists():
            print(f"closure: {out} does not exist; a partial merge needs it",
                  file=sys.stderr)
            return 1
        payload = json.loads(out.read_text())
        # Refresh the disclosure even though everything else in the payload
        # is preserved: a partial merge is the sanctioned way this file is
        # rewritten (#90's --single), so a stale pre-#934 comment would
        # otherwise survive every repair (#934).
        payload["_comment"] = CLOSURES_COMMENT
        closures = payload["closures"]
        recorded = payload.setdefault("recorded", {})
        # Overlay the fresh records on the committed closures and apply the
        # same rules the full fold applies. Without this a single re-record
        # wrote the raw trace, and a rule-widened closure (env_drift.py,
        # golden.py: the whole integration plus every file in tests/golden/)
        # silently lost its widening.
        overlay = {k: set(v) for k, v in closures.items()}
        for k, r in records.items():
            fresh = {f for f in r["files"] if _is_real_file(f)} | {k}
            # node-fs-trace sees Node opens, not strace -f children. Union
            # so Darwin --single can grow a node closure without dropping
            # files only Linux strace recorded.
            if r.get("how") == "node-fs-trace" and k in closures:
                overlay[k] = set(closures[k]) | fresh
            else:
                overlay[k] = fresh
        _widen(overlay)
        touched = set(records)
        for child, parent in DRIVEN_BY_OTHERS.items():
            if f"tests/{child}" in records:
                touched.discard(f"tests/{child}")
                touched.add(f"tests/{parent}")
        for consumer, producers in PRODUCERS.items():
            if consumer in overlay and any(p in records for p in producers):
                touched.add(consumer)
        pair = {"tests/golden.py", "tests/env_drift.py"}
        if touched & pair:
            touched |= pair & set(overlay)
        for k in sorted(touched):
            old = set(closures.get(k, ()))
            closures[k] = _keep_committed_files(k, old, set(overlay[k]))
            if k in records:
                recorded[k] = {
                    "seconds": records[k].get("seconds", 0),
                    "rc": records[k]["rc"],
                }
        # The #357 refusal the full fold applies, scoped to the entries this
        # overlay writes. Without it `--single` -- the sanctioned Darwin
        # re-derivation path -- wrote an INERT-and-recorded pair the full
        # merge and CI's `check` both refuse (#995: harness_headers.py's
        # discovery closure grew to 216 files inside the tools/audit/ prefix,
        # and only the selftest's full-merge pin caught it before push).
        # Touched entries only, so a stale table elsewhere cannot veto an
        # unrelated repair -- the cross-lane veto is what #527 removed.
        bad = inert_closure_violations(
            {k: closures[k] for k in sorted(touched) if k in closures})
        if bad:
            print("closure: files on the INERT list are actually read by tests:",
                  file=sys.stderr)
            for b in bad:
                print(f"  {b}", file=sys.stderr)
            print("  remove them from INERT in tests/closure.py, or except them,",
                  file=sys.stderr)
            print("  then re-run this merge -- check refuses this pair on CI.",
                  file=sys.stderr)
            return 1
        payload["closures"] = closures
        out.write_text(json.dumps(payload, indent=1) + "\n")
        print(f"closure: updated {len(touched)} closure(s) in {out}")
        for k in sorted(touched):
            print(f"  {k:26s} {len(closures[k]):4d} files")
        return 0
    closures = _fold(records)
    if out.exists():
        prev = json.loads(out.read_text()).get("closures", {})
        for k, fresh in list(closures.items()):
            closures[k] = _keep_committed_files(k, set(prev.get(k, ())), set(fresh))
    bad = inert_closure_violations(closures)
    if bad:
        print("closure: files on the INERT list are actually read by tests:", file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        print("  remove them from INERT in tests/closure.py.", file=sys.stderr)
        return 1
    payload = {
        "_comment": CLOSURES_COMMENT,
        "recorded": {k: {"seconds": records[k]["seconds"], "rc": records[k]["rc"]}
                     for k in sorted(records)},
        "closures": closures,
    }
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"closure: wrote {out} ({len(closures)} scripts)")
    for k, v in closures.items():
        print(f"  {k:26s} {len(v):4d} files")
    return 0


def production_names() -> dict[str, str]:
    """Every top-level name a production module defines, name -> module.

    The ``_``-private majority is deliberately included: a test file
    defining its own ``_apply_house_heat_loss_scale`` is exactly as bad
    as one defining ``HOUSE_LOSS_ALPHA`` -- worse, actually, because the
    underscore reads like an import alias.
    """
    names: dict[str, str] = {}
    comp = ROOT / "custom_components" / "heatpump_optimizer"
    for p in sorted(comp.glob("*.py")):
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                names[node.name] = p.stem
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names[t.id] = p.stem
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names[node.target.id] = p.stem
    return names


def no_copies() -> int:
    """Fail when a test file defines a symbol production also defines.

    The rule this enforces is written in tests/README.md and was violated
    twice in one session (issue #91): a test re-implements a production
    formula -- a local confidence curve, a local materiality guard -- and
    asserts against its own copy. The assertion CAN fail, so it survives
    the review that catches tests that cannot, but it fails when the
    TEST FILE's arithmetic changes rather than when production's does,
    and its mutation proofs prove the copy.

    This is deliberately the cheap version the issue proposes: a name
    collision. It is not airtight against a copy that renames the local,
    and it does not try to be -- it raises the cost of the accident,
    which is what this is. Nobody did it on purpose.

    Judged per top-level scope, because that is where a test file's
    helpers live; a same-named LOCAL inside a function is shadowing a
    production name only within those few lines, which the collision
    list would make noisy rather than useful.
    """
    prod = production_names()
    # ``DOMAIN`` and friends are generic enough that a test-local use of
    # the WORD is not a copy claim; anything the tests import is usage,
    # not a definition. Only definitions collide.
    imported_ok = set()
    failed = 0
    for script in test_scripts() + ["tests/harness.py", "tests/profiles.py"]:
        if not script.endswith(".py") or script in NOT_A_TEST:
            if script not in ("tests/harness.py", "tests/profiles.py"):
                continue
        path = ROOT / script
        if not path.exists():
            continue
        tree = ast.parse(path.read_text())
        # What this file legitimately brings in from production: direct
        # from-imports and attributes of imported production modules.
        prod_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and (
                node.module.startswith("heatpump_optimizer")
            ):
                for a in node.names:
                    imported_ok.add(a.asname or a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.startswith("heatpump_optimizer"):
                        prod_modules.add(a.asname or a.name.split(".")[-1])
            elif (isinstance(node, ast.Attribute)
                  and isinstance(node.value, ast.Name)
                  and node.value.id in prod_modules):
                imported_ok.add(node.attr)
        for node in tree.body:
            defined: str | None = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                defined = node.name
            elif isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    defined = node.targets[0].id
            if defined is None or defined not in prod:
                continue
            print(f"COPY-CLAIMED: {script} defines '{defined}', which is "
                  f"production's {prod[defined]}.{defined}")
            failed += 1
    if failed:
        print()
        print(f"{failed} test-file symbol(s) share a name with production.")
        print("A test must import the production symbol, not re-implement")
        print("it: an assertion against a copy fails when the copy changes,")
        print("not when production does. See tests/README.md -- 'import the")
        print("real thing'.")
        return 1
    print("closure: no test file defines a symbol production also defines")
    return 0


def check(in_dir: Path, partial: bool = False) -> int:
    """Fail if the committed closures MISS anything a fresh run touched.

    Under-approximation is the dangerous direction: it is what makes the gate
    skip a script it should have run. Over-approximation only costs time, so
    it is reported and tolerated.

    ``partial`` is the scoped path of the closures job (see ``affected``):
    only the scripts a diff can reach were re-derived, so the roster check
    below -- "a selectable script with no recording at all" -- would fail by
    construction. It is dropped there and only there, and `affected` returns
    FULL whenever a selectable script has no committed closure, so the scoped
    path cannot run on the tree where that roster check would have fired.
    """
    if not CLOSURES.exists():
        print("closure: tests/closures.json is missing", file=sys.stderr)
        return 1
    committed = json.loads(CLOSURES.read_text())["closures"]
    # Same contradiction `merge` refuses, checked here too (#357): the
    # closures CI job runs `derive_closures.sh --record-only`, which never
    # calls `merge`, so a file that is both INERT and inside a recorded
    # closure was never caught in the configuration that actually executes.
    bad = inert_closure_violations(committed)
    if bad:
        print("closure: files on the INERT list are inside a recorded "
              "closure (committed tests/closures.json):", file=sys.stderr)
        for b in bad:
            print(f"  {b}", file=sys.stderr)
        print("  A file cannot be declared unread (INERT) and recorded as "
              "read (in a closure) at the same time. Either it genuinely "
              "affects that script's output and must leave INERT, or the "
              "recorder over-approximated and should stop recording it "
              "(#357).", file=sys.stderr)
        return 1
    # The same existence rule the recorder applies to a fresh trace (#1310),
    # applied to the table `select` actually trusts. The check below reads the
    # fresh recordings, so a phantom the never-shrink guard carried into the
    # committed file -- a path renamed away after it was recorded -- was never
    # asked the question. It is not merely over-scope: over-scope costs time,
    # while a phantom is a FALSE claim that `select` reads as a measurement,
    # so a diff that re-creates that path is scoped to a script that never
    # read it instead of running FULL for the unmeasured file. Fail rather
    # than note, and name the repair. The committed file is pruned in the
    # pull request that added this rule (#1310).
    phantoms = sorted(
        (script, name)
        for script, files in committed.items()
        for name in files
        if not (ROOT / name).is_file()
    )
    if phantoms:
        print("PHANTOM: a committed closure lists a file that does not exist;")
        print("  no run can open it, so nothing re-records it, and `select`")
        print("  reads the dead entry as a measurement that never happened")
        print("  (#1310). Repair the table without a re-derivation:")
        for script, name in phantoms:
            print(f"    {script}: {name}")
        print("  python3 tests/closure.py prune")
        return 1
    records = {}
    for f in sorted(in_dir.glob("*.json")):
        rec = json.loads(f.read_text())
        records[rec["script"]] = rec
    if not records:
        print("closure: no fresh recordings to check against", file=sys.stderr)
        return 1
    # A recorded entry must be a regular FILE. The scoped and full re-derives
    # silently assume they produce the same closure for the same script, and
    # that assumption is what `--single` rests on; directory entries are how it
    # broke (#365). Checked on the fresh recordings rather than on the committed
    # table, so a recorder that starts emitting them again is caught at the run
    # that emits them, not a merge later.
    non_files = sorted(
        (script, name)
        for script, rec in records.items()
        for name in rec.get("files", ())
        if not (ROOT / name).is_file()
    )
    if non_files:
        print("NOT A FILE: a closure recorded something that is not a regular file;")
        print("  a directory carries no content a closure can be stale against,")
        print("  and recording one makes the scoped and full re-derives disagree (#365).")
        for script, name in non_files:
            print(f"    {script}: {name}")
        return 1
    # LOUD, before anything else: a selectable script with no recording at
    # all is the silent-degradation case (issue #90). The lanes in
    # tests/derive_closures.sh record a fixed roster, so a newly added test
    # script is invisible to the under-approximation comparison below -- it
    # was never run -- and the only symptom used to be the PR gate quietly
    # reverting to full mode while CI stayed green. Failing here, on main,
    # does not block the PR that added the script but does not let the
    # omission survive either.
    unmeasured = [] if partial else [
        s for s in selectable_scripts() if s not in records]
    if unmeasured:
        print("closure: selectable script(s) with NO recording this run:")
        for s in unmeasured:
            print(f"    {s}")
        print()
        print("No closure can be recorded for a script the lanes never ran,")
        print("so the scoped gate silently runs FULL on every PR until this")
        print("is fixed. Add the script to a lane in tests/derive_closures.sh")
        print("(or record just it with: ./tests/derive_closures.sh --single")
        print("                         <script>), then commit the re-derived")
        print("tests/closures.json.")
        return 1
    # Fold only when the recordings cover everything a re-derivation produces
    # -- a partial run cannot fold, because a driver may be missing the very
    # recording that would be folded into it. SLOW_GATED scripts are never
    # recorded, so they must not count towards that expectation or a complete
    # run would look partial and dst_checks.py would be checked as if it were
    # selectable in its own right.
    expected_recordings = {
        s for s in test_scripts() if Path(s).name not in SLOW_GATED
    }
    fresh = _fold(records) if set(records) >= expected_recordings else {
        k: sorted(set(v["files"]) | {k}) for k, v in records.items()
    }
    failed = 0
    for name, files in sorted(fresh.items()):
        have = set(committed.get(name, ()))
        if name not in committed:
            print(f"UNDER-SCOPED: {name} has no committed closure")
            failed += 1
            continue
        missing = sorted(set(files) - have)
        if missing:
            print(f"UNDER-SCOPED: {name} really reads {len(missing)} file(s) "
                  f"the committed closure does not list:")
            for m in missing:
                print(f"    {m}")
            failed += 1
        extra = sorted(have - set(files))
        if extra:
            print(f"note: {name} lists {len(extra)} file(s) this run did not "
                  f"touch (safe: over-scoped)")
    if failed:
        print()
        print(f"{failed} closure(s) are stale. Re-derive the named script:")
        print("    ./tests/derive_closures.sh --single <script>")
        print("and commit tests/closures.json. A full derive_closures.sh off")
        print("Linux replaces node-lane recordings; --single cannot shrink them.")
        return 1
    print("closure: committed closures cover every file this run touched")
    return 0


def autofix_allowed(*, event_name: str, closures_result: str,
                    head_repo: str, repo: str, commit_subject: str,
                    loop_subject: str = "ci: re-record closures") -> bool:
    """True only for a failed same-repo PR job that is not our own push."""
    return (
        event_name == "pull_request"
        and closures_result == "failure"
        and head_repo == repo
        and commit_subject != loop_subject
    )


def retrigger_needed(*, pushed: bool, used_pat: bool) -> bool:
    """A GITHUB_TOKEN push's pull_request runs wait for approval; dispatch."""
    return pushed and not used_pat


# Both autofix jobs push only on `changed`, and every other status used to fall
# through to job success -- so a job that repaired nothing looked exactly like
# one that did, and `.cursor/rules/ci-autofix.mdc`'s "wait for the bot commit"
# waited for a commit no step would push (#523). These are the statuses that
# owe a human nothing: a repair happened, or none was ever attempted.
#
# `claims-autofix` is a different shape, not a mirror. `apply_inherited_claims`
# reports no attempted-and-failed status at all, and its `skip-not-inherited`
# is the ordinary answer for every `fast` failure that was not INHERITED
# CLAIMS -- unlike `closures-autofix`, that job never asks which it was, so
# reddening it would redden every unrelated `fast` failure a second time. Its
# entry is here for the summary line and to fail closed on a status added
# later, not because anything it returns today means a skipped repair.
AUTOFIX_QUIET = {
    "closures-autofix": (
        "changed", "skip-clean", "skip-not-allowed", "skip-not-under-scoped"),
    # `skip-moves-nothing-claimable` is a REFUSAL rather than a missed repair:
    # the branch's three-dot cannot have moved a fixture, so its claim file is
    # not the bot's to rewrite, and there is nothing for a human to wait for.
    # `skip-cannot-compare` is quiet for the opposite reason -- the three-dot
    # could not be computed, which `check_claims_hygiene` reports as
    # CANNOT COMPARE on the same run, and two jobs shouting one fact is how
    # the earlier three CI failures became unreadable.
    "claims-autofix": ("changed", "skip-not-allowed", "skip-not-inherited",
                       "skip-moves-nothing-claimable", "skip-cannot-compare"),
}

# Keyed by status where the job-wide remedy would misdirect. A failed
# recording is not repaired by re-deriving: the script stopped early, so its
# recorded closure is truncated, and re-deriving it here would record the same
# truncation.
_AUTOFIX_STATUS_REMEDY = {
    "skip-failed-recording":
        "A script exited non-zero WHILE being recorded, so its closure is only\n"
        "what it reached before stopping -- and merging that would under-scope\n"
        "the gate, which is why the merge refuses it. The under-approximation\n"
        "this job was going to repair is real and still unrepaired.\n"
        "Fix the failing script first; the closures job re-records on the next\n"
        "push and this repair then happens on its own.\n",
}

_AUTOFIX_REMEDY = {
    "closures-autofix":
        "Re-derive the failing script yourself and commit tests/closures.json:\n"
        "    ./tests/derive_closures.sh --single <script>\n"
        "Python lanes record through sys.addaudithook, so a Darwin recording of\n"
        "one is sound; a Darwin recording of a node lane can only widen a Linux\n"
        "one, never replace it.",
    "claims-autofix":
        "Rewrite tests/golden/claimed_drift.txt and card_claimed_drift.txt for\n"
        "THIS diff by hand, keeping `claims-for:` and any `# may-drift:` line.",
}


def autofix_repair_failed(job: str, status: str) -> bool:
    """True when `job`'s status means a repair is owed and no commit is coming.

    Fails closed. A status this table does not carry -- one invented later, or
    the empty string a crashed merge step leaves in the job output -- is a
    repair nobody can wait for, and so is an unknown job.
    """
    return status not in AUTOFIX_QUIET.get(job, ())


def autofix_report(job: str, status: str) -> tuple[int, str]:
    """The job's verdict on its own status: exit code, and what to say."""
    if not autofix_repair_failed(job, status):
        return 0, f"{job}: {status} -- nothing owed to a human."
    return 1, (
        f"{job}: {status} -- THE REPAIR DID NOT HAPPEN.\n"
        "No commit will be pushed, so waiting for one waits forever. This is\n"
        "the case `.cursor/rules/ci-autofix.mdc` already lists as a human\n"
        "judgment call, and its rule against re-recording an UNDER-SCOPED\n"
        "yourself does not apply once the bot has reported that it did not.\n"
        + _AUTOFIX_STATUS_REMEDY.get(status, _AUTOFIX_REMEDY.get(job, "")))


def _autofix_report_cmd(job: str, status: str) -> int:
    rc, text = autofix_report(job, status)
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        # The point of the finding: legible without opening the log.
        with open(summary, "a") as fh:
            fh.write(f"### {job}\n\n```\n{text}\n```\n")
    return rc


def apply_under_scoped_recordings(in_dir: Path, *, partial: bool = True) -> str:
    """Merge recordings into CLOSURES only when check printed UNDER-SCOPED.

    Returns one of: changed, skip-clean, skip-not-under-scoped,
    skip-failed-recording, skip-merge-failed, skip-still-fails,
    skip-unchanged. Restores the previous closures.json text unless the
    status is changed.
    """
    in_dir = Path(in_dir)
    prev = CLOSURES.read_text() if CLOSURES.exists() else None

    def _restore() -> None:
        if prev is None:
            if CLOSURES.exists():
                CLOSURES.unlink()
        else:
            CLOSURES.write_text(prev)

    try:
        records = [json.loads(p.read_text()) for p in sorted(in_dir.glob("*.json"))]
    except (json.JSONDecodeError, OSError):
        return "skip-merge-failed"
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = check(in_dir, partial=partial)
    except (KeyError, TypeError, json.JSONDecodeError, OSError):
        return "skip-merge-failed"
    if rc == 0:
        return "skip-clean"
    if "UNDER-SCOPED" not in out.getvalue() + err.getvalue():
        return "skip-not-under-scoped"
    # Only now, because `closures-autofix` runs on ANY `closures` failure and
    # a failed recording is common to several of them. Reddening it before the
    # test above would fire on every no-copies, NOT-A-FILE or INERT failure
    # that happened to coincide with one, and send its reader to re-derive a
    # closure that was never stale. Past this line UNDER-SCOPED was printed,
    # so this is not that no-op -- and `merge(allow_failures=False)` below
    # would refuse these records anyway, as `skip-merge-failed`. This says
    # which refusal it was, and keeps it loud (#523). The UNDER-SCOPED may
    # itself be an artefact of the failure (an error path reads files the
    # clean path does not), which is why the remedy is "fix the script", not
    # "re-derive it".
    if any(r.get("rc", 0) != 0 for r in records):
        return "skip-failed-recording"

    mout, merr = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(mout), contextlib.redirect_stderr(merr):
            mrc = merge(in_dir, CLOSURES, allow_failures=False, partial=partial)
    except (KeyError, TypeError, json.JSONDecodeError, OSError):
        _restore()
        return "skip-merge-failed"
    if mrc != 0:
        _restore()
        # `merge` printed its reason -- a refused INERT pair, a recording it
        # will not fold without --allow-failures, a shrink it kept -- to the
        # streams captured above. They used to be throwaway buffers, so
        # `closures-autofix` reported a bare `skip-merge-failed` and the job
        # log carried no cause: the reader had to re-derive one (#1139).
        # Surface the text beside the status. The status STRING is unchanged,
        # deliberately: `autofix_repair_failed` and the job's `GITHUB_OUTPUT`
        # are keyed on it.
        reason = (mout.getvalue() + merr.getvalue()).strip()
        if reason:
            print(reason, file=sys.stderr)
        return "skip-merge-failed"

    out2, err2 = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
            rc2 = check(in_dir, partial=partial)
    except (KeyError, TypeError, json.JSONDecodeError, OSError):
        _restore()
        return "skip-still-fails"
    if rc2 != 0:
        _restore()
        return "skip-still-fails"
    new = CLOSURES.read_text() if CLOSURES.exists() else None
    if new == prev:
        return "skip-unchanged"
    return "changed"


def _autofix_cmd(in_dir: Path, out: Path, partial: bool) -> int:
    global CLOSURES
    orig = CLOSURES
    CLOSURES = out
    try:
        status = apply_under_scoped_recordings(in_dir, partial=partial)
    finally:
        CLOSURES = orig
    print(f"AUTOFIX: {status}")
    return 0


# ---------------------------------------------------------------------------
# selection


def changed_files(diff_ref: str) -> list[str]:
    base = subprocess.run(["git", "merge-base", diff_ref, "HEAD"], cwd=ROOT,
                          capture_output=True, text=True)
    ref = base.stdout.strip() if base.returncode == 0 else diff_ref
    out = subprocess.run(["git", "diff", "--name-only", f"{ref}...HEAD"], cwd=ROOT,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"closure: cannot diff against {diff_ref}: {out.stderr.strip()}")
    files = [l.strip() for l in out.stdout.splitlines() if l.strip()]
    # Uncommitted work counts too, so a local `run.sh` scopes to what is
    # actually on disk.
    for extra in (["git", "diff", "--name-only", "HEAD"],
                  ["git", "ls-files", "--others", "--exclude-standard"]):
        o = subprocess.run(extra, cwd=ROOT, capture_output=True, text=True)
        files += [l.strip() for l in o.stdout.splitlines() if l.strip()]
    return sorted(set(files))


def select(files: list[str]) -> dict:
    """Decide what to run. Returns a plan; every decision carries its reason."""
    if not CLOSURES.exists():
        return {"mode": "full", "reason": "tests/closures.json is missing",
                "run": selectable_scripts(), "skip": {}, "changed": files}
    closures = json.loads(CLOSURES.read_text())["closures"]

    scripts = selectable_scripts()
    unknown = sorted(k for k in closures if k not in scripts)
    if unknown:
        return {"mode": "full",
                "reason": f"closures.json describes scripts that no longer exist: "
                          f"{', '.join(unknown)}",
                "run": scripts, "skip": {}, "changed": files}
    uncovered = [s for s in scripts if s not in closures]
    if uncovered:
        return {"mode": "full",
                "reason": f"no closure recorded for {', '.join(uncovered)}",
                "run": scripts, "skip": {}, "changed": files}

    if not files:
        return {"mode": "full", "reason": "no changed files could be determined",
                "run": scripts, "skip": {}, "changed": files}

    for f in files:
        if is_gate_file(f):
            return {"mode": "full",
                    "reason": f"{f} changes the gate itself, so every closure is suspect",
                    "run": scripts, "skip": {}, "changed": files}

    known = {f for files_ in closures.values() for f in files_}
    unmapped = [f for f in files if f not in known and not is_inert(f)]
    if unmapped:
        return {"mode": "full",
                "reason": ("no recorded closure mentions "
                           + ", ".join(unmapped[:6])
                           + (" ..." if len(unmapped) > 6 else "")
                           + " -- an unmeasured file is not a safe skip"),
                "run": scripts, "skip": {}, "changed": files}

    # The belt to the closure's braces: any integration change gets a
    # behavioural diff whether or not the closure saw the file. The bundled
    # card is excluded for the same measured reason `_widen` excludes it --
    # a capture cannot read it (see FRONTEND_ASSETS). Without this, the rule
    # above re-selected env_drift for card-only changes even once its closure
    # no longer listed the card, and the most expensive script in the suite
    # ran on every card pull request to prove a plan that could not move.
    touched_integration = [f for f in files
                           if f.startswith("custom_components/")
                           and not _is_frontend_asset(f)]

    run, skip = [], {}
    for s in scripts:
        hits = sorted(set(files) & set(closures[s]))
        if hits:
            run.append(s)
            continue
        if s == "tests/env_drift.py" and touched_integration:
            run.append(s)
            continue
        skip[s] = {"closure_size": len(closures[s]),
                   "reason": "no changed file is in its measured closure"}

    # Pull in whatever the selected scripts need to have run before them.
    for consumer, producers in PRODUCERS.items():
        if consumer in run:
            for prod in producers:
                if prod in skip:
                    del skip[prod]
                    run.append(prod)
    run = suite_order(run)      # suite order, PRODUCERS edge honoured (#1146)

    return {"mode": "scoped", "reason": "", "run": run, "skip": skip,
            "changed": files, "closure_sizes": {s: len(closures[s]) for s in scripts}}


def print_plan(plan: dict, stream=sys.stdout) -> None:
    """The plan, written so a human scanning the log cannot misread it."""
    w = stream.write
    w("########## scoped gate ##########\n")
    if plan["mode"] == "full":
        w("  MODE: FULL -- every test script runs, nothing is scoped out.\n")
        w(f"  reason: {plan['reason']}\n")
        return
    w(f"  MODE: SCOPED -- {len(plan['run'])} script(s) run, "
      f"{len(plan['skip'])} scoped out.\n")
    w(f"  changed files ({len(plan['changed'])}), measured against the "
      f"recorded closures in tests/closures.json:\n")
    for f in plan["changed"][:60]:
        w(f"      {f}\n")
    if len(plan["changed"]) > 60:
        w(f"      ... and {len(plan['changed']) - 60} more\n")
    w("\n")
    for s_ in plan["run"]:
        w(f"      RUN   {s_}\n")
    w("\n")
    for s_, info in plan["skip"].items():
        w(f"      SKIP  {s_}  (closure: {info['closure_size']} files, "
          f"{info['reason']})\n")
    w("\n")
    w("  A skipped script is a claim that no changed file is in its measured\n")
    w("  closure. The claim is re-checked by the FULL unscoped suite that runs\n")
    w("  on every push to main, so a wrong closure turns main red within one\n")
    w("  gate. Set GATE_SCOPE=full to run everything here and now.\n")


def write_plan(plan: dict, workdir: Path) -> None:
    """Emit the plan as three files run.sh can read without parsing JSON."""
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "scope.json").write_text(json.dumps(plan, indent=1))
    if plan["mode"] == "full":
        (workdir / "scope.run").write_text("")   # empty == no scoping
    else:
        (workdir / "scope.run").write_text("\n".join(plan["run"]) + "\n")
    lines = []
    for s, info in plan.get("skip", {}).items():
        lines.append(f"{s}\t{info['closure_size']}\t{info['reason']}")
    (workdir / "scope.skip").write_text("\n".join(lines) + ("\n" if lines else ""))
    import io
    buf = io.StringIO()
    print_plan(plan, buf)
    (workdir / "scope.txt").write_text(buf.getvalue())


# ---------------------------------------------------------------------------
# the closures check's own scope
#
# `select` above decides which TESTS a change needs. This decides whether the
# `closures` job -- the thing that checks the table `select` trusts -- needs to
# run at all, and if so how much of it.
#
# It exists because that job was scoped by the wrong question. It ran on a pull
# request only when the diff ADDED a file under custom_components/ (#332), so a
# change to what a test READS was checked only after it merged: the pull
# request was green, main went red, and a second pull request repaired it.
# That happened five times -- #214, #320, #332, #340, #349 -- and the sharpest
# case is #353, a pull request that exists solely to fix a closure error and
# whose own `closures` check says `skipping`.
#
# Three cases:
#
#   full    a changed file is a GATE_FILE (every closure is suspect at once),
#           is a script this gate cannot re-derive on its own, or -- the case
#           that matters -- is in NO recorded closure and not INERT. Nothing
#           can be inferred about a file the table has never measured.
#   scoped  some recorded closure contains a changed file: re-derive exactly
#           those scripts, then run the same `check`. One entry is ~40 s
#           against 12-22 minutes for the full table.
#   skip    no recorded closure contains any changed file. Nothing the gate
#           runs reads them, so no recording can move. A docs-only pull request
#           must still cost nothing, or the scoping this replaces was pointless.
#
# The order matters, and the skip is LAST on purpose. The first draft asked
# "is every changed file INERT?" first, and that is a different question: a
# file CAN be on INERT and in a recorded closure at the same time -- that is
# exactly the shape quality_scale.yaml took until #357: listed as inert and
# also inside env_drift's rule-widened closure, simultaneously, on main.
# Asking the hand list first would have skipped a change to a file the table
# said a test reads. The table decides the skip; INERT only licenses a
# file's ABSENCE from the table. #357 fixed the recorder so quality_scale.yaml
# no longer sits in both places (measured: it does not move env_drift's or
# golden's output), and `inert_closure_violations()` now asserts that no
# other file does either -- but the ORDER this function applies stays right
# regardless of whether such a file currently exists, which is what the
# synthetic case in tests/entities.py pins.
#
# The `full` rule carries no path prefix on purpose. The first draft said "a
# changed file under custom_components/ that is in no closure", and the
# argument for it -- an unmeasured file is not a safe skip -- has nothing to do
# with that directory: a file under tests/ in no closure is equally unmeasured.
# An inclusion list of one directory fails OPEN when someone adds a file type
# nobody thought about, which is the failure this whole predicate is here to
# stop; the exclusion list (INERT) fails closed. Today the widened rule costs
# nothing measurable -- `orphan_files()` returns 0, so every non-inert tracked
# file is already in some closure -- and the gap it closes is hard to reach on
# purpose: a new file becomes a dependency only when something reads it, and
# that something is itself in a closure, so the `scoped` rule fires anyway.
# It is defensive, not a live hole. (tvofi-claude-09's objection to the
# narrower draft.)


def affected(files: list[str]) -> dict:
    """Decide whether the closures check must run, and on what. Returns a plan."""
    scripts = selectable_scripts()

    def _full(reason: str) -> dict:
        return {"case": "full", "reason": reason, "rederive": [], "why": {},
                "changed": files}

    # The same preconditions `select` applies, for the same reason: a table
    # that does not describe this tree cannot scope anything, in either
    # direction. They also underwrite `check --partial` -- the scoped path
    # never runs on a tree where a selectable script has no closure, so
    # skipping that check's roster test there cannot hide an unrecorded script.
    if not CLOSURES.exists():
        return _full("tests/closures.json is missing")
    closures = json.loads(CLOSURES.read_text())["closures"]
    unknown = sorted(k for k in closures if k not in scripts)
    if unknown:
        return _full("closures.json describes scripts that no longer exist: "
                     + ", ".join(unknown))
    uncovered = [s for s in scripts if s not in closures]
    if uncovered:
        return _full("no closure recorded for " + ", ".join(uncovered))
    if not files:
        return _full("no changed files could be determined")

    gate = [f for f in files if is_gate_file(f)]
    if gate:
        return _full(f"{gate[0]} changes the gate itself, so every closure "
                     f"is suspect")

    # A script another script drives in a SUBPROCESS reaches the table only
    # through its driver's fold, and `--single` cannot record it (dst_checks.py
    # needs HASTUB_TZ set, which only the lane sets). Re-deriving the driver
    # alone would not see the child's new reads, so a change here is not
    # something the scoped path can check.
    driven = [f for f in files if Path(f).name in DRIVEN_BY_OTHERS]
    if driven:
        return _full(f"{driven[0]} is driven in a subprocess by "
                     f"{DRIVEN_BY_OTHERS[Path(driven[0]).name]}; only a full "
                     f"re-derivation folds its reads in")

    known = {f for files_ in closures.values() for f in files_}
    unmapped = [f for f in files if f not in known and not is_inert(f)]
    if unmapped:
        return _full("no recorded closure mentions "
                     + ", ".join(unmapped[:6])
                     + (" ..." if len(unmapped) > 6 else "")
                     + " -- nothing can be inferred about a file the table "
                       "has never measured")

    why: dict[str, dict] = {}
    for s in scripts:
        hits = sorted(set(files) & set(closures[s]))
        if hits:
            why[s] = {"changed": hits, "via": "closure"}
    # A recording is a real run: card.mjs reads the payload plan_view.py
    # writes, so re-deriving the consumer without its producer records a run
    # that found no payload -- and a failed run records only what it reached.
    for consumer, producers in PRODUCERS.items():
        if consumer in why:
            for prod in producers:
                if prod not in why:
                    why[prod] = {"changed": [], "via": f"producer of {consumer}"}
    # Suite order, so the recordings run in the order run.sh would -- which
    # includes the PRODUCERS edge: the plan payload's producer ahead of the
    # card scripts that read it, or a `--single` re-record of the pair runs
    # the card against no payload and fails (#1146).
    rederive = suite_order(why)
    if not rederive:
        # Everything that changed is absent from every closure, and `unmapped`
        # above already proved each such file is INERT. Nothing a recording
        # could touch has moved.
        return {"case": "skip",
                "reason": "no recorded closure contains any changed file, and "
                          "every one of them is INERT",
                "rederive": [], "why": {}, "changed": files}
    return {"case": "scoped",
            "reason": f"{len(rederive)} closure(s) intersect the diff",
            "rederive": rederive, "why": why, "changed": files}


def print_affected(plan: dict, stream=sys.stdout) -> None:
    """The decision, written so a human scanning the log cannot misread it."""
    w = stream.write
    w("########## closures check ##########\n")
    w(f"  CASE: {plan['case'].upper()} -- {plan['reason']}\n")
    w(f"  changed files ({len(plan['changed'])}):\n")
    for f in plan["changed"][:60]:
        w(f"      {f}\n")
    if len(plan["changed"]) > 60:
        w(f"      ... and {len(plan['changed']) - 60} more\n")
    if plan["case"] == "skip":
        w("  Nothing to re-derive: this check does not run for this change.\n")
        return
    if plan["case"] == "full":
        w("  Every closure is re-derived, exactly as on a push to main.\n")
        return
    w("\n")
    for s in plan["rederive"]:
        info = plan["why"][s]
        pulled = ", ".join(info["changed"][:4]) or info["via"]
        more = f" (+{len(info['changed']) - 4} more)" if len(info["changed"]) > 4 else ""
        w(f"      REDERIVE  {s}  <- {pulled}{more}\n")
    w("\n")
    w("  Every other closure is left alone: no changed file is in it, so a\n")
    w("  fresh recording could not disagree with the committed one. The FULL\n")
    w("  unscoped re-derivation on every push to main re-checks that claim.\n")


def write_affected(plan: dict, workdir: Path) -> None:
    """Emit the decision as files a workflow can read without parsing JSON."""
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "affected.json").write_text(json.dumps(plan, indent=1))
    (workdir / "affected.case").write_text(plan["case"] + "\n")
    (workdir / "affected.scripts").write_text(
        "".join(f"{s}\n" for s in plan["rederive"]))
    import io

    buf = io.StringIO()
    print_affected(plan, buf)
    (workdir / "affected.txt").write_text(buf.getvalue())


# ---------------------------------------------------------------------------
# #527: a full merge used to replace tests/card_drift.mjs's committed 66 with
# the raw 6-file trace, and the refusal that said "run a full re-derivation"
# was the same path. A partial merge aborted the whole overlay at the first
# shrink, so one unreproducible lane vetoed an unrelated repair.


def _selftest_write_records(rec_dir: Path, mapping: dict[str, list[str]]) -> None:
    rec_dir.mkdir(parents=True, exist_ok=True)
    for script, files in mapping.items():
        (rec_dir / f"{Path(script).name}.json").write_text(json.dumps({
            "script": script, "rc": 0, "seconds": 0.1, "files": files,
        }))


def selftest() -> int:
    """Drive merge() and check() against the #527 trap. No suite recording."""
    failed = 0
    n = 0

    # #934 (D3-INST): `recorded[*].seconds` for the two differential guards
    # time the cheap stub invocation derive_closures.sh records them with
    # (golden.py --only __no_such_scenario__, env_drift.py --cache-key <ref>
    # --all) -- the committed table said 0.5 s for a standalone golden.py
    # run the judge measured at 160.9 s -- and closures.json is the only
    # per-script timing table in the tree, so a reader sizing a gate run off
    # it is misled ~300x unless the file's own comment discloses the stub.
    # Both write paths are pinned: a partial merge that only preserved a
    # stale comment would keep pre-#934 text alive through every --single
    # repair of this file.
    disclosure = ("cheap", "golden.py", "env_drift.py")

    def pin(name: str, cond: bool, detail: str = "") -> None:
        nonlocal failed, n
        n += 1
        if cond:
            print(f"  ok   {name}")
        else:
            failed += 1
            extra = f"  [{detail}]" if detail else ""
            print(f"  FAIL {name}{extra}")

    print("\n=== closure shrink guard (#527) ===")
    committed = json.loads(CLOSURES.read_text())["closures"]
    drift = "tests/card_drift.mjs"
    raw_six = [
        "VERSION",
        "tests/card_drift.mjs",
        "tests/card_rig.mjs",
        "tests/dom_stub.mjs",
        "tests/golden/card_claimed_drift.txt",
        "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js",
    ]
    old_drift = set(committed[drift])
    pin(
        "card_drift.mjs's committed closure covers plan_view.py",
        set(committed["tests/plan_view.py"]) <= old_drift,
        f"missing {sorted(set(committed['tests/plan_view.py']) - old_drift)}",
    )
    pin(
        "the 6-file raw trace is a strict subset of that claim",
        set(raw_six) < old_drift,
        f"missing from committed: {sorted(set(raw_six) - old_drift)}",
    )

    expected = [s for s in test_scripts() if Path(s).name not in SLOW_GATED]
    mapping = {}
    for s in expected:
        mapping[s] = list(committed[s]) if s in committed else [s]
    mapping[drift] = raw_six

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(CLOSURES.read_text())
        rec = td_path / "rec"
        _selftest_write_records(rec, mapping)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = merge(rec, out, allow_failures=False, partial=False)
        after = json.loads(out.read_text())["closures"][drift]
        dropped = sorted(old_drift - set(after))
        pin(
            "a full merge does not drop files from card_drift.mjs",
            rc == 0 and old_drift <= set(after),
            f"rc={rc} after={len(after)} dropped={len(dropped)} "
            f"first={dropped[:4]!r}",
        )
        full_comment = json.loads(out.read_text()).get("_comment", "")
        pin(
            "a full merge writes the _comment's stub-seconds disclosure",
            all(w in full_comment for w in disclosure),
            f"_comment={full_comment!r}",
        )

    grower = "tests/open_meteo.py"
    grower_old = [grower]
    grower_new = [grower, "tests/harness.py"]
    shrinker = "tests/frontend.py"
    shrinker_old = [shrinker, "tests/harness.py"]
    shrinker_new = [shrinker]
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(json.dumps({
            "closures": {grower: grower_old, shrinker: shrinker_old},
            "recorded": {},
        }))
        rec = td_path / "rec"
        _selftest_write_records(rec, {grower: grower_new, shrinker: shrinker_new})
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = merge(rec, out, allow_failures=False, partial=True)
        payload = json.loads(out.read_text())["closures"]
        log = buf.getvalue() + err.getvalue()
        pin(
            "a shrinking script does not abort an unrelated grow",
            rc == 0
            and "tests/harness.py" in payload[grower]
            and "tests/harness.py" in payload[shrinker],
            f"rc={rc} grower={payload.get(grower)!r} "
            f"shrinker={payload.get(shrinker)!r}",
        )
        pin(
            "the shrink path does not tell you to run a full derive",
            "full re-derivation" not in log.lower(),
            f"log={log[-400:]!r}",
        )

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(json.dumps({
            "closures": {grower: grower_old},
            "recorded": {},
        }))
        rec = td_path / "rec"
        _selftest_write_records(rec, {grower: grower_new})
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            rc = merge(rec, out, allow_failures=False, partial=True)
        payload = json.loads(out.read_text())["closures"]
        pin(
            "a grow-only partial merge still grows (null control)",
            rc == 0 and payload[grower] == sorted(grower_new),
            f"rc={rc} files={payload.get(grower)!r}",
        )

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(json.dumps({
            "_comment": "MEASURED, not written by hand.",
            "closures": {grower: grower_old},
            "recorded": {},
        }))
        rec = td_path / "rec"
        _selftest_write_records(rec, {grower: grower_new})
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            rc = merge(rec, out, allow_failures=False, partial=True)
        stale_comment = json.loads(out.read_text()).get("_comment", "")
        pin(
            "a partial merge refreshes a stale _comment",
            rc == 0 and all(w in stale_comment for w in disclosure),
            f"rc={rc} _comment={stale_comment!r}",
        )

    widened = {
        drift: {drift},
        "tests/plan_view.py": {"tests/plan_view.py", "tests/profiles.py"},
        "tests/card.mjs": {"tests/card.mjs"},
    }
    _widen(widened)
    pin(
        "card_drift.mjs inherits plan_view.py's closure the way card.mjs does",
        "tests/profiles.py" in widened[drift]
        and "tests/profiles.py" in widened["tests/card.mjs"],
        f"drift={sorted(widened[drift])!r} card={sorted(widened['tests/card.mjs'])!r}",
    )

    brc, blog = _selftest_broken_message()
    pin(
        "a broken-recording refusal names the command that takes the flag",
        brc == 1
        and "tests/closure.py merge" in blog
        and "--record-only" in blog
        and "re-run with --allow-failures" not in blog,
        f"rc={brc} log={blog[-400:]!r}",
    )

    crc, log = _selftest_stale_message()
    pin(
        "a stale-closure refusal names --single, not a bare full derive",
        crc == 1
        and "--single" in log
        and "Regenerate with tests/derive_closures.sh and commit" not in log,
        f"rc={crc} log={log[-400:]!r}",
    )

    fstatus, flog, nstatus, nlog = _selftest_merge_failure_diagnostic()
    pin(
        "a refused merge surfaces merge()'s reason, not just skip-merge-failed",
        fstatus == "skip-merge-failed"
        and "INERT list are actually read by tests" in flog,
        f"status={fstatus!r} log={flog[-400:]!r}",
    )
    pin(
        "and a merge that succeeds carries no merge reason (null control)",
        nstatus == "changed"
        and "INERT list are actually read by tests" not in nlog,
        f"status={nstatus!r} log={nlog[-200:]!r}",
    )

    # #1309 (D3-01): the recorder must attribute a warm-__pycache__ load of a
    # file path. The audit hook fires `open` on the .pyc when the cache is
    # warm and never on the .py, and a module loaded the way entities.py
    # loads governance_cost.py -- spec_from_file_location + exec_module,
    # never inserted into sys.modules -- is invisible to the sweep too, so a
    # warm-box re-derivation recorded the dependency as absent and check()
    # read the miss as "safe: over-scoped". The property, not the instance:
    # any repo pyc path maps to the source it was compiled from, a pyc whose
    # source is gone maps to nothing, and the cold path is unchanged. Pure
    # path arithmetic -- the pinned arm needs no cache to exist, so it holds
    # on a cold CI checkout exactly as on a warm box.
    tag = sys.implementation.cache_tag
    pin(
        "a warm __pycache__ .pyc open attributes the source it was compiled from",
        _rel(str(ROOT / "tests" / "__pycache__" / f"harness.{tag}.pyc"))
        == "tests/harness.py",
        f"_rel(tests/__pycache__/harness.{tag}.pyc)="
        f"{_rel(str(ROOT / 'tests' / '__pycache__' / f'harness.{tag}.pyc'))!r}",
    )
    pin(
        "the #1309 instance maps: governance_cost's cache attributes its source",
        _rel(str(ROOT / "tools/audit/round4/D11/__pycache__"
                 / f"governance_cost.{tag}.pyc"))
        == "tools/audit/round4/D11/governance_cost.py",
        f"_rel(governance_cost.{tag}.pyc)="
        f"{_rel(str(ROOT / 'tools/audit/round4/D11/__pycache__' / f'governance_cost.{tag}.pyc'))!r}",
    )
    pin(
        "a cache whose source is gone attributes nothing (null control)",
        _rel(str(ROOT / "tests" / "__pycache__" / f"no_such_module.{tag}.pyc"))
        is None,
        f"_rel(no_such_module.{tag}.pyc)="
        f"{_rel(str(ROOT / 'tests' / '__pycache__' / f'no_such_module.{tag}.pyc'))!r}",
    )
    pin(
        "the cold path is unchanged (control)",
        _rel(str(ROOT / "tests" / "harness.py")) == "tests/harness.py",
        f"_rel(tests/harness.py)="
        f"{_rel(str(ROOT / 'tests' / 'harness.py'))!r}",
    )

    # #1310 (D3-02): a committed closure entry whose path is not an existing
    # file is a PHANTOM. `_keep_committed_files` never shrank a committed
    # closure (#527), which is right for a file that still exists and wrong
    # for one that does not: a path no test can read is not a dependency, yet
    # `select` reads the dead entry as a measurement, so a diff that
    # re-creates that path is scoped to a script that never read it instead
    # of running FULL for an unmeasured file. The repair has three arms --
    # `merge` drops phantoms, `prune` repairs a table that predates the
    # guard, and `check` fails on one in the committed table -- pinned here
    # against a synthetic table, since the live one is already pruned.
    phantom = "tests/record_status.py"   # renamed to delivery_status.py (#896)
    kept_real = "tests/harness.py"       # exists, absent from the fresh run
    caller = "tests/open_meteo.py"
    rover = [s for s in test_scripts() if Path(s).name not in SLOW_GATED]

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(json.dumps({
            "closures": {caller: [caller, phantom, kept_real]},
            "recorded": {},
        }))
        rec = td_path / "rec"
        # Every other script records just itself, so the full fold's roster
        # check passes; the caller's fresh trace is only the caller.
        _selftest_write_records(rec, {s: [s] for s in rover} | {caller: [caller]})
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            rc = merge(rec, out, allow_failures=False, partial=False)
        after = set(json.loads(out.read_text())["closures"][caller])
        pin(
            "merge drops a committed entry whose path does not exist (#1310)",
            rc == 0 and phantom not in after,
            f"rc={rc} after={sorted(after)!r}",
        )
        pin(
            "merge still keeps a committed REAL file the run did not touch "
            "(#527 null control)",
            kept_real in after,
            f"after={sorted(after)!r}",
        )

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        fake = td_path / "closures.json"
        rec = td_path / "rec"
        _selftest_write_records(rec, {caller: [caller, kept_real]})
        crc, log = _selftest_phantom_check(
            fake, {caller: [caller, phantom, kept_real]}, rec)
        pin(
            "check fails on a phantom in the COMMITTED table (#1310)",
            crc == 1 and phantom in log and "PHANTOM" in log,
            f"rc={crc} log={log[-300:]!r}",
        )
        # Null control: the same table, phantom removed, is clean.
        crc2, log2 = _selftest_phantom_check(
            fake, {caller: [caller, kept_real]}, rec)
        pin(
            "check passes on the same table once the phantom is gone (#1310 "
            "null control)",
            crc2 == 0,
            f"rc={crc2} log={log2[-300:]!r}",
        )

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        out = td_path / "closures.json"
        out.write_text(json.dumps({
            "closures": {caller: [caller, phantom, kept_real]},
            "recorded": {},
        }))
        pruner = globals().get("prune")
        if pruner is None:
            pin("prune drops committed phantom entries (#1310)", False,
                "closure.prune is absent")
        else:
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                prc = pruner(out)
            after = set(json.loads(out.read_text())["closures"][caller])
            pin(
                "prune drops committed phantom entries (#1310)",
                prc == 0 and phantom not in after and kept_real in after,
                f"rc={prc} after={sorted(after)!r}",
            )
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                prc2 = pruner(out)
            pin(
                "prune is idempotent (#1310 null control)",
                prc2 == 0
                and set(json.loads(out.read_text())["closures"][caller]) == after,
                f"rc={prc2} after={sorted(after)!r}",
            )

    if failed:
        print(f"\n{failed} of {n} closure shrink pins FAILED")
        return 1
    print(f"\nALL {n} closure shrink pins PASSED")
    return 0


def _selftest_broken_message() -> tuple[int, str]:
    """merge()'s broken-recording refusal, captured (#1071).

    A bare "re-run with --allow-failures" sends a seat to
    `derive_closures.sh --single X --allow-failures`, which answers `unknown
    argument` -- the refusal has to name the command the flag belongs to.
    """
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        rec = td_path / "rec"
        rec.mkdir(parents=True)
        (rec / "open_meteo.py.json").write_text(json.dumps({
            "script": "tests/open_meteo.py", "rc": 1, "seconds": 0.1,
            "files": ["tests/open_meteo.py"],
        }))
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = merge(rec, td_path / "out.json", allow_failures=False, partial=True)
        return rc, buf.getvalue() + err.getvalue()


def _selftest_stale_message() -> tuple[int, str]:
    grower = "tests/open_meteo.py"
    global CLOSURES
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        fake = td_path / "closures.json"
        fake.write_text(json.dumps({"closures": {grower: [grower]}}))
        rec = td_path / "rec"
        _selftest_write_records(rec, {grower: [grower, "tests/harness.py"]})
        orig = CLOSURES
        CLOSURES = fake
        buf, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = check(rec, partial=True)
        finally:
            CLOSURES = orig
        return rc, buf.getvalue() + err.getvalue()


def _selftest_phantom_check(fake: Path, closures: dict, rec: Path) -> tuple[int, str]:
    """Drive check() against a committed table `closures`, captured (#1310).

    check() reads the module-level CLOSURES, so the table under test is
    swapped in for the call and restored after -- the `_selftest_stale_message`
    pattern, kept in its own function so selftest() never rebinds the global.
    Returns (rc, captured stdout+stderr).
    """
    global CLOSURES
    fake.write_text(json.dumps({"closures": closures, "recorded": {}}))
    orig = CLOSURES
    CLOSURES = fake
    buf, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = check(rec, partial=True)
    finally:
        CLOSURES = orig
    return rc, buf.getvalue() + err.getvalue()


def _selftest_merge_failure_diagnostic() -> tuple[str, str, str, str]:
    """`apply_under_scoped_recordings` surfaces a refused merge's reason (#1139).

    Returns (status, log) for a drive whose merge must REFUSE, then (status,
    log) for the same drive one file over, where the merge succeeds -- the
    null control. A recorded closure that names an INERT file is exactly what
    `merge` refuses (#357), and `merge` prints why. The capture buffers at the
    `merge` call used to be throwaway objects, so `closures-autofix` reported a
    bare `skip-merge-failed` with no cause anywhere in the job log.
    """
    script = "tests/open_meteo.py"

    def drive(files: list[str]) -> tuple[str, str]:
        global CLOSURES
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            fake = td_path / "closures.json"
            fake.write_text(CLOSURES.read_text())
            rec = td_path / "rec"
            _selftest_write_records(rec, {script: [script, *files]})
            orig = CLOSURES
            CLOSURES = fake
            buf, err = io.StringIO(), io.StringIO()
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                    status = apply_under_scoped_recordings(rec, partial=True)
            finally:
                CLOSURES = orig
            return status, buf.getvalue() + err.getvalue()

    # `LICENSE` is INERT and a regular file, so merge() refuses the pair and
    # prints the refusal; `tests/harness.py` is ordinary, so the same overlay
    # merges cleanly.
    return drive(["LICENSE"]) + drive(["tests/harness.py"])


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--exec-record":
        return _exec_record(sys.argv[2], sys.argv[3], sys.argv[4:])
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record"); r.add_argument("script"); r.add_argument("--out-dir", required=True)
    # REMAINDER, not "*": the arguments being forwarded start with dashes
    # (--only, --cache-key), and argparse reads those as options of its own.
    # That silently recorded nothing for golden.py and env_drift.py once.
    r.add_argument("--args", nargs=argparse.REMAINDER, default=[])
    m = sub.add_parser("merge"); m.add_argument("--in-dir", required=True)
    m.add_argument("--out", default=str(CLOSURES))
    m.add_argument("--allow-failures", action="store_true")
    m.add_argument("--partial", action="store_true")
    c = sub.add_parser("check"); c.add_argument("--in-dir", required=True)
    c.add_argument("--partial", action="store_true")
    af = sub.add_parser("autofix")
    af.add_argument("--in-dir", required=True)
    af.add_argument("--partial", action="store_true")
    af.add_argument("--out", default=str(CLOSURES))
    ar = sub.add_parser("autofix-report")
    ar.add_argument("--job", required=True)
    # Not required: a merge step that crashed leaves the output empty, and
    # that has to reach the table as a status rather than as a usage error.
    ar.add_argument("--status", default="")
    pr = sub.add_parser("prune")
    pr.add_argument("--out", default=str(CLOSURES))
    s = sub.add_parser("select")
    s.add_argument("--files", nargs="*"); s.add_argument("--diff")
    s.add_argument("--json", action="store_true")
    s.add_argument("--workdir")
    f = sub.add_parser("affected")
    f.add_argument("--files", nargs="*"); f.add_argument("--diff")
    # A git-produced list, read from a file rather than the command line: a
    # workflow passing `--files $(cat ...)` splits paths on whitespace and
    # loses a long diff to ARG_MAX.
    f.add_argument("--files-from")
    f.add_argument("--json", action="store_true")
    f.add_argument("--workdir")
    sub.add_parser("show")
    sub.add_parser("no-copies")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "record":
        return record(a.script, Path(a.out_dir), a.args)
    if a.cmd == "merge":
        return merge(Path(a.in_dir), Path(a.out), a.allow_failures,
                      partial=a.partial)
    if a.cmd == "check":
        return check(Path(a.in_dir), a.partial)
    if a.cmd == "autofix":
        return _autofix_cmd(Path(a.in_dir), Path(a.out), a.partial)
    if a.cmd == "autofix-report":
        return _autofix_report_cmd(a.job, a.status)
    if a.cmd == "prune":
        return prune(Path(a.out))
    if a.cmd == "no-copies":
        return no_copies()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "show":
        print(CLOSURES.read_text())
        return 0
    if a.cmd == "affected":
        files = list(a.files or [])
        if a.files_from:
            files += [l.strip() for l in
                      Path(a.files_from).read_text().splitlines() if l.strip()]
        if a.diff:
            files += changed_files(a.diff)
        plan = affected(sorted(set(files)))
        if a.workdir:
            write_affected(plan, Path(a.workdir))
        if a.json:
            print(json.dumps(plan, indent=1))
        else:
            print_affected(plan)
        # "nothing affected" is an answer, not an error: the workflow reads the
        # decision, and a non-zero exit here would read as a broken check.
        return 0
    files = list(a.files or [])
    if a.diff:
        files += changed_files(a.diff)
    plan = select(sorted(set(files)))
    if a.workdir:
        write_plan(plan, Path(a.workdir))
    if a.json:
        print(json.dumps(plan, indent=1))
    else:
        print_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
