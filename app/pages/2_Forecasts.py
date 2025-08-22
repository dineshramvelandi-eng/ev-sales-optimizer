import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from core.io import load_all_datasets
from core.forecast import make_county_forecasts
from core.state import remember_forecast

st.title("Forecasts")

# --------- Load data ---------
eri, hist, branches, inv, crm, webs = load_all_datasets(prefer_real=True)
if hist is None or eri is None:
    st.error("Missing Historical_Registrations or EV_Readiness_Index.")
    st.stop()

# --------- CONTROLS (stateful & robust) ---------
counties_all = sorted(hist["county"].unique().tolist())
default_sel = st.session_state.get("sel_counties", []) or (counties_all[:6] if len(counties_all) >= 6 else counties_all)
alpha_default = float(st.session_state.get("alpha", 0.10))
share_default = float(st.session_state.get("market_share", 0.15))

c1, c2, c3 = st.columns([0.45, 0.28, 0.27])
sel   = c1.multiselect("Counties", counties_all, default=default_sel, key="__fc_sel")
alpha = c2.slider("Readiness impact (α)", 0.0, 0.25, alpha_default, 0.01, key="__fc_alpha")
share = c3.slider("Target dealer market share", 0.0, 0.5,  share_default, 0.01, key="__fc_share")

if not sel:
    st.info("Select at least one county.")
    st.stop()

# --------- BUILD FORECASTS ---------
fc = make_county_forecasts(hist, eri, sel, alpha, share).copy()
if fc.empty:
    st.warning("Not enough history to forecast the selected counties.")
    st.stop()

fc["period_dt"] = pd.to_datetime(fc["period"], format="%Y-%m")
next_month = fc["period_dt"].min()
fc_next = fc[fc["period_dt"] == next_month].copy()

# Growth vs last actual month
hist2 = hist[hist["county"].isin(sel)].copy()
hist2["period_dt"] = pd.to_datetime(hist2["period"], format="%Y-%m")
last_hist_month = hist2["period_dt"].max()
last_hist = hist2[hist2["period_dt"] == last_hist_month][["county", "ev_units"]].rename(columns={"ev_units": "last_actual"})
fc_next = fc_next.merge(last_hist, on="county", how="left")
fc_next["growth_vs_last_m"] = ((fc_next["forecast_adj"] - fc_next["last_actual"]) /
                               (fc_next["last_actual"].replace(0, np.nan))).replace([np.inf, -np.inf], np.nan) * 100

# --------- KPIs ---------
k1, k2, k3 = st.columns(3, gap="medium")
with k1:
    st.metric("Next‑month expected dealer units", int(fc_next["expected_dealer_units"].sum()))
with k2:
    top_row = fc_next.sort_values("expected_dealer_units", ascending=False).head(1)
    top_label = f"{top_row['county'].iloc[0]} ({int(top_row['expected_dealer_units'].iloc[0])})" if len(top_row) else "–"
    st.metric("Top county (expected units)", top_label)
with k3:
    med_growth = np.nanmedian(fc_next["growth_vs_last_m"].values) if len(fc_next) else 0
    st.metric("Median growth vs last month", f"{med_growth:.1f}%")

st.divider()

# --------- Opportunities: demand vs local stock (shortfall) ---------
st.subheader("Opportunities: next‑month demand vs local stock (shortfall)")
if (inv is not None) and (branches is not None):
    invb = inv.merge(branches[["branch_id", "county"]], on="branch_id", how="left")
    local_stock = invb.groupby("county", as_index=False)["stock_units"].sum().rename(columns={"stock_units": "local_stock"})
else:
    local_stock = pd.DataFrame({"county": sel, "local_stock": 0})

opp = fc_next[["county", "expected_dealer_units"]].merge(local_stock, on="county", how="left")
opp["local_stock"] = opp["local_stock"].fillna(0)
opp["shortfall_units"] = (opp["expected_dealer_units"] - opp["local_stock"]).astype(int)

opp_sorted = opp.sort_values(["shortfall_units", "expected_dealer_units"], ascending=[False, False])
fig_bar = px.bar(
    opp_sorted,
    x="county",
    y=["expected_dealer_units", "local_stock"],
    barmode="group",
    title="Expected dealer demand vs local stock (next month)",
    labels={"value": "Units", "variable": ""}
)
st.plotly_chart(fig_bar, use_container_width=True)
st.caption("Shortfall = expected dealer units − local stock. Use the Inventory Optimizer to plan transfers.")

# --------- Trend small‑multiples ---------
st.subheader("Trend (per county)")
show_norm = st.toggle("Normalise each county to 0–1 (compare shape, not volume)", value=False)

trend = fc.sort_values(["county", "period_dt"])
if show_norm:
    trend["norm_adj"] = trend.groupby("county")["forecast_adj"].transform(lambda s: (s - s.min()) / (s.max() - s.min() + 1e-9))
    fig_sm = px.line(
        trend, x="period_dt", y="norm_adj", color="county",
        facet_col="county", facet_col_wrap=3, height=500, markers=True,
        title="Normalised adjusted forecast (shape only)"
    )
else:
    fig_sm = px.line(
        trend, x="period_dt", y="forecast_adj", color="county",
        facet_col="county", facet_col_wrap=3, height=500, markers=True,
        title="Adjusted forecast (α applied) — small multiples"
    )
fig_sm.update_xaxes(title="period")
fig_sm.update_yaxes(matches=None)
st.plotly_chart(fig_sm, use_container_width=True)

# --------- Table + Export ---------
st.subheader("Forecast table")
show_cols = ["county", "period", "forecast", "forecast_adj", "expected_dealer_units"]
st.dataframe(fc[show_cols].sort_values(["county", "period"]), use_container_width=True)
st.download_button(
    "Download Forecast CSV",
    fc[show_cols].to_csv(index=False).encode("utf-8"),
    file_name="Forecasts.csv",
    mime="text/csv"
)

# --------- HAND‑OFF to Optimizer (persist in session) ---------
cA, cB = st.columns([0.6, 0.4])
with cA:
    if st.button("✅ Use these forecasts in Inventory Optimizer"):
        remember_forecast(sel, alpha, share, fc, fc_next)
        st.success("Saved to session. Open the Inventory Optimizer tab ➜")
with cB:
    st.caption(f"Next‑month expected dealer units saved: **{int(fc_next['expected_dealer_units'].sum())}**")
