import sys,re
d,m=sys.argv[1],sys.argv[2]
p=f"{d}/custom_components/heatpump_optimizer/coordinator.py"
s=open(p).read()
def rep(a,b):
    global s
    assert s.count(a)==1,(m,a,s.count(a)); s=s.replace(a,b)
save="        if save:\n            await self._async_save_thermal_learning()\n"
if m=="M1":
    rep(save,"")
    rep("        self._measured_cop = MeasuredCop.from_dict(stored.get(\"measured_cop\"))\n",
        save+"        self._measured_cop = MeasuredCop.from_dict(stored.get(\"measured_cop\"))\n")
elif m=="M2":
    rep("for store in (*_restored_stores(self), self._snapshot_store):","for store in _restored_stores(self):")
elif m=="M3":
    rep("            self._load_scalar_learners(thermal)  # the loader's parser: sample counts roll back too\n",
        "            for setter, key in ((self._apply_buffer_cooling_rate, 'buffer_cooling_rate'),(self._apply_house_heat_loss_scale, 'house_heat_loss_scale'),(self._apply_lower_floor_loss_ratio, 'lower_floor_loss_ratio'),(self._apply_cop_scale, _COP_STORE_KEY)):\n                if (value := finite_float(thermal.get(key))) is not None:\n                    setter(value)\n")
elif m=="M4":
    rep("self._cop_samples) = (c if v is None else v for v, c in zip(n, cur))","self._cop_samples) = cur")
elif m=="M5":
    rep("self._cop_samples) = (c if v is None else v for v, c in zip(n, cur))","self._cop_samples) = (v for v, c in zip(n, cur))")
elif m=="M6":  # drop cop row from parser
    rep("            (_COP_STORE_KEY, \"cop_samples\", self._apply_cop_scale))]","            )]\n        n.append(None)")
elif m=="NULL": pass
open(p,"w").write(s)
