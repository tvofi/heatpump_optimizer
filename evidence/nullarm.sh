set -e
W=$(cat ~/W); cd $W/wt; P=$W/nullpkg; rm -rf $P; mkdir -p $P; cp -r custom_components $P/
{ printf 'import ast, json, sys\nfrom pathlib import Path\nclass _R:\n  def check(self,n,c,d): print("PASS" if c else "FAIL", n, "::", d)\nR=_R()\n'
  sed -n '/^_UXH_PKG = /,/^    f"reads keyed some other way/p' tests/entities.py; echo ")"; } > $W/uxh_arm.py
cd $P; H=custom_components/heatpump_optimizer
echo "== unperturbed"; python3 -I $W/uxh_arm.py
echo 'CONF_ZZ_PROBE_ENTITY = "zz_probe_entity"' >> $H/const.py
printf '\nfrom .const import CONF_ZZ_PROBE_ENTITY\ndef _zz(reader):\n    return reader.read(CONF_ZZ_PROBE_ENTITY)\n' >> $H/flow_lift.py
echo "== perturbed CONF_ZZ"; python3 -I $W/uxh_arm.py
git -C $W/wt show HEAD:$H/flow_lift.py > $H/flow_lift.py
printf '\ndef _yy(reader, k):\n    return reader.read(k["x"])\n' >> $H/flow_meter.py
echo "== perturbed k[x]"; python3 -I $W/uxh_arm.py
