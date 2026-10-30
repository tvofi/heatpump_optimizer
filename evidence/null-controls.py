import sys
from dataclasses import replace
from datetime import datetime
from heatpump_optimizer import away
from heatpump_optimizer.optimizer import OptimizationConfig
class T: dhw_min_temp=45.0; dhw_idle_min_temp=40.0
sat=datetime(2026,10,31,14)
def row(cfg, **kw):
    b,_=away.solve_bands(cfg,T(),away.AwayState(**kw)); c=replace(cfg,**b)
    return (c.get_comfort_temp(14,sat),c.get_comfort_temp(3,sat),c.target_temp,c.min_temp,
            c.comfort_temp_day_weekend,c.holiday_comfort_day,sorted(b))
wk=OptimizationConfig(comfort_temp_day_weekend=21.0,comfort_temp_night_weekend=19.5)
plain=OptimizationConfig()
for name,cfg in (("weekend",wk),("unconfigured",plain)):
  for k,kw in (("home",{"active":False}),("away16",{"active":True,"target_temperature":16.0}),
               ("away22",{"active":True,"target_temperature":22.0}),
               ("recovering",{"active":True,"recovery_active":True,"target_temperature":16.0})):
    print("RESULT",name,k,row(cfg,**kw))
