from __future__ import annotations
import os
import io
import pandas as pd
from typing import Tuple, Optional, Dict, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample")

REQUIRED_SCHEMAS: Dict[str, List[str]] = {
    "EV_Readiness_Index": ["county","readiness_score","disposable_income_index","dealer_presence_index","yoy_ev_growth_index"],
    "Historical_Registrations": ["county","period","ev_units"],
    "Branches": ["branch_id","branch_name","county","serves_counties"],
    "Inventory": ["branch_id","model","trim","stock_units","avg_days_on_lot","msrp","gross_margin_per_unit"],
    "CRM": ["lead_id","first_name","last_name","email","phone","county","current_vehicle_type","vehicle_year","income_band","distance_km","last_touch_date","engagements_90d"],
}

OPTIONAL_SCHEMAS: Dict[str, List[str]] = {
    "WebSignals": ["county","model","pageviews_30d","configurator_starts_30d","testdrive_requests_30d"],
}

def _load_csv(path: str) -> Optional[pd.DataFrame]:
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)

def _find_real_or_sample(name: str) -> Optional[pd.DataFrame]:
    real_path = os.path.join(DATA_DIR, f"{name}.csv")
    df = _load_csv(real_path)
    if df is None:
        sample_path = os.path.join(SAMPLE_DIR, f"{name}.csv")
        df = _load_csv(sample_path)
    return df

def load_all_datasets(prefer_real: bool=True):
    eri = _find_real_or_sample("EV_Readiness_Index")
    hist = _find_real_or_sample("Historical_Registrations")
    branches = _find_real_or_sample("Branches")
    inv = _find_real_or_sample("Inventory")
    crm = _find_real_or_sample("CRM")
    webs = _find_real_or_sample("WebSignals")
    return eri, hist, branches, inv, crm, webs

def validate_and_save_upload(file, expected_name: str) -> (bool, str):
    # Determine which schema to use
    base = expected_name.replace(".csv","")
    schema = REQUIRED_SCHEMAS.get(base) or OPTIONAL_SCHEMAS.get(base)
    if schema is None:
        return False, f"Unknown dataset: {base}"

    # Read into DataFrame
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return False, f"Failed to read CSV: {e}"

    missing = [c for c in schema if c not in df.columns]
    if missing:
        return False, f"Missing columns: {missing}. Expected: {schema}"

    out_path = os.path.join(DATA_DIR, expected_name)
    df.to_csv(out_path, index=False)
    return True, f"Saved to {out_path}"
