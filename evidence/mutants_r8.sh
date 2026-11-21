#!/bin/bash
# round-8 mutants: one sed on the head's tests/entities.py in /root/wt; the reach driver runs the N-log-flood section
W=$1; cd /root/wt
run() { cp tests/entities.py $W/ent_orig.py; sed -i "$2" tests/entities.py
  if cmp -s tests/entities.py $W/ent_orig.py; then echo "$1 NO-OP (sed matched nothing)"; else
  echo "$1 $(timeout 220 python3 $W/ev/reach_drv.py tests/entities.py 2>&1 | grep -E '^(ok|FAIL)' | grep -E 'N-log-flood' | cut -c1-4 | tr '\n' ' ')(R10 flood, R11 reach)"; fi
  cp $W/ent_orig.py tests/entities.py; }
echo "UNMUTATED $(timeout 220 python3 $W/ev/reach_drv.py tests/entities.py 2>&1 | grep N-log-flood | cut -c1-4 | tr '\n' ' ')"
run M1_no_exception_critical 's/if call.func.attr in ("warning", "warn", "error", "exception", "critical", "fatal"):/if call.func.attr in ("warning", "warn", "error", "fatal"):/'
run M2_kw_level_unread 's/else next((k.value for k in call.keywords if k.arg == "level"), None))/else ast.Constant(10))/'
run M3_logger_attr_unreached 's/    reached = {"logging", "logger", "_LOGGER"}/    reached = {"logging", "_LOGGER"}/'
run M4_regex_no_logger 's/    names_one = re.compile(r"LOGGER|\[Ll\]ogger|logging")/    names_one = re.compile(r"LOGGER|logging")/'
run M5_files_unread 's/        if text_names_one(data):/        if False:/'
run M6_pickle_unread 's/^                    inner.append(arg)$/                    pass/'
run M7_warnings_refused 's/    reached = {"logging", "logger", "_LOGGER"}/    reached = {"logging", "logger", "_LOGGER", "warnings"}/'
run M8_escape_unrefused 's/            elif isinstance(node, ast.Name) and node.id == "_LOGGER" and isinstance(node.ctx, ast.Load):/            elif False:/'
run M9_handover_dropped '/("coordinator.py", "_LOGGER -> super().__init__"): 1,/d'
run M10_canonical_any 's/                canonical = id(node) in top and id(value) in canonical_values/                canonical = True/'
