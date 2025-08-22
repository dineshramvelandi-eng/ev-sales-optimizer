def simulate_uplift(baseline_conversion: float, available_leads: int, plan_units: int, gross_margin_per_unit: float, transfer_units: int, transfer_cost_per_unit: float):
    baseline_units = baseline_conversion * available_leads
    delta_units = plan_units - baseline_units
    uplift_revenue = delta_units * gross_margin_per_unit - transfer_units * transfer_cost_per_unit
    baseline_revenue = baseline_units * gross_margin_per_unit if gross_margin_per_unit else 0.0
    uplift_percent = (uplift_revenue / baseline_revenue) if baseline_revenue else None
    return {
        "baseline_units": round(baseline_units, 2),
        "plan_units": plan_units,
        "delta_units": round(delta_units, 2),
        "uplift_revenue": round(uplift_revenue, 2),
        "uplift_percent": round(uplift_percent*100, 2) if uplift_percent is not None else None
    }
