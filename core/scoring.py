import pandas as pd
import numpy as np

VEHICLE_TYPE_SCORES = {
    "ICE": 1.0,
    "HEV": 0.6,
    "PHEV": 0.7,
    "EV": 0.3,
}

INCOME_BANDS = ["<€40k","€40–60k","€60–80k",">€80k"]

def _norm_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    if s.max() == s.min():
        return pd.Series([0.0]*len(s), index=s.index)
    return (s - s.min()) / (s.max() - s.min())

def _income_to_numeric(band: str) -> float:
    mapping = {"<€40k": 0, "€40–60k": 1, "€60–80k": 2, ">€80k": 3}
    return mapping.get(str(band), 1)

def score_leads(crm: pd.DataFrame, eri: pd.DataFrame) -> pd.DataFrame:
    # Merge readiness
    out = crm.copy()
    out = out.merge(eri[['county','readiness_score']], on='county', how='left')

    # Normalizations
    out['readiness_norm'] = _norm_series(out['readiness_score'].fillna(out['readiness_score'].median()))
    out['vehicle_type_score'] = out['current_vehicle_type'].map(VEHICLE_TYPE_SCORES).fillna(0.5)
    out['income_num'] = out['income_band'].apply(_income_to_numeric)
    out['income_norm'] = _norm_series(out['income_num'])
    out['engagements_norm'] = _norm_series(out['engagements_90d'].astype(float).fillna(0))
    out['distance_norm'] = _norm_series(out['distance_km'].astype(float).fillna(out['distance_km'].median()))

    out['score'] = (100 * (
        0.35*out['readiness_norm'] +
        0.25*out['vehicle_type_score'] +
        0.20*out['income_norm'] +
        0.10*out['engagements_norm'] +
        0.10*(1 - out['distance_norm'])
    )).round(0).astype(int)

    return out
