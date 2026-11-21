#!/bin/bash
# round-7 mutants: one sed on a copy of the head's tests/entities.py; the reach driver runs the N-log-flood section
W=$1; cd /root/wt
run() { cp tests/entities.py $W/ent_orig.py; sed -i "$2" tests/entities.py
  if cmp -s tests/entities.py $W/ent_orig.py; then echo "$1 NO-OP (sed matched nothing)"; else
  echo "$1 $(timeout 220 python3 $W/ev/reach_drv.py tests/entities.py 2>&1 | grep 'R11 N-log-flood barrier reach' | cut -c1-4)"; fi
  cp $W/ent_orig.py tests/entities.py; }
echo "UNMUTATED"; timeout 220 python3 $W/ev/reach_drv.py tests/entities.py 2>&1 | cut -c1-200
run N1_handlers_not_reached 's/    reached = {"logging", "logger", "_LOGGER", "warnings"} | handlers/    reached = {"logging", "logger", "_LOGGER", "warnings"}/'
run N2_regex_no_handlers 's/names_one = re.compile(r"LOGGER|\[Ll\]ogger|logging|warnings|(call|default)_exception_handler")/names_one = re.compile(r"LOGGER|[Ll]ogger|logging|warnings")/'
run N3_only_call_handler 's/    handlers = {"call_exception_handler", "default_exception_handler"}/    handlers = {"call_exception_handler"}/'
run N4_residue_extra 's/_R11_LOOP_LOGGING_RESIDUE = {"_run_once", /_R11_LOOP_LOGGING_RESIDUE = {"_run_once", "run_forever", /'
run N5_residue_drop 's/_R11_LOOP_LOGGING_RESIDUE = {"_run_once", "_stop_serving", /_R11_LOOP_LOGGING_RESIDUE = {"_stop_serving", /'
run N6_census_blind 's/    if re.search(r"\\blogger\\.(warning|error|exception|critical|log)\\b", src)/    if False/'
