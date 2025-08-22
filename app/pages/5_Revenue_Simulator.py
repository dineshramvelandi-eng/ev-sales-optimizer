import streamlit as st
import numpy as np
import plotly.graph_objects as go
from core.io import load_all_datasets
from core.revenue import simulate_uplift

st.title("Revenue Simulator")

# --- read context from session_state ---
plan_units   = st.session_state.plan_units or 0
transfer_units = st.session_state.transfer_units or 0
transfer_cost = st.session_state.transfer_cost_per_unit or 50

eri, hist, branches, inv, crm, webs = load_all_datasets(prefer_real=True)

# Inputs with sensible defaults from session
c1, c2, c3 = st.columns(3)
baseline_conv  = c1.slider("Baseline conversion rate", 0.0, 0.3, 0.05, 0.01)
available_leads= c2.number_input("Available leads", 0, 1_000_000, len(crm) if crm is not None else 2000, 50)
margin         = c3.number_input("Gross margin per unit (€)", 0, 20000, 5000, 100)

c4, c5, c6 = st.columns(3)
plan_units_in  = c4.number_input("Planned units (from Forecasts)", 0, 100000, int(plan_units), 10)
transfer_units_in = c5.number_input("Transfer units (from Optimizer)", 0, 100000, int(transfer_units), 1)
transfer_cost_in  = c6.number_input("Transfer cost per unit (€)", 0, 2000, int(transfer_cost), 10)

# Compute
res = simulate_uplift(baseline_conv, available_leads, plan_units_in, margin, transfer_units_in, transfer_cost_in)

# --- KPIs (nice, readable) ---
k1, k2, k3, k4 = st.columns(4, gap="medium")
k1.metric("Baseline units", int(res["baseline_units"]))
k2.metric("Plan units", int(plan_units_in))
k3.metric("Incremental units", int(res["delta_units"]))
k4.metric("€ Uplift (net)", f"{res['uplift_revenue']:.0f}")

st.divider()
st.subheader("Results (details)")
st.json(res)

# --- Better waterfall ---
baseline_rev = res["baseline_units"] * margin
uplift_rev   = (plan_units_in - res["baseline_units"]) * margin
total_trans_cost = transfer_units_in * transfer_cost_in
net_uplift = uplift_rev - total_trans_cost

fig = go.Figure(go.Waterfall(
    name="Revenue",
    orientation="v",
    measure=["absolute","relative","relative","total"],
    x=["Baseline revenue","Uplift from extra units","Transfer cost","Net revenue"],
    text=[f"€{baseline_rev:,.0f}", f"€{uplift_rev:,.0f}", f"-€{total_trans_cost:,.0f}", f"€{baseline_rev + net_uplift:,.0f}"],
    y=[baseline_rev, uplift_rev, -total_trans_cost, 0],
))
fig.update_layout(title="Revenue Impact Waterfall", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# Friendly summary
if net_uplift >= 0:
    st.success(f"✅ Plan is profitable: **€{net_uplift:,.0f}** net uplift at margin €{margin:,}/unit.")
else:
    st.warning(f"⚠️ Plan loses **€{-net_uplift:,.0f}**. Reduce transfer distance/cost or increase market share/α.")
