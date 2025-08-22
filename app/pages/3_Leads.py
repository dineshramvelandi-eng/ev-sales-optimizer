import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from core.io import load_all_datasets
from core.scoring import score_leads

st.title("Leads")
eri, hist, branches, inv, crm, webs = load_all_datasets(prefer_real=True)

if crm is None or eri is None:
    st.error("Missing CRM or EV_Readiness_Index.")
    st.stop()

# Score everything
scored = score_leads(crm, eri)
st.caption(f"Leads scored: {len(scored)}")

# ----------- Dynamic filter choices (avoid label mismatch) -----------
# Clean up strings a bit
for col in ["current_vehicle_type", "income_band", "county"]:
    if col in scored.columns:
        scored[col] = scored[col].astype(str).str.strip()

veh_types = sorted(scored["current_vehicle_type"].dropna().unique().tolist())
income_opts = sorted(scored["income_band"].dropna().unique().tolist())

# Sensible default threshold = 75th percentile
thresh_default = int(np.percentile(scored["score"], 75))

c1, c2, c3, c4 = st.columns(4)
with c1:
    thresh = st.slider("Score ≥", 0, 100, thresh_default, 1)
with c2:
    vt = st.multiselect("Vehicle type", veh_types, default=veh_types)
with c3:
    inc = st.multiselect("Income band", income_opts, default=income_opts)
with c4:
    max_dist = st.number_input("Max distance (km, optional)", min_value=0, value=0, step=5)

# Apply filters
f = scored[
    (scored["score"] >= thresh) &
    (scored["current_vehicle_type"].isin(vt)) &
    (scored["income_band"].isin(inc))
].copy()
if max_dist > 0:
    f = f[f["distance_km"] <= max_dist]

st.write(f"Showing {len(f)} leads.")

# ----------- Charts & table -----------
fig = px.histogram(scored, x="score", nbins=20, title="Score Distribution (all leads)")
st.plotly_chart(fig, use_container_width=True)

cols = ["lead_id","first_name","last_name","county","score",
        "current_vehicle_type","income_band","engagements_90d","distance_km"]
st.dataframe(
    f[cols].sort_values(["score","engagements_90d"], ascending=[False, False]),
    use_container_width=True
)

# Export CSV
csv = f[cols].to_csv(index=False).encode("utf-8")
st.download_button("Download Call List (CSV)", data=csv, file_name="Call_List.csv", mime="text/csv")
