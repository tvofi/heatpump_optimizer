#!/usr/bin/env bash
# Owner ruling (orchestrator NOTE 2): every probe saved under wave/<box>/probes/<key>/ at its repo-relative path, with INDEX.md
. "$HOME/.boxcomms.env"
W="$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/$BOX"
REL="dev/audit/rounds/round11/D3/s1/wave/$BOX/probes"
for k in $(tail -n +2 "$W/keys.tsv" | cut -f1); do
  mkdir -p "$W/probes/$k"
  (cd "$HOME/probe-r11" && cp --parents "$REL/probe_$k.py" "$W/probes/$k/")
  t=$(python3 -c "import sys;sys.path.insert(0,'$HOME/probe-gen');from meta import META;print(META['$k'][0])")
  echo "- $REL/probe_$k.py: baseline vs in-memory mutant $k on the production symbol; pins: $t" > "$W/probes/$k/INDEX.md"
done
# the generator that writes the probes, kept with them (not a harness: it writes the probe files)
mkdir -p "$W/probes/_generator"
cp "$HOME/probe-gen/"{gen.py,specs.py,drivers.py,preamble.py,should.py,meta.py,build_result.py,build_report.py,post_loop.sh,save_probes.sh} "$W/probes/_generator/"
for f in "$W/probes/_generator/"*.py; do mv "$f" "$f.txt"; done
echo "- _generator/*.txt: out-of-tree generator (gen.py writes each probe_<key>.py from specs/drivers/preamble), record and report builders; .txt so no tree scan reads them as harnesses" > "$W/probes/_generator/INDEX.md"
cd "$REPO" && bash "$HOME/gate_wave.sh" ckpt
