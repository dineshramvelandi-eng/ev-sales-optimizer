import streamlit as st
import pandas as pd
import plotly.express as px
from core.io import load_all_datasets
from core.optimize import greedy_reallocate
from core.state import remember_optimizer

st.title("Inventory Optimizer")
eri, hist, branches, inv, crm, webs = load_all_datasets(prefer_real=True)

# --- read forecast context from session_state ---
sel = st.session_state.sel_counties
fc_next = st.session_state.forecast_next  # next-month per county with expected_dealer_units
if not sel or fc_next is None or inv is None or branches is None:
    st.info("Tip: set forecasts first and click 'Use these forecasts in Inventory Optimizer'.")
    st.stop()

st.caption(f"Using **Forecasts** for: {', '.join(sel)} — target units (next month): "
           f"**{int(fc_next['expected_dealer_units'].sum())}**")

# Controls
c1, c2, c3, c4 = st.columns(4)
min_safety   = c1.number_input("Min safety stock / (branch, model)", 0, 50, 2, 1)
max_transfer = c2.number_input("Max transfer distance (km)", 0, 1000, 250, 10)
max_batch    = c3.number_input("Max batch size per transfer", 1, 100, 10, 1)
trans_cost   = c4.number_input("Transfer cost per unit (€)", 0, 1000, st.session_state.transfer_cost_per_unit, 10)

# Visual stock
invb = inv.merge(branches[['branch_id','branch_name','county']], on='branch_id', how='left')
fig = px.bar(invb, x='branch_name', y='stock_units', color='model', barmode='group',
             title="Current Stock by Branch & Model", hover_data=['county'])
st.plotly_chart(fig, use_container_width=True)

# --- compute needs from forecast next-month, by county ---
needs_by_county = fc_next[['county','expected_dealer_units']].groupby('county', as_index=False).sum()
local_stock = invb.groupby('county', as_index=False)['stock_units'].sum().rename(columns={'stock_units':'local_stock'})
gap = needs_by_county.merge(local_stock, on='county', how='left').fillna({'local_stock':0})
gap['shortfall'] = (gap['expected_dealer_units'] - gap['local_stock']).astype(int)

st.subheader("Demand vs Local Stock (next month)")
st.dataframe(gap.sort_values('shortfall', ascending=False), use_container_width=True)

# --- reallocation plan (branch-level), still uses greedy_reallocate you already have ---
plan = greedy_reallocate(inv, branches, min_safety, max_transfer, max_batch, trans_cost)

st.subheader("Proposed Reallocation Plan")
st.dataframe(plan, use_container_width=True)

cA, cB = st.columns([0.6, 0.4])
with cA:
    if st.button("✅ Use this plan in Revenue Simulator"):
        remember_optimizer(plan, trans_cost)
        st.success(f"Saved. Transfer units: {int(plan['units'].sum()) if not plan.empty else 0}")
with cB:
    st.download_button("Download Plan (CSV)",
        plan.to_csv(index=False).encode('utf-8'),
        file_name="Reallocation_Plan.csv", mime="text/csv")
