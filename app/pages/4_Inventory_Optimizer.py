# ================= Inventory Optimizer (robust, state-safe) =================
import sys, os
import pandas as pd
import streamlit as st
from pathlib import Path

# Ensure root on path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Init session keys (prevents missing-attr errors)
from core.state import init as init_state
init_state()

from core.io import load_all_datasets
from core.forecast import make_county_forecasts

st.title("Inventory Optimizer")

# ---- Load data
eri, hist, branches, inv, crm, webs = load_all_datasets(prefer_real=True)

if (hist is None) or (branches is None) or (inv is None):
    st.error("Missing required data (History / Branches / Inventory). Check Admin/Data.")
    st.stop()

# ---- Safe state pulls with defaults
counties_all = sorted(hist["county"].unique().tolist())
sel = st.session_state.get("sel_counties", counties_all[:6] if len(counties_all) >= 6 else counties_all)
alpha = float(st.session_state.get("alpha", 0.10))
share = float(st.session_state.get("market_share", 0.15))

# Try to use forecasts saved from Forecasts page; if not there, recompute
fc_next = st.session_state.get("forecast_next", None)
if fc_next is None:
    # Rebuild a minimal forecast for the selected counties so the page still works
    if not sel:
        st.info("Select counties in **Forecasts** first to drive the optimizer.")
        try:
            st.page_link("app/pages/2_Forecasts.py", label="Go to Forecasts", icon="📈")
        except Exception:
            pass
        st.stop()

    fc_full = make_county_forecasts(hist, eri, sel, alpha, share)
    if fc_full.empty:
        st.warning("Not enough history to forecast selected counties.")
        st.stop()

    fc_full["period_dt"] = pd.to_datetime(fc_full["period"], format="%Y-%m")
    next_month = fc_full["period_dt"].min()
    fc_next = fc_full[fc_full["period_dt"] == next_month].copy()

# ---- Build demand vs local stock (next month)
# Map inventory to county via branches
inv_b = inv.merge(
    branches[["branch_id", "county"]],
    on="branch_id", how="left"
)
local_stock = inv_b.groupby("county", as_index=False)["stock_units"].sum().rename(columns={"stock_units": "local_stock"})

demand = fc_next[["county", "expected_dealer_units"]].merge(local_stock, on="county", how="left")
demand["local_stock"] = demand["local_stock"].fillna(0).astype(int)
demand["shortfall_units"] = (demand["expected_dealer_units"] - demand["local_stock"]).astype(int)

# Let user confirm / tweak inputs before optimization
st.subheader("Next‑month demand vs local stock")
st.dataframe(
    demand.sort_values(["shortfall_units","expected_dealer_units"], ascending=[False,False]),
    use_container_width=True
)

# ====== your existing optimization code can continue below ======
# It should read from `demand` (shortfall), `inv_b` (stock by branch/model), etc.
# and finally write the plan to st.session_state via:
# from core.state import remember_optimizer
# remember_optimizer(plan_df, transfer_cost_per_unit)
