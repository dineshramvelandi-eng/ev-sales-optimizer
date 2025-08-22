# EV Sales Optimizer — Starter Kit

This is a **working skeleton** of the EV Sales Optimizer Streamlit app.
It includes:
- Project structure
- CSV templates (headers only) in `data/input_templates/`
- Synthetic sample data in `data/sample/`
- Minimal code for scoring, simple forecasts (ARIMA via statsmodels), a greedy inventory optimizer, and revenue uplift

## Quick start

1. Create a virtual environment
   - **Windows (PowerShell):**
     ```powershell
     py -3.11 -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux (bash/zsh):**
     ```bash
     python3.11 -m venv .venv
     source .venv/bin/activate
     ```

2. Install packages
   ```bash
   pip install -r requirements.txt
   # Optional extras (maps/Prophet)
   # pip install -r optional-requirements.txt
   ```

3. Run the app
   ```bash
   streamlit run app/app.py
   ```

4. Load your data
   - Put your real CSVs into `data/` with the *exact* filenames:
     - `EV_Readiness_Index.csv`
     - `Historical_Registrations.csv`
     - `Branches.csv`
     - `Inventory.csv`
     - `CRM.csv`
     - (Optional) `WebSignals.csv`
   - Or start with the demo in `data/sample/` (loaded by default if `data/*.csv` not found).

5. Build a desktop binary (optional)
   ```bash
   pyinstaller --onefile --name EVSalesOptimizer launcher/launcher.py
   ```

## Notes
- Forecasting uses **statsmodels ARIMA** by default. If you install Prophet (see `optional-requirements.txt`), the app will **auto‑use Prophet** when available and fall back to ARIMA otherwise.
- All schema checks happen in `core/io.py`. See templates in `data/input_templates/`.
- The UI is modular: see pages under `app/pages/`.
