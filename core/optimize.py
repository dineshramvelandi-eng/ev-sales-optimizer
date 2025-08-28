import pandas as pd
import numpy as np



def _county_distance(c1: str, c2: str) -> float:
    return 0.0 if c1 == c2 else 200.0

def greedy_reallocate(inv: pd.DataFrame, branches: pd.DataFrame, min_safety: int, max_distance: float, max_batch: int, transfer_cost_per_unit: float) -> pd.DataFrame:
    # Merge branch county
    inv2 = inv.merge(branches[['branch_id','county']], on='branch_id', how='left', suffixes=('','_branch'))
    # Compute surplus and shortfall by (branch_id, model)
    grp = inv2.groupby(['branch_id','county','model'], as_index=False)['stock_units'].sum()

    # Heuristic: branches with stock_units > min_safety are sources, stock_units < min_safety are sinks
    sources = grp[grp['stock_units'] > min_safety].copy()
    sinks = grp[grp['stock_units'] < min_safety].copy()
    if sources.empty or sinks.empty:
        return pd.DataFrame(columns=['from_branch','to_branch','model','units','distance_km','transfer_cost','note'])

    plan = []
    for _, s in sinks.iterrows():
        need = min_safety - s['stock_units']
        if need <= 0:
            continue
        # find candidate sources for same model
        cand = sources[(sources['model']==s['model']) & (sources['stock_units'] > min_safety)].copy()
        # sort by proximity
        cand['dist'] = cand.apply(lambda r: _county_distance(r['county'], s['county']), axis=1)
        cand = cand.sort_values('dist')
        for _, src in cand.iterrows():
            if need <= 0: break
            if src['dist'] > max_distance: continue
            surplus = src['stock_units'] - min_safety
            if surplus <= 0: continue
            move = int(min(surplus, need, max_batch))
            if move <= 0: continue
            plan.append({
                'from_branch': src['branch_id'],
                'to_branch': s['branch_id'],
                'model': s['model'],
                'units': move,
                'distance_km': src['dist'],
                'transfer_cost': move * transfer_cost_per_unit,
                'note': 'greedy'
            })
            # update bookkeeping
            need -= move
            idx = (sources['branch_id']==src['branch_id']) & (sources['model']==src['model'])
            sources.loc[idx, 'stock_units'] -= move

    return pd.DataFrame(plan)
