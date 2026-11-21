#!/bin/bash
# each mutant: one sed on a copy of the head's tests/entities.py, run the reach driver
W=$1; cd $W/wt
run() { cp tests/entities.py $W/ent_orig.py; sed -i "$2" tests/entities.py
  if cmp -s tests/entities.py $W/ent_orig.py; then echo "$1 NO-OP (sed matched nothing)"; else
  echo "$1 $(timeout 220 python3 $W/ev/reach_drv.py tests/entities.py 2>&1 | grep 'R11 N-log-flood barrier reach' | cut -c1-4)"; fi
  cp $W/ent_orig.py tests/entities.py; }
run M1_const_arm_off 's/                if text_names_one(node.value):/                if False:/'
run M2_file_arm_off 's/        if text_names_one(data):/        if False:/'
run M3_no_recursion 's/        return any(v != value and text_names_one(v) for v in inner)/        return False/'
run M4_regex_narrow 's/names_one = re.compile(r"LOGGER|\[Ll\]ogger|logging|warnings")/names_one = re.compile(r"_LOGGER")/'
run M5_genops_off 's/            for _op, arg, _pos in pickletools.genops(io.BytesIO(/            for _op, arg, _pos in ()(io.BytesIO(/'
run M6_shipped_untracked 's/    return {p: (pkg \/ p).read_bytes() for p in sorted(tracked)/    tracked = [str(q.relative_to(pkg)) for q in pkg.rglob("*")]\n    return {p: (pkg \/ p).read_bytes() for p in sorted(tracked)/'
