A=custom_components/heatpump_optimizer/accuracy.py
C=custom_components/heatpump_optimizer/coordinator.py
T=custom_components/heatpump_optimizer/thermal_model.py
S=custom_components/heatpump_optimizer/sensor.py
./run.sh base $A - - tests/features.py &
./run.sh m1 $A '        if follows is False:
            # #2262' '        if False:
            # #2262' tests/features.py &
./run.sh m5 $T 'return self.electric_counter if self.heat_counter else self.measured_power' 'return self.measured_power' tests/features.py &
./run.sh m7 $A '    if measured_heat:
        return COP_HEAT_METERED' '    if False:
        return COP_HEAT_METERED' tests/features.py &
wait
./run.sh m3 $A ' or utc_elapsed_seconds(self.at, since) <= 0.0:' ':' tests/features.py &
./run.sh m2 $C 'pending["split"], ctx._thermal_params' 'self._commanded_split(), ctx._thermal_params' tests/features.py &
./run.sh m8 $A 'return 0.05 <= elapsed_h <= 2.0' 'return 0.0 <= elapsed_h <= 2.0' tests/features.py &
./run.sh m9 $A ' or (raw.get("at") is not None and at is None):' ':' tests/features.py &
wait
./run.sh m4 $S 'if data.get("cop_observability") == COP_NOT_MEASURABLE:' 'if False:' tests/entities.py &
./run.sh m10 $C '            if pairs_interval(elapsed):' '            if True:' tests/features.py &
./run.sh m6 $A '        self.at = at' '        pass' tests/features.py &
wait
echo ALLDONE > /home/user/mut/done
