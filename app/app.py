# --- Make sure project root is on sys.path ---
import sys, os
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import streamlit as st


import plotly.io as pio
pio.templates.default = "plotly_dark"  # matches dark theme
pio.templates["plotly_dark"]["layout"]["font"]["family"] = "Inter, system-ui, sans-serif"
pio.templates["plotly_dark"]["layout"]["paper_bgcolor"] = "#0B0F19"
pio.templates["plotly_dark"]["layout"]["plot_bgcolor"] = "#0B0F19"
pio.templates["plotly_dark"]["layout"]["colorway"] = ["#21D4FD","#B721FF","#00E6A8","#F9C80E","#FF3D71"]

from core.state import init as init_state
init_state()  # <-- run once at app start

from pathlib import Path
from PIL import Image
import streamlit as st



# Paths
ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "assets" / "logo.png"

# Use your logo as the favicon if it exists; fallback to emoji
page_icon = Image.open(LOGO) if LOGO.exists() else "⚡"

st.set_page_config(
    page_title="EV Sales Optimizer",
    page_icon=page_icon,   # <-- this controls the tab icon
    layout="wide",
)

from pathlib import Path

# --- Top header with logo ---
LOGO = Path(__file__).resolve().parents[1] / "assets" / "logo.png"
cols = st.columns([0.1, 0.9])
with cols[0]:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)

with cols[1]:
    st.markdown("<h1 style='margin-bottom:0'>EV Sales Optimizer</h1>", unsafe_allow_html=True)
    st.caption("Forecast • Focus • Reallocate • Prove Revenue Uplift")
st.divider()

# ---------------- Global style ----------------
st.markdown("""
<style>
/* smoother fonts & spacing */
html, body, [class*="css"]  { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
h1, h2, h3 { letter-spacing: 0.2px; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* Hero card */
.hero {
  background: radial-gradient(1200px 600px at 10% -10%, rgba(33,212,253,0.18), rgba(0,0,0,0)) ,
              linear-gradient(135deg, #1E293B 0%, #0B0F19 60%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  padding: 28px 28px;
  margin: 8px 0 18px 0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.hero-title {
  font-size: 40px; font-weight: 800; margin: 0 0 6px 0; color: #F8FAFC;
}
.hero-sub {
  color: #A9B4C4; font-size: 16px; margin-bottom: 18px;
}
.chips { display:flex; gap:10px; flex-wrap:wrap; margin: 8px 0 0 0;}
.chip {
  background: linear-gradient(180deg, #0F172A 0%, #0B1220 100%);
  border: 1px solid rgba(255,255,255,0.08);
  color: #CFE6FF; padding: 6px 10px; border-radius: 999px;
  font-size: 12.5px; letter-spacing: .3px;
}

/* CTA buttons */
.cta { display:flex; gap:12px; margin-top:12px; }
.btn-primary {
  background: linear-gradient(90deg, #21D4FD 0%, #B721FF 100%);
  color: #0B0F19; font-weight: 700; border-radius: 12px; padding: 10px 14px;
  text-decoration:none; display:inline-block;
}
.btn-ghost {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  color: #E8EEF6; border-radius: 12px; padding: 10px 14px;
  text-decoration:none; display:inline-block;
}

/* Tip card */
.tip {
  background: #0E223A;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 14px 16px;
  color: #D5E6FF;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Hero block ----------------
hero_left, hero_right = st.columns([0.62, 0.38], gap="large")
with hero_left:
    st.markdown("""
    <div class="hero">
      <div class="hero-title">EV Sales Optimizer</div>
      <div class="hero-sub">Forecast • Focus • Reallocate • Prove Revenue Uplift</div>
      <div class="chips">
        <div class="chip">🔭 County demand forecasts</div>
        <div class="chip">🎯 Lead propensity scoring</div>
        <div class="chip">🚚 Inventory reallocation plan</div>
        <div class="chip">💶 Uplift & ROI simulator</div>
      </div>
      <div class="cta">
        <a class="btn-primary" href="#goto-overview">Open dashboard</a>
        <a class="btn-ghost" href="#quick-links">Quick links</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

with hero_right:
    st.markdown("""
    <div class="tip">
      <b>Tip:</b> Start with <b>Admin / Data</b> to validate your files, or try the built‑in demo data.
      <br/><br/>
      <small>Use the left sidebar to navigate sections.</small>
    </div>
    """, unsafe_allow_html=True)

# Anchor so the "Open dashboard" button scrolls here
st.markdown('<div id="goto-overview"></div>', unsafe_allow_html=True)

# ---------------- Quick links (uses native page links if available) ----------------
st.markdown('<div id="quick-links"></div>', unsafe_allow_html=True)
try:
    # Streamlit >=1.29 has st.page_link
    l1, l2, l3, l4, l5 = st.columns(5)
    with l1: st.page_link("app/pages/1_Overview.py", label="Overview", icon="📊")
    with l2: st.page_link("app/pages/2_Forecasts.py", label="Forecasts", icon="📈")
    with l3: st.page_link("app/pages/3_Leads.py", label="Leads", icon="🎯")
    with l4: st.page_link("app/pages/4_Inventory_Optimizer.py", label="Inventory", icon="🚚")
    with l5: st.page_link("app/pages/5_Revenue_Simulator.py", label="Revenue", icon="💶")
except Exception:
    st.write("Use the sidebar to navigate.")
