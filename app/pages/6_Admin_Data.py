import streamlit as st
import pandas as pd
from core.io import REQUIRED_SCHEMAS, validate_and_save_upload

st.title("Admin / Data")
st.write("Upload CSVs matching the required schemas.")

for name, cols in REQUIRED_SCHEMAS.items():
    st.subheader(name)
    file = st.file_uploader(f"Upload {name}.csv", type=["csv"], key=name)
    if file is not None:
        ok, msg = validate_and_save_upload(file, expected_name=f"{name}.csv")
        if ok:
            st.success(msg)
        else:
            st.error(msg)
