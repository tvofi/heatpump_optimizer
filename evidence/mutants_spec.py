import json,sys
F="custom_components/heatpump_optimizer/dhw_learning.py"
M=[
("SETTLE_ARM_OFF","<= DHW_CHARGE_SETTLE_HOURS","<= 0.0"),
("SETTLE_SHORT","DHW_CHARGE_SETTLE_HOURS = 0.25","DHW_CHARGE_SETTLE_HOURS = 0.05"),
("SETTLE_LONG","DHW_CHARGE_SETTLE_HOURS = 0.25","DHW_CHARGE_SETTLE_HOURS = 0.5"),
("STAMP_DEL","            self.last_heated_time = now\n","            pass\n"),
("ZERO_DROP_OFF","0.0 if charge_affected else temp_drop","temp_drop"),
("USAGE_HEATING_ONLY","            charge_affected,\n            weekend=","            heating,\n            weekend="),
("COOLING_HEATING_ONLY","        if not charge_affected:\n","        if not heating:\n"),
("OVERFLOW_DROP","except (TypeError, ValueError, OverflowError):\n                self.daytype_samples[idx] = 0","except (TypeError, ValueError):\n                self.daytype_samples[idx] = 0"),
("RESTORE_SKIP_OFF","            else:\n                continue\n            try:","            else:\n                pass\n            try:"),
("RESTORE_LEN_OFF","if isinstance(arr, list) and len(arr) == 24:\n                setattr(self, key, self.normalize_profile(arr))","if isinstance(arr, list):\n                setattr(self, key, self.normalize_profile(arr))"),
("RESTORE_CLAMP_DROP","self.daytype_samples[idx] = max(0, int(source.get(f\"{key}_samples\", 0)))","self.daytype_samples[idx] = int(source.get(f\"{key}_samples\", 0))"),
# reviewer's own
("R_SINCE_ARM_OFF","charge_affected = self.heating_since_sample or heating or (","charge_affected = heating or ("),
("R_STAMP_ALWAYS","        if heating:\n            self.last_heated_time = now\n","        if True:\n            self.last_heated_time = now\n"),
("R_FOLD_SKIP","        await self.async_fold_draw_stats(\n            now, previous_temp, 0.0 if charge_affected else temp_drop, dt_h\n        )","        if not charge_affected:\n            await self.async_fold_draw_stats(\n                now, previous_temp, temp_drop, dt_h\n            )"),
("R_SETTLE_STRICT","            <= DHW_CHARGE_SETTLE_HOURS\n","            < DHW_CHARGE_SETTLE_HOURS\n"),
("R_STAMP_PREV","            self.last_heated_time = now\n","            self.last_heated_time = previous_time\n"),
]
json.dump([dict(name=n,file=F,old=o,new=w) for n,o,w in M],open(sys.argv[1],"w"),indent=1)
