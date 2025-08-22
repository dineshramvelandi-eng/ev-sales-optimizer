import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

# Try Prophet first, fall back to ARIMA
try:
    from prophet import Prophet  # type: ignore
    _HAS_PROPHET = True
except Exception:
    _HAS_PROPHET = False
    from statsmodels.tsa.arima.model import ARIMA  # type: ignore

def _forecast_one(county_df: pd.DataFrame, periods: int=3) -> pd.DataFrame:
    df = county_df.copy()
    df['period'] = pd.to_datetime(df['period'])
    df = df.sort_values('period')
    y = df['ev_units'].astype(float)

    # Ensure positive values
    y = y.clip(lower=0.0)
    if _HAS_PROPHET:
        m = Prophet(seasonality_mode='additive', yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        train = pd.DataFrame({'ds': df['period'], 'y': y})
        m.fit(train)
        future = m.make_future_dataframe(periods=periods, freq='MS')
        fc = m.predict(future).tail(periods)[['ds','yhat']].rename(columns={'ds':'period','yhat':'forecast'})
    else:
        order = (1,1,1) if len(y) > 6 else (1,0,0)
        model = ARIMA(y, order=order)
        res = model.fit()
        pred = res.forecast(steps=periods)
        last = df['period'].max()
        idx = [last + relativedelta(months=i) for i in range(1, periods+1)]
        fc = pd.DataFrame({'period': idx, 'forecast': pred.values})

    return fc

def make_county_forecasts(hist: pd.DataFrame, eri: pd.DataFrame, counties, alpha: float, share: float) -> pd.DataFrame:
    out_rows = []
    eri2 = eri[['county','readiness_score']].copy()
    z = (eri2['readiness_score'] - eri2['readiness_score'].mean()) / (eri2['readiness_score'].std() + 1e-6)
    eri2['readiness_z'] = z
    for c in counties:
        cdf = hist[hist['county']==c]
        if len(cdf) < 3:
            continue
        fc = _forecast_one(cdf, periods=3)
        rz = float(eri2.loc[eri2['county']==c, 'readiness_z'].fillna(0).iloc[0]) if (eri2['county']==c).any() else 0.0
        adj = 1 + alpha * rz
        fc['county'] = c
        fc['forecast_adj'] = (fc['forecast'] * adj).clip(lower=0.0)
        fc['expected_dealer_units'] = (fc['forecast_adj'] * share).round(0).astype(int)
        out_rows.append(fc)
    if not out_rows:
        return pd.DataFrame()
    res = pd.concat(out_rows, ignore_index=True)
    res['period'] = pd.to_datetime(res['period']).dt.strftime('%Y-%m')
    return res[['county','period','forecast','forecast_adj','expected_dealer_units']]
