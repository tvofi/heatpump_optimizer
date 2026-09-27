import sys, os, time
root=sys.argv[1]; os.chdir(root); sys.path[:0]=[root+'/tests', root+'/tests/hastub', root]
import golden
import heatpump_optimizer.optimizer as O
n=[0]; orig=O.HeatPumpOptimizer.optimize
objs=[]
def wrap(self,*a,**k):
    r=orig(self,*a,**k); objs.append(float(r.objective_value)); return r
O.HeatPumpOptimizer.optimize=wrap
for name in sys.argv[2:]:
    objs.clear(); t=time.process_time(); golden.capture(name, golden.SCENARIOS[name]); dt=time.process_time()-t
    print(root[-8:], name, 'objective', [round(x,4) for x in objs], 'cpu_s', round(dt,1))
