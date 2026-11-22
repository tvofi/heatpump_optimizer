import _sysid_lib as L, numpy as np
from custom_components.heatpump_optimizer import sysid
M = {}
def mk(line, old, new): return L.mutant_identify(line, old, new)
muts = {
 'b8d5_1942': (1942,"        if len(rows) < 5:","        if False:"),
 '756f_1974': (1974,"        prior_sd = 0.5 / max(self.config.thermal_mass_prior, 0.1)","        prior_sd = 0.5 / (self.config.thermal_mass_prior)"),
 '3918_1979': (1979,"            dof = max(len(rows) - n_cols, 1)","            dof = (len(rows) - n_cols)"),
 '8437_2010': (2010,"        k_hat = max(float(pass1[0]), 0.0)","        k_hat = (float(pass1[0]))"),
 '20f7_2018': (2018,"                if h_prev <= 1e-6:","                if False:"),
 '50da_2018': (2018,"                if h_prev <= 1e-6:","                if h_prev < 1e-6:"),
 '4eeb_2032': (2032,"        if len(d2_all) >= 3:","        if len(d2_all) > 3:"),
 'a9bc_2037': (2037,"        x1_spread2 = float(np.var(a[:, 0])) * n_rows / max(n_rows - 1.0, 1.0)","        x1_spread2 = float(np.var(a[:, 0])) * n_rows / (n_rows - 1.0)"),
 '44bb_2038': (2038,"        if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0:","        if sigma2 > 0.0 and sigma2 >= x1_spread2 / 9.0:"),
 'b97b_2038': (2038,"        if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0:","        if sigma2 >= 0.0 and sigma2 > x1_spread2 / 9.0:"),
 '6b6a_2068': (2068,"        if sigma2 > 0.0:","        if sigma2 >= 0.0:"),
 '1066_2114': (2114,"            if rank < 2:","            if False:"),
 'd742_2114': (2114,"            if rank < 2:","            if rank <= 2:"),
 '0722_2126': (2126,"        if one_over_c <= 1e-6 or ua_over_c <= 1e-6:","        if False:"),
 '3e78_2126': (2126,"        if one_over_c <= 1e-6 or ua_over_c <= 1e-6:","        if one_over_c < 1e-6 or ua_over_c <= 1e-6:"),
 '87c3_2126': (2126,"        if one_over_c <= 1e-6 or ua_over_c <= 1e-6:","        if one_over_c <= 1e-6 or ua_over_c < 1e-6:"),
}
for k,v in muts.items(): M[k]=mk(*v)
# random battery
rng=np.random.default_rng(0)
cases=[]
for s in range(60):
    kw=dict(ua=float(rng.uniform(0.05,0.5)),cap=float(rng.uniform(1,20)),gains=float(rng.uniform(0,1)),noise=float(rng.choice([0,0.01,0.03,0.06,0.1,0.2])),dt_h=float(rng.choice([0.25,0.5,1.0])),drift=float(rng.choice([0,0.05,-0.05])),seed=s, q=(float(rng.uniform(0,4)),float(rng.uniform(2,8)),0.0))
    cases.append((f"r{s}",L.plant(**kw)))
for k,m in M.items():
    n=sum(repr(L.call(L.SI.identify,c[1]))!=repr(L.call(m,c[1])) for c in cases)
    print(k, "random-battery differs", n, "/", len(cases))
