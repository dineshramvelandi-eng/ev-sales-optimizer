import streamlit as st
import pandas as pd
import plotly.express as px
from core.io import load_all_datasets

st.title("Overview")

eri, hist, branches, inv, crm, webs = load_all_datasets(prefer_real=True)


st.markdown("""
<style>
.kpi > div { background:#111827; border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:14px; }
</style>
""", unsafe_allow_html=True)


# ---- KPIs ----
k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    st.markdown('<div class="kpi">', unsafe_allow_html=True)
    st.metric("Counties", len(eri['county'].unique()) if eri is not None else 0)
    st.markdown('</div>', unsafe_allow_html=True)

with k2:
    st.markdown('<div class="kpi">', unsafe_allow_html=True)
    st.metric("Total Leads", len(crm) if crm is not None else 0)
    st.markdown('</div>', unsafe_allow_html=True)

with k3:
    st.markdown('<div class="kpi">', unsafe_allow_html=True)
    st.metric("Total Stock Units", int(inv['stock_units'].sum()) if inv is not None else 0)
    st.markdown('</div>', unsafe_allow_html=True)

with k4:
    st.markdown('<div class="kpi">', unsafe_allow_html=True)
    st.metric("Branches", len(branches) if branches is not None else 0)
    st.markdown('</div>', unsafe_allow_html=True)


st.write("")

# ---- Readiness by county (bar) + filter ----
st.subheader("EV Readiness by County")
if eri is not None:
    sel = st.multiselect("Filter counties (optional)", sorted(eri['county'].unique().tolist()))
    eri_plot = eri if not sel else eri[eri['county'].isin(sel)]
    fig = px.bar(
        eri_plot.sort_values('readiness_score', ascending=False),
        x='county', y='readiness_score',
        hover_data=['disposable_income_index','dealer_presence_index','yoy_ev_growth_index'],
        title="Readiness Score (higher = more ready to buy)"
    )
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Data (readiness)", expanded=False):
        st.dataframe(eri_plot, use_container_width=True)
else:
    st.info("EV_Readiness_Index not loaded.")

# ---- Historical trend line per county ----
st.subheader("Historical EV Registrations — Trend")
if hist is not None:
    counties = sorted(hist['county'].unique().tolist())
    csel = st.selectbox("Select county for trend", counties[:1] + counties)
    h1 = hist[hist['county'] == csel].copy()
    fig2 = px.line(h1, x='period', y='ev_units', markers=True,
                   title=f"Monthly EV registrations in {csel}")
    st.plotly_chart(fig2, use_container_width=True)
    with st.expander("Data (historical)", expanded=False):
        st.dataframe(h1, use_container_width=True)
else:
    st.info("Historical_Registrations not loaded.")

# ---- Stock snapshot: per-branch per-model ----
st.subheader("Inventory Snapshot")
if inv is not None and branches is not None:
    invb = inv.merge(branches[['branch_id','branch_name','county']], on='branch_id', how='left')
    fig3 = px.bar(
        invb, x='branch_name', y='stock_units', color='model', barmode='group',
        hover_data=['county','avg_days_on_lot','msrp'],
        title="Stock Units by Branch & Model"
    )
    st.plotly_chart(fig3, use_container_width=True)
    with st.expander("Data (inventory)", expanded=False):
        st.dataframe(invb, use_container_width=True)
else:
    st.info("Inventory/Branches not loaded.")

# ---- Readiness Map (bubble map) ----
st.subheader("EV Readiness Map")
try:
    from core.geo import COUNTY_CENTROIDS
    if eri is not None:
        dfm = eri.copy()
        dfm[['lat','lon']] = dfm['county'].map(lambda c: COUNTY_CENTROIDS.get(c, (None, None))).apply(pd.Series)
        dfm = dfm.dropna(subset=['lat','lon'])
        size_scalar = st.slider("Bubble size scale", 5, 40, 20)
        map_fig = px.scatter_mapbox(
            dfm,
            lat='lat', lon='lon',
            size=dfm['readiness_score'].clip(lower=1),  # avoid zero dots
            size_max=size_scalar,
            color='readiness_score',
            hover_name='county',
            hover_data=['disposable_income_index','dealer_presence_index','yoy_ev_growth_index'],
            color_continuous_scale='Turbo',
            zoom=5, height=500
        )
        map_fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(map_fig, use_container_width=True)
    else:
        st.info("EV_Readiness_Index not loaded.")
except Exception as e:
    st.warning(f"Map could not render: {e}")

from pathlib import Path
from core.pdf import build_exec_summary

st.subheader("Export")
if st.button("Generate 1‑page Exec Summary (PDF)"):
    out = Path(__file__).resolve().parents[2] / "data" / "outputs" / "Exec_Summary.pdf"
    logo_path = Path(__file__).resolve().parents[2] / "assets" / "logo.png"
    try:
        pdf_path = build_exec_summary(eri, hist, branches, inv, crm, logo_path, out)
        with open(pdf_path, "rb") as f:
            st.download_button("Download PDF", f, file_name="Exec_Summary.pdf", mime="application/pdf")
        st.success("PDF generated.")
    except Exception as e:
        st.error(f"PDF generation failed: {e}")
