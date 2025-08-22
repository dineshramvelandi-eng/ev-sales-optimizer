# core/state.py
import streamlit as st
import pandas as pd
from typing import List

def init():
    defaults = {
        "sel_counties": [],
        "alpha": 0.10,
        "market_share": 0.15,
        "forecast_df": None,
        "forecast_next": None,
        "plan_units": None,
        "optimizer_plan": None,
        "transfer_units": 0,
        "transfer_cost_per_unit": 50,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def remember_forecast(sel_counties: List[str], alpha: float, share: float,
                      fc_full: pd.DataFrame, fc_next: pd.DataFrame):
    st.session_state.sel_counties = sel_counties
    st.session_state.alpha = alpha
    st.session_state.market_share = share
    st.session_state.forecast_df = fc_full
    st.session_state.forecast_next = fc_next
    st.session_state.plan_units = int(fc_next["expected_dealer_units"].sum())

def remember_optimizer(plan: pd.DataFrame, transfer_cost_per_unit: float):
    st.session_state.optimizer_plan = plan
    st.session_state.transfer_units = int(plan["units"].sum()) if plan is not None and not plan.empty else 0
    st.session_state.transfer_cost_per_unit = float(transfer_cost_per_unit)
