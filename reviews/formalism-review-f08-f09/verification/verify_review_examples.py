#!/usr/bin/env python3
"""Independent, bounded review examples. Does not import or certify F08/F09."""
from __future__ import annotations
import datetime as dt
import itertools
import json
import math
from pathlib import Path
import platform
import numpy as np
import scipy
from scipy.optimize import linprog


def require(ok, msg):
    if not bool(ok): raise AssertionError(msg)


def near(x, y, tol=1e-9):
    require(np.allclose(x, y, atol=tol, rtol=tol), f"{x!r} != {y!r}")


def mi(p):
    p = np.asarray(p, float)
    px, py = p.sum(axis=1), p.sum(axis=0)
    return float(sum(p[i,j]*math.log2(p[i,j]/(px[i]*py[j]))
                     for i,j in np.ndindex(p.shape) if p[i,j]>0))


def imin_pid(p):
    # p[x1,x2,target]. Specific information = KL(p(source|target)||p(source)).
    p = np.asarray(p, float)
    require(p.ndim==3 and (p>=0).all(), "invalid distribution")
    near(p.sum(), 1)
    py = p.sum(axis=(0,1))
    pairs = [p.sum(axis=1),p.sum(axis=0)]
    specs = []
    for pair in pairs:
        px = pair.sum(axis=1)
        out = []
        for t in range(len(py)):
            if py[t]==0: out.append(0); continue
            cond = pair[:,t]/py[t]
            out.append(sum(q*math.log2(q/px[i]) for i,q in enumerate(cond) if q>0))
        specs.append(np.asarray(out))
    red = float(py @ np.minimum(*specs))
    i1,i2 = map(mi,pairs)
    joint = mi(p.reshape(-1,len(py)))
    return np.array([red,i1-red,i2-red,joint-i1-i2+red]), joint


def gate(f, targets=2):
    p=np.zeros((2,2,targets))
    for a,b in itertools.product(range(2),repeat=2):p[a,b,f(a,b)]=.25
    return p


def r01_pid_canonical_cases():
    cases={"UNIQUE":gate(lambda a,b:a),"XOR":gate(lambda a,b:a^b),
           "AND":gate(lambda a,b:a&b)}
    cp=np.zeros((2,2,2));cp[0,0,0]=cp[1,1,1]=.5;cases["REDUNDANT_COPY"]=cp
    vals={k:imin_pid(p)[0].tolist() for k,p in cases.items()}
    near(vals["UNIQUE"],[0,1,0,0]);near(vals["XOR"],[0,0,0,1])
    near(vals["REDUNDANT_COPY"],[1,0,0,0])
    near(vals["AND"],[.31127812445913283,0,0,.5])
    return {"atom_order":["redundancy","unique1","unique2","synergy"],"atoms":vals}


def r02_two_bit_copy():
    atoms,total=imin_pid(gate(lambda a,b:2*a+b,targets=4))
    near(atoms,[1,0,0,1]);near(total,2)
    # A common Blackwell output must obey alpha[a]=beta[b] for all four pairs.
    mat=np.zeros((4,4))
    for row,(a,b) in enumerate(itertools.product(range(2),repeat=2)):
        mat[row,a]=1;mat[row,2+b]=-1
    require(np.linalg.matrix_rank(mat)==3,"only constant common channel survives")
    near(mat@np.ones(4),0)
    return {"I_min_atoms":atoms.tolist(),"total_bits":total,"Blackwell_redundancy_bits":0,
            "common_channel_nullity":1}


def r03_gemini_rb_formula_and_countercase():
    p=gate(lambda a,b:a&b)
    ch1=p.sum(axis=1);ch2=p.sum(axis=0)
    # Both source channels given target are identical: Blackwell lower and upper coincide.
    near(ch1,ch2)
    blackwell=mi(ch1)
    # Gemini's two conditional independence requirements force q00=q01=q10=q11.
    mat=np.array([[1,-1,0,0],[0,0,1,-1],[1,0,-1,0],[0,1,0,-1]],float)
    require(np.linalg.matrix_rank(mat)==3,"connected full-support source grid")
    near(blackwell,.31127812445913283)
    return {"AND_Blackwell_bits":blackwell,"Gemini_common_sample_constraint_bits":0,
            "scope":"counterexample to the Gemini formula, not a test of unavailable F09"}


def r04_rb_not_generic_convex_maximization():
    identity=np.array([[.5,0],[0,.5]])
    flip=np.array([[0,.5],[.5,0]])
    vals=[mi(identity),mi(flip),mi((identity+flip)/2)]
    near(vals,[1,1,0])
    require(vals[2] < (vals[0]+vals[1])/2,"objective not concave in channel")
    return {"endpoint_objectives":vals[:2],"mixture_objective":vals[2],
            "scope":"identical sources, feasible RB(0) channels; no universal LP guarantee"}


CONTEXTS=list(itertools.product(range(2),repeat=2))
ASSIGNMENTS=list(itertools.product(range(2),repeat=4)) # A0,A1,B0,B1
ROWS=[(a,b,x,y) for a,b in CONTEXTS for x,y in itertools.product(range(2),repeat=2)]
INC=np.array([[int(g[a]==x and g[2+b]==y) for g in ASSIGNMENTS] for a,b,x,y in ROWS],float)


def validate_empirical(p):
    require(p.shape==(2,2,2,2) and np.isfinite(p).all() and (p>=0).all(),"invalid table")
    near(p.sum(axis=(2,3)),np.ones((2,2)))
    for a in range(2):
        near(p[a,0].sum(axis=1),p[a,1].sum(axis=1))
    for b in range(2):
        near(p[0,b].sum(axis=0),p[1,b].sum(axis=0))


def cf(p):
    validate_empirical(p)
    observed=np.array([p[a,b,x,y] for a,b,x,y in ROWS])
    result=linprog(-np.ones(16),A_ub=INC,b_ub=observed,bounds=(0,None),method="highs")
    require(result.success,"CF linear program failed")
    require(np.max(INC@result.x-observed)<1e-8,"LP feasibility")
    return float(1-result.x.sum())


def prbox():
    p=np.zeros((2,2,2,2))
    for a,b,x,y in ROWS:p[a,b,x,y]=.5 if (x^y)==a*b else 0
    return p


def r05_cf_reference_tables():
    white=np.full((2,2,2,2),.25)
    vals={}
    for v in [0,.25,.5,.625,.75,1.]:
        val=cf(v*prbox()+(1-v)*white)
        near(val,max(0,2*v-1));vals[str(v)]=val
    rng=np.random.default_rng(3219)
    dist=rng.uniform(size=16);dist/=dist.sum()
    classical=(INC@dist).reshape(2,2,2,2)
    near(cf(classical),0)
    return {"PR_visibility_to_CF":vals,"global_distribution_CF":cf(classical),
            "note":"CF=.25 is one declared toy table, not the unavailable project's CHSH table"}


def r06_inconsistent_marginals_rejected():
    p=np.full((2,2,2,2),.25)
    p[0,0]=np.array([[1.,0],[0,0]])
    try:cf(p)
    except AssertionError:return {"rejected":True,"reason":"same A0 has different marginals across B contexts"}
    raise AssertionError("disturbing data accepted as nondisturbing CF case")


def r07_controllability_and_viability():
    # Full-rank scalar xdot=x+u, |u|<=.25, K=[-1,1], upper boundary outward.
    require(np.linalg.matrix_rank(np.array([[1.]]))==1,"full Kalman rank")
    minimum_boundary_drift=1-.25
    require(minimum_boundary_drift>0,"upper safe boundary cannot be held")
    # No actuation, xdot=-x: K is invariant although controllability rank is zero.
    require(np.linalg.matrix_rank(np.array([[0.]]))==0,"no control")
    require(-1<0 and 1>0,"opposite boundaries point inwards")
    return {"full_rank_min_outward_drift":minimum_boundary_drift,
            "rank_zero_safe_solution":"x(t)=x(0)*exp(-t), |x(0)|<=1"}


def r08_topology_not_control_cost():
    # xdot=b*u, x(0)=0, x(T)=1: Cauchy-Schwarz gives minimum effort=1/(b*b*T).
    T=1.
    costs={}
    for b in [1.,.1]:
        u=1/(b*T)
        near(b*u*T,1)
        costs[str(b)]=u*u*T
    near(costs["0.1"]/costs["1.0"],100)
    return {"same_zero_pattern_min_integral_u_squared":costs,"physical_energy_claimed":False}


def r09_information_and_common_action():
    # L,R safe; D unsafe. The two safe states look identical to the coarse observer.
    pa=np.array([[1,0,0],[0,0,1],[0,0,1]],float)
    pb=np.array([[0,0,1],[0,1,0],[0,0,1]],float)
    c=np.array([[1,0],[1,0],[0,1]],float)
    average=(pa+pb)/2
    q=np.array([[.5,.5],[0,1]])
    near(average@c,c@q)
    safe_actions=[{i for i,p in enumerate([pa,pb]) if p[s,2]==0} for s in [0,1]]
    require(all(safe_actions),"each microstate has a safe action")
    require(not set.intersection(*safe_actions),"no common safe action with coarse information")
    return {"policy_averaged_closure_error":float(np.max(abs(average@c-c@q))),
            "micro_safe_actions":[sorted(s) for s in safe_actions],"coarse_common_safe_actions":[]}


def r10_shared_budget_partial_observation():
    # Two-buffer variant: r=1, e=.2, W=.7, k=.1, U=.6, b=0.
    demands=[]
    for x in [np.array([0.,1.]),np.array([1.,0.])]:
        uncontrolled=-(x-.2)-.7+.1*(x[::-1]-x)
        lower=np.array([max(0,-uncontrolled[i]) if x[i]==0 else 0 for i in range(2)])
        require(lower.sum()<=.6,"known microstate admits inward boundary action")
        demands.append(lower)
    common=np.maximum(*demands)
    near(common,[.4,.4]);require(common.sum()>.6,"sum observation hides conflicting allocations")
    return {"statewise_boundary_demands":[a.tolist() for a in demands],
            "common_requirement":common.tolist(),"available":.6,
            "scope":"instantaneous boundary feasibility, not an entire viability kernel"}


def r11_open_heat_balance():
    T=np.array([300.,310.]);C=np.array([2.,3.]);powers=np.array([-100.,-100.]);k=1.
    j=k*(T[1]-T[0])
    dT=(np.array([j,-j])+powers)/C
    dE=C@dT
    dS=(C/T)@dT
    internal=k*(T[0]-T[1])**2/(T[0]*T[1])
    entropyflow=(powers/T).sum()
    near(dE,powers.sum());near(dS,internal+entropyflow)
    require(internal>=0 and dS<0,"open-system entropy can fall")
    reservoir_change=(-powers/200).sum()
    require(dS+reservoir_change>0,"combined entropy production positive")
    return {"energy_rate_W":float(dE),"system_entropy_rate_W_per_K":float(dS),
            "internal_entropy_production_W_per_K":float(internal),
            "combined_entropy_rate_W_per_K":float(dS+reservoir_change)}


def main():
    results=[]
    for name,fn in sorted(globals().items()):
        if name.startswith("r") and name[1:3].isdigit() and callable(fn):
            try:results.append({"id":name,"status":"passed","evidence":fn()})
            except Exception as exc:results.append({"id":name,"status":"failed","error":str(exc)})
    passed=sum(r['status']=='passed' for r in results)
    report={"scope":"independent review examples; not a reproduction of F08/F09",
            "timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,
            "passed":passed,"total":len(results),"results":results}
    Path(__file__).with_name('review_results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(f"{passed}/{len(results)} independent review checks passed")
    for r in results:
        if r['status']=='failed':print(r)
    raise SystemExit(passed!=len(results))


if __name__=='__main__':main()
