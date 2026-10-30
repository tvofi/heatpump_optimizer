# Review packet #2973
head: 18c9d3193e4aafd3a7997e125fc6e164ef8343d6
base: 2fde526340bdb1da17fa7a5cd8bff283cff2757c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123784844865 success
arch-score / arch-score id=123936145875 success
arm id=123781087212 skipped
budget-raise-gate / budget-raise-gate id=123936145845 success
cancel-superseded id=123936180163 success
codeql id=123936129209 skipped
codeql / Analyze (actions) id=123936146520 success
codeql / Analyze (javascript-typescript) id=123936147176 success
codeql / Analyze (python) id=123936146704 success
gate id=123936669294 queued
governance id=123936129485 skipped
governance / delivery-status id=123936146763 success
governance / delivery-status-publish id=123936146790 skipped
governance / env-matrix id=123936146644 success
governance / instrument-self-tests id=123936146781 success
governance / policy-docs id=123936146665 success
governance / record id=123936147237 skipped
governance / wave-script id=123936146411 success
hassfest id=123936129022 skipped
hassfest / hassfest id=123936146527 success
kernel-points id=123936146105 skipped
pr-contract / pr-contract id=123936487915 success
prelude id=123936162252 success
refresh id=123936176405 success
tests id=123936128642 skipped
tests / arch-instrument id=123936147242 success
tests / briefs id=123936146999 success
tests / browser id=123936147863 success
tests / ci-ratchet id=123936148517 skipped
tests / claims-autofix id=123936148810 skipped
tests / closure-scope id=123936146167 success
tests / closures id=123936147928 success
tests / closures-autofix id=123936148806 skipped
tests / coverage id=123936147741 success
tests / coverage-ratchet id=123936148000 success
tests / fast (3.14) id=123936147458 success
tests / graders-head-copy id=123936148008 success
tests / lane-proofs id=123936148484 success
tests / mutation id=123936146796 success
tests / mutation-autofix id=123936147919 skipped
tests / mutation-pins id=123936148103 skipped
tests / nightly-ha id=123936148163 skipped
tests / nightly-status id=123936146906 failure
tests / replay id=123936148455 skipped
tests / typing id=123936148113 success
validate id=123936129301 skipped
validate / validate-hacs id=123936146126 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git ls-tree -r -l e5ddba1fa | awk '{s+=$4} END{print s}'
             `git ls-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git archive --format=tar e5ddba1fa | wc -c
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git archive --format=tar HEAD | wc -c
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git archive --format=zip HEAD:custom_components/heatpump_optimizer | wc -c
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git ls-tree -r -l HEAD custom_components/heatpump_optimizer | awk '{s+=$4} END{print s}'
             `git ls-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff e5ddba1fa --workdir <scratch>
             `tests/closure.py` is in the tree at this head
  ok         tests/arch_score_head.py
             `tests/arch_score_head.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/card_drift.mjs
             `tests/card_drift.mjs` is in the tree at this head
  ok         tests/plan_view.py
             `tests/plan_view.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 9 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/release.yml b/.github/workflows/release.yml
index afa51df8b..7cabba06b 100644
--- a/.github/workflows/release.yml
+++ b/.github/workflows/release.yml
@@ -24,15 +24,28 @@ permissions:
   contents: write
 
 # Build provenance (#960, D11-07 option B, owner-approved this wave): every
-# release gains a signed attestation of the tag's tree. The subject is honest
-# about what this repository ships -- no artefact exists and none is built
-# (option C declined: HACS installs from the ref), so the attested subject is
-# the tag's tree itself, serialised deterministically as the `git archive`
-# tar of the tag and digested with sha256. A verifier reproduces the digest
-# with `git archive --format=tar <tag> | sha256sum` and compares it against
-# the attestation; nothing in the statement claims a downloadable asset, and
-# the Signed-Releases scorecard row stays an honest PARTIAL for exactly that
-# reason.
+# release gains a signed attestation of the tag's tree, serialised
+# deterministically as the `git archive` tar of the tag and digested with
+# sha256. A verifier reproduces the digest with
+# `git archive --format=tar <tag> | sha256sum` and compares it against the
+# attestation.
+#
+# The release asset (R10-MARKETPLACE, owner's option (a), 2026-10-29). #960
+# declined option C -- build an artefact -- because HACS installed from the
+# ref. That reason expired with the Home Assistant Marketplace, which replaces
+# HACS in core from 2026.11: it refuses a download over 100 MiB (core
+# marketplace `MAX_DOWNLOAD_SIZE`), and the tag archive of this repository is
+# over it, because dev/ alone is most of it -- so every install fell back to
+# one GitHub API fetch per file. So each release now carries
+# `heatpump_optimizer.zip`: the integration folder's own files at the archive
+# root, which is what a `zip_release` install unpacks into
+# custom_components/heatpump_optimizer. `hacs.json` names it under `filename`,
+# and tests/entities.py pins the two names equal. The release is created as a
+# draft carrying the asset and published only once the asset is read back on
+# it, so a release without its asset fails this run and is never published.
+# The attested subject stays the tag's tree: the asset is that tree's
+# custom_components/heatpump_optimizer subtree, packed by `git archive` from
+# the same commit.
 jobs:
   release:
     runs-on: ubuntu-latest
@@ -54,6 +67,11 @@ jobs:
       contents: write
       id-token: write
       attestations: write
+    env:
+      # The release asset's name. hacs.json's `filename` must equal it: the
+      # Marketplace downloads the asset of that name, and tests/entities.py
+      # and the check step below both refuse a mismatch.
+      ASSET: heatpump_optimizer.zip
     steps:
       - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5
         with:
@@ -133,19 +151,77 @@ jobs:
             echo "See RELEASE_NOTES.md for ${TAG}." > /tmp/notes.md
           fi
 
+      - name: Build the integration ZIP
+        run: |
+          set -euo pipefail
+          # `<commit>:<path>` archives that subtree with its files at the
+          # archive root -- the layout a `zip_release` install unpacks into
+          # custom_components/heatpump_optimizer -- and only tracked files,
+          # so no __pycache__ or local file of the runner reaches it.
+          git archive --format=zip -o "${RUNNER_TEMP}/${ASSET}" \
+            "${GITHUB_SHA}:custom_components/heatpump_optimizer"
+
+      - name: Check the integration ZIP
+        run: |
+          set -euo pipefail
+          python3 - "${RUNNER_TEMP}/${ASSET}" <<'EOF'
+          import json, os, sys, zipfile
+          path, asset = sys.argv[1], os.environ["ASSET"]
+          hacs = json.load(open("hacs.json"))
+          problems = []
+          if hacs.get("zip_release") is not True:
+              problems.append("hacs.json does not set zip_release to true")
+          if hacs.get("filename") != asset:
+              problems.append(f"hacs.json names {hacs.get('filename')!r}, "
+                              f"this workflow uploads {asset!r}")
+          with zipfile.ZipFile(path) as z:
+              infos = z.infolist()
+              names = {i.filename for i in infos}
+              unpacked = sum(i.file_size for i in infos)
+              manifest = (json.loads(z.read("manifest.json"))
+                          if "manifest.json" in names else {})
+          if manifest.get("domain") != "heatpump_optimizer":
+              problems.append("manifest.json of this integration is not at "
+                              "the archive root")
+          # The Marketplace's download limit is 100 MiB; both the download
+          # and what it unpacks to stay under it.
+          limit = 100 * 1024 * 1024
+          for what, size in (("download", os.path.getsize(path)),
+                             ("unpacked", unpacked)):
+              if size >= limit:
+                  problems.append(f"{what} size {size} is not under {limit}")
+          for p in problems:
+              print(f"::error::{p}")
+          sys.exit(1 if problems else 0)
+          EOF
+
       - name: Create the GitHub release
         env:
           GH_TOKEN: ${{ github.token }}
         run: |
-          # On dispatch the tag does not exist yet; --target pins it to
-          # the commit this run checked out, and gh creates tag+release
-          # in one go. On a tag push the tag exists and --target is
-          # ignored by GitHub for an existing tag.
-          gh release create "${TAG}" \
+          # As a DRAFT carrying the asset: the next step publishes it only
+          # once the asset is read back. On dispatch the tag does not exist
+          # yet; --target pins it to the commit this run checked out, and
+          # publishing the draft creates the tag there. On a tag push the tag
+          # exists and --target is ignored by GitHub for an existing tag.
+          gh release create "${TAG}" "${RUNNER_TEMP}/${ASSET}" \
+            --draft \
             --target "${GITHUB_SHA}" \
             --title "${TAG}" \
             --notes-file /tmp/notes.md
 
+      - name: Publish the release once its asset is on it
+        env:
+          GH_TOKEN: ${{ github.token }}
+        run: |
+          set -euo pipefail
+          if ! gh release view "${TAG}" --json assets --jq '.assets[].name' \
+              | grep -Fqx "${ASSET}"; then
+            echo "::error::release ${TAG} does not carry ${ASSET}; left as a draft, not published" >&2
+            exit 1
+          fi
+          gh release edit "${TAG}" --draft=false
+
       - name: Digest the tag's tree
         run: |
           # The attested subject is the TAG as it exists on the remote,
@@ -165,8 +241,8 @@ jobs:
         uses: actions/attest-build-provenance@4d101475d8b20a2381f78447822ac1eab6504dd8 # v4.2.2
         with:
           # The subject NAME is the honest claim: the tag's source tree,
-          # git-archive serialised -- not an artefact, not a zip, nothing
-          # downloadable. `subject-digest` is the sha256 the previous step
+          # git-archive serialised -- not the release asset, which is one
+          # subtree of it. `subject-digest` is the sha256 the previous step
           # computed over exactly that serialisation.
           subject-name: "tvofi/heatpump_optimizer ${{ env.TAG }} source tree (git archive tar)"
           subject-digest: "sha256:${{ env.TREE_SHA256 }}"
diff --git a/README.md b/README.md
index c642c177d..4d291dcb2 100644
--- a/README.md
+++ b/README.md
@@ -314,10 +314,28 @@ installing rather than discover it after:
 > [!IMPORTANT]
 > **Home Assistant 2025.2.0 and Python 3.13 are the minimum, and that was a
 > breaking change.** An installation on an older Home Assistant stops being
-> offered updates through HACS. Why the floor sits exactly there is in
+> offered updates through the Marketplace or HACS. Why the floor sits exactly there is in
 > [docs/architecture.md](docs/architecture.md).
 
-### HACS (recommended)
+[![Open your Home Assistant instance and open this repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tvofi&repository=heatpump_optimizer&category=integration)
+
+### Home Assistant Marketplace (2026.11 and later)
+
+The Marketplace replaces HACS in Home Assistant itself from 2026.11. Each
+release carries `heatpump_optimizer.zip`, the integration folder alone, and
+the Marketplace installs from that asset. The button above is the short way
+to open this repository in your own Home Assistant: it does steps 1 and 2 for
+you, in the Marketplace from 2026.11 and in HACS before it.
+
+1. Add this repository to the Marketplace as a custom repository.
+2. Install **Heat Pump Cost Optimizer**.
+3. Restart Home Assistant.
+4. Go to **Settings → Devices & services → Add integration → Heat Pump Cost
+   Optimizer**.
+
+### HACS (before 2026.11)
+
+Before 2026.11 the same four steps run in HACS:
 
 1. Add this repository to HACS as a custom repository.
 2. Install **Heat Pump Cost Optimizer**.
@@ -366,7 +384,8 @@ things are left behind on purpose, because deleting them is your call:
   uses the card; a card left on a dashboard shows "Custom element doesn't
   exist" afterwards.
 
-Then uninstall the code: in HACS, open **Heat Pump Cost Optimizer** and choose
+Then uninstall the code: in the Marketplace (HACS before 2026.11), open
+**Heat Pump Cost Optimizer** and choose
 **Remove** (for a manual install, delete `custom_components/heatpump_optimizer`),
 and restart Home Assistant. Nothing needs doing on Tibber's side — the token was
 only ever stored in the entry — though you can revoke it at
diff --git a/custom_components/heatpump_optimizer/manifest.json b/custom_components/heatpump_optimizer/manifest.json
index c3efd3174..d62567f25 100644
--- a/custom_components/heatpump_optimizer/manifest.json
+++ b/custom_components/heatpump_optimizer/manifest.json
@@ -5,6 +5,10 @@
     "mqtt",
     "recorder"
   ],
+  "categories": [
+    "climate.heat_pumps_air_conditioning",
+    "energy.energy_prices"
+  ],
   "codeowners": [
     "@tvofi"
   ],
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 890c5bfdb..7fb9db682 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -992,7 +992,7 @@
  {
   "id": "C111",
   "source": "README.md + docs/*.md",
-  "claim": "every external link answers 200 to a HEAD request (17 links)",
+  "claim": "every external link answers 200 to a HEAD request (19 links)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links",
   "result": "not run: pass --links",
   "verdict": "unverifiable",
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 028e0f451..0b4cf05fb 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -114,7 +114,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C108 | `README.md + docs/*.md` | every relative link resolves (84 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 84 links, broken=[], of which removed-by-the-export=[] | **true** |  |
 | C109 | `README.md + docs/how-it-works.md` | the links to docs/audit-2026-08.md, docs/audit-2026-09.md and docs/backlog.md resolve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | finder_wall in tools/audit/prepare_baseline.sh removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md; this tree cannot answer | **unverifiable** | not checkable in the export -- finder_wall removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md |
 | C110 | `README.md + docs/*.md` | every image the documentation embeds exists (22 images) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 22 images, missing=[] | **true** |  |
-| C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (17 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
+| C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (19 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
 | C112 | `strings.json + translations/*.json` | every translation file carries exactly the keys strings.json declares | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | languages=['en', 'sv'], missing={'en': 0, 'sv': 0}, extra={'en': 0, 'sv': 0} | **true** |  |
 | C113 | `README.md` | entity names are translated into English and Swedish | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['en', 'sv'] measured=['en', 'sv'] | **true** |  |
 | C114 | `README.md` | every entity's display name comes from the translation files | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | untranslated=[] | **true** |  |
diff --git a/dev/programme/delivery/2973.md b/dev/programme/delivery/2973.md
new file mode 100644
index 000000000..e57e7c9c2
--- /dev/null
+++ b/dev/programme/delivery/2973.md
@@ -0,0 +1 @@
+- [#2973](https://github.com/tvofi/heatpump_optimizer/pull/2973) — **open**, R10-MARKETPLACE: ship the integration through the Home Assistant Marketplace (R10-MARKETPLACE)
diff --git a/docs/dashboard-card.md b/docs/dashboard-card.md
index 1f6ccb064..e6552d388 100644
--- a/docs/dashboard-card.md
+++ b/docs/dashboard-card.md
@@ -814,7 +814,8 @@ when the browser reports `prefers-reduced-motion: reduce`.
 
 ### Automatic (recommended)
 
-When you install the integration through HACS and add a config entry, the card is
+When you install the integration through the Home Assistant Marketplace (HACS
+before 2026.11) and add a config entry, the card is
 served and registered automatically:
 
 1. The integration exposes the JS at `/heatpump_optimizer_static/heatpump-optimizer-card.js`.
diff --git a/docs/index.html b/docs/index.html
index 584b17578..e07066520 100644
--- a/docs/index.html
+++ b/docs/index.html
@@ -211,11 +211,11 @@ footer .brand { font-size: 1rem }
 
 <main id="main">
 <div class="hero" id="top"><div class="wrap">
-  <span class="eyebrow">Home Assistant integration · installs with HACS</span>
+  <span class="eyebrow">Home Assistant integration · installs from the Marketplace or HACS</span>
   <h1 data-src="README.md#heat-pump-cost-optimizer-for-home-assistant">As warm as you asked, <em>bought in better hours</em>.</h1>
   <p class="lede" data-src="README.md#heat-pump-cost-optimizer-for-home-assistant">Model-predictive heating control for Home Assistant. It plans your heat pump and your hot water 24 hours ahead against hourly electricity prices, the weather forecast, and a thermal model of your own house that it keeps correcting from your own sensors.</p>
   <div class="cta">
-    <a class="btn primary" href="#install">Install with HACS</a>
+    <a class="btn primary" href="#install">Install from the Marketplace</a>
     <a class="btn ghost" href="#docs">Read the documentation</a>
   </div>
   <figure>
@@ -342,15 +342,17 @@ footer .brand { font-size: 1rem }
 </section>
 
 <section class="band" id="install" aria-labelledby="in-h">
-  <div class="sec-head"><span class="eyebrow">Get started</span><h2 id="in-h">From HACS to a first plan</h2></div>
+  <div class="sec-head"><span class="eyebrow">Get started</span><h2 id="in-h">From the Marketplace to a first plan</h2></div>
   <div class="start">
-    <div class="panel" data-src="README.md#hacs-recommended"><h3 data-copy>HACS (recommended)</h3>
+    <div class="panel" data-src="README.md#home-assistant-marketplace-202611-and-later"><h3 data-copy>Home Assistant Marketplace (2026.11 and later)</h3>
       <ol class="hacs">
-        <li><span>Add this repository to HACS as a custom repository.</span></li>
+        <li><span>Add this repository to the Marketplace as a custom repository.</span></li>
         <li><span>Install Heat Pump Cost Optimizer.</span></li>
         <li><span>Restart Home Assistant.</span></li>
         <li><span>Go to Settings → Devices &amp; services → Add integration → Heat Pump Cost Optimizer.</span></li>
-      </ol></div>
+      </ol>
+      <p class="muted" style="margin-top:12px" data-src="README.md#hacs-before-202611">Before 2026.11 the same four steps run in HACS.</p>
+      <p style="margin-top:12px"><a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=tvofi&amp;repository=heatpump_optimizer&amp;category=integration">Open this repository in your own Home Assistant</a></p></div>
     <div style="display:grid;gap:16px;align-content:start">
       <div class="panel" data-src="README.md#requirements"><h3 data-copy>Requirements</h3>
         <ul class="req"><li><b>Home Assistant 2025.2.0 or newer</b></li><li>Python 3.13 or newer</li><li>numpy, scipy and threadpoolctl, installed automatically from the integration manifest</li></ul></div>
diff --git a/docs/setup.md b/docs/setup.md
index 7a7ef0731..9488a4150 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -46,8 +46,9 @@ meter — is optional and can be pointed at later from the options pages.
 ## Adding the integration
 
 **Settings → Devices & services → Add integration → Heat Pump Cost
-Optimizer** (from HACS or a manual install; see the
-[README](../README.md#installation) for both).
+Optimizer** (from the Home Assistant Marketplace on 2026.11 and later, from
+HACS before it, or a manual install; see the
+[README](../README.md#installation) for all three).
 
 The first two screens are the only required answers in the whole flow. After
 them, the flow asks how you want to finish, and each of the three answers
diff --git a/hacs.json b/hacs.json
index c17408881..31a6627ed 100644
--- a/hacs.json
+++ b/hacs.json
@@ -1,5 +1,6 @@
 {
   "name": "Heat Pump Cost Optimizer",
-  "render_readme": true,
-  "homeassistant": "2025.2.0"
+  "homeassistant": "2025.2.0",
+  "zip_release": true,
+  "filename": "heatpump_optimizer.zip"
 }
diff --git a/tests/entities.py b/tests/entities.py
index 6a6dead25..edf1592c5 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -1284,8 +1284,10 @@ R.check(
     f"the census is {_arch_diagram_want}",
 )
 
-# HACS renders this README inside Home Assistant -- `hacs.json` asks for it,
-# and hacs/integration's `async_get_info_file_contents` reads README.md -- so
+# HACS renders this README inside Home Assistant -- hacs/integration's
+# `async_get_info_file_contents` reads README.md for every repository, with no
+# `hacs.json` key asking for it (`render_readme` is not a key HACS knows, and
+# R10-MARKETPLACE dropped it from `hacs.json`) -- so
 # the README has a second renderer, and it is much weaker than GitHub's.
 # hacs/frontend's repository dashboard passes it to `<ha-markdown>` with no
 # `allow-svg`, which is home-assistant/frontend's markdown-worker: plain
@@ -32851,11 +32853,12 @@ R.check(
     "replaces, because `gh release create` uses it. Anything beyond these "
     "three is scope this job does not use and should not hold",
 )
-# The subject honesty is the other half of the approval: option C (build an
-# artefact) is declined because HACS installs from the ref, so the attested
-# subject must be the tag's tree itself -- a digest recomputable by anyone
-# from the tag -- and never a zip, an upload, or an asset the release does
-# not carry. The pins are the wiring that makes that claim checkable: the
+# The subject honesty is the other half of the approval: the attested subject
+# is the tag's tree itself -- a digest recomputable by anyone from the tag --
+# and never a built file. #960 declined option C (build an artefact) because
+# HACS installed from the ref; R10-MARKETPLACE reversed that for the
+# Marketplace's 100 MiB download limit and added `heatpump_optimizer.zip`
+# (pinned below), but the attestation still names the tree, not the asset. The pins are the wiring that makes that claim checkable: the
 # digest step serialises the tag with `git archive`, and the attestation
 # carries that digest under `subject-digest`, pinned by its own SHA.
 _REL_ATTEST_PIN = re.search(
@@ -32873,8 +32876,141 @@ R.check(
     f"subject-path present={'subject-path:' in _REL_JOB} (must be False); the "
     "digest step serialises the tag's tree and the attestation carries that "
     "sha256 -- `subject-path` would bind the statement to a built file, which "
-    "is the overclaim #960 exists to remove while the artefact build stays "
-    "declined",
+    "is not what #960 approved: the attestation covers the tree, of which "
+    "the release asset is one subtree",
+)
+
+# --- the release asset the Marketplace installs (R10-MARKETPLACE) ------------
+#
+# The Home Assistant Marketplace, HACS's successor in core from 2026.11,
+# refuses a download over 100 MiB, and this repository's tag archive is over
+# it; with `zip_release` it downloads the release asset `hacs.json` names
+# under `filename` instead. Three things make that true, each pinned here:
+#   * `hacs.json` sets `zip_release` and names exactly the asset release.yml
+#     uploads (the job's `ASSET`), and holds no key HACS does not know -- a
+#     wrong `filename` installs nothing, and the Marketplace says only that
+#     the asset is missing;
+#   * the build and check steps, RUN in a scratch repository, produce a ZIP
+#     with the integration's manifest.json at its root and no
+#     custom_components/ prefix, and the check refuses a `hacs.json` naming
+#     another file;
+#   * the release is created as a draft carrying the asset, and published by
+#     a later step that reads the asset back, so a release without its asset
+#     fails the run and is never published.
+# Design choice, said out loud (fixer.md step 11): the asset name is stated
+# once in the workflow and once in hacs.json, and this check pins them equal,
+# rather than the workflow reading hacs.json, so that a wrong `filename` is
+# refused here instead of being uploaded under the wrong name.
+_HACS_KEYS = {"name", "content_in_root", "zip_release", "filename",
+              "hide_default_branch", "country", "homeassistant", "hacs",
+              "persistent_directory"}
+_REL_DOC = _yaml.safe_load(Path(_REL_WF).read_text()) or {}
+_REL_JOBD = ((_REL_DOC.get("jobs") or {}).get("release") or {})
+_REL_ASSET = (_REL_JOBD.get("env") or {}).get("ASSET")
+_REL_STEPS = {str((_s or {}).get("name")): _i for _i, _s in
+              enumerate(_REL_JOBD.get("steps") or [])}
+_REL_RUN = {str((_s or {}).get("name")): str((_s or {}).get("run") or "")
+            for _s in _REL_JOBD.get("steps") or []}
+_HACS_DOC = json.loads(Path("hacs.json").read_text())
+
+
+def _rel_hacs_defects(hacs: dict, asset: "str | None") -> "list[str]":
+    out: "list[str]" = []
+    if hacs.get("zip_release") is not True:
+        out.append(f"zip_release is {hacs.get('zip_release')!r}, not true")
+    if not asset or hacs.get("filename") != asset:
+        out.append(f"hacs.json filename {hacs.get('filename')!r} is not the "
+                   f"asset release.yml uploads ({asset!r})")
+    if set(hacs) - _HACS_KEYS:
+        out.append(f"keys HACS does not know: {sorted(set(hacs) - _HACS_KEYS)}")
+    return out
+
+
+def _rel_zip_defects(build: str, check: str, asset: str) -> "list[str]":
+    """Run the build and check steps in a scratch repository."""
+    import zipfile
+    out: "list[str]" = []
+    with tempfile.TemporaryDirectory() as tmp:
+        repo = Path(tmp) / "repo"
+        files = {"hacs.json": json.dumps({"zip_release": True,
+                                          "filename": asset}),
+                 "custom_components/heatpump_optimizer/manifest.json":
+                     json.dumps({"domain": "heatpump_optimizer"}),
+                 "custom_components/heatpump_optimizer/sub/a.py": "x = 1\n",
+                 "dev/big.txt": "outside the integration\n"}
+        for rel, body in files.items():
+            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
+            (repo / rel).write_text(body)
+        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
+        env = throwaway_git_init(repo, "-q")
+        subprocess.run(git + ["add", "-A"], cwd=repo, check=True, env=env)
+        subprocess.run(git + ["commit", "-qm", "t"], cwd=repo, check=True,
+                       env=env)
+        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, env=env,
+                             check=True, capture_output=True,
+                             text=True).stdout.strip()
+
+        def run(script: str) -> int:
+            e = dict(os.environ, RUNNER_TEMP=tmp, ASSET=asset, GITHUB_SHA=sha)
+            return subprocess.run(["bash", "--noprofile", "--norc", "-eo",
+                                   "pipefail", "-c", script], cwd=repo, env=e,
+                                  capture_output=True, text=True).returncode
+        if run(build) != 0:
+            return ["the build step fails"]
+        zpath = Path(tmp) / asset
+        names = set(zipfile.ZipFile(zpath).namelist()) if zpath.is_file() else set()
+        if "manifest.json" not in names or "sub/a.py" not in names \
+                or any(n.startswith(("custom_components/", "dev/")) for n in names):
+            out.append(f"the ZIP holds {sorted(names)}, not the integration "
+                       "folder's files at its root")
+        if run(check) != 0:
+            out.append("the check step refuses a correct ZIP")
+        (repo / "hacs.json").write_text(json.dumps(
+            {"zip_release": True, "filename": "wrong.zip"}))
+        if run(check) == 0:
+            out.append("the check step passes a hacs.json naming another file")
+    return out
+
+
+R.check(
+    "hacs.json names the release asset release.yml uploads, with zip_release",
+    not _rel_hacs_defects(_HACS_DOC, _REL_ASSET),
+    "; ".join(_rel_hacs_defects(_HACS_DOC, _REL_ASSET)) or "holds",
+)
+# Null control: the same reader refuses a wrong filename, so the pass above
+# is the files agreeing, not the reader passing everything.
+R.check(
+    "the hacs.json asset reader refuses a filename release.yml does not upload",
+    bool(_rel_hacs_defects(dict(_HACS_DOC, filename="wrong.zip"), _REL_ASSET)),
+    "a hacs.json naming wrong.zip read as clean",
+)
+_REL_ZIP_DEFECTS = _rel_zip_defects(
+    _REL_RUN.get("Build the integration ZIP", "exit 1"),
+    _REL_RUN.get("Check the integration ZIP", "exit 1"),
+    _REL_ASSET or "unset.zip")
+R.check(
+    "the release ZIP holds the integration folder at its root, and its check "
+    "refuses a hacs.json naming another file",
+    not _REL_ZIP_DEFECTS,
+    "; ".join(_REL_ZIP_DEFECTS) or "holds",
+)
+_REL_ORDER = [_REL_STEPS.get(_n) for _n in (
+    "Build the integration ZIP", "Check the integration ZIP",
+    "Create the GitHub release", "Publish the release once its asset is on it",
+    "Digest the tag's tree")]
+_REL_CREATE = _REL_RUN.get("Create the GitHub release", "")
+_REL_PUBLISH = _REL_RUN.get("Publish the release once its asset is on it", "")
+R.check(
+    "the release is a draft carrying the asset until a later step reads the "
+    "asset back and publishes it",
+    None not in _REL_ORDER and _REL_ORDER == sorted(_REL_ORDER)
+    and "--draft" in _REL_CREATE and "${ASSET}" in _REL_CREATE
+    and "--draft=false" not in _REL_CREATE
+    and "--json assets" in _REL_PUBLISH and "--draft=false" in _REL_PUBLISH
+    and _REL_PUBLISH.index("--json assets") < _REL_PUBLISH.index("--draft=false"),
+    f"step order {_REL_ORDER}; create has --draft={'--draft' in _REL_CREATE} "
+    f"asset={'${ASSET}' in _REL_CREATE}; publish reads assets="
+    f"{'--json assets' in _REL_PUBLISH} then publishes",
 )
 
 # --- the two instruments beside the gate: coverage and mutation (#195) -------

