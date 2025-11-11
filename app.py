import numpy as np
import pandas as pd
import streamlit as st
import joblib
from pathlib import Path

st.set_page_config(page_title="UK House Price Predictor", page_icon="🏡", layout="centered")

st.title("🏡 UK House Price Predictor")
st.caption("Team Yunus — Cloud AI")

# ------------------------------------------------------------
# Load model bundle (model + target encoder + training columns)
# ------------------------------------------------------------
BUNDLE_PATH = Path("data/clean/price_model_lgbm.pkl")

if not BUNDLE_PATH.exists():
    st.error(f"Model bundle not found at {BUNDLE_PATH}. Train and save your model first.")
    st.stop()

bundle = joblib.load(BUNDLE_PATH.open("rb"))

# Handle both cases: saved as dict or as raw estimator
if isinstance(bundle, dict):
    model = bundle.get("model", None)
    target_encoder = bundle.get("target_encoder", None)
    columns = bundle.get("columns", None)
else:
    model = bundle
    target_encoder = None
    columns = None

if model is None:
    st.error("Loaded bundle has no 'model'. Re-save your model with keys: model, target_encoder, columns.")
    st.stop()

# ------------------------------------------------------------
# Feature builder: matches training-time preprocessing
# ------------------------------------------------------------
def make_features(type_code: str, is_new: str, duration: str, county: str, year: int) -> pd.DataFrame:
    # normalize inputs
    type_code = (type_code or "").strip().upper()
    is_new    = (is_new or "").strip().upper()
    duration  = (duration or "").strip().upper()
    county    = (county or "").strip().upper()

    row = pd.DataFrame([{
        "type": type_code,         # D/S/T/F/O
        "is_new": is_new,          # Y/N
        "duration": duration,      # F/L/U (dataset can contain U=Unknown)
        "county": county,
        "year": int(year)
    }])

    # Target encode county -> county_te
    if target_encoder is not None:
        enc_df = target_encoder.transform(row[["county"]])  # returns DF with 'county'
        row["county_te"] = enc_df["county"]
    else:
        row["county_te"] = 0.0

    # IMPORTANT: do NOT drop_first here (single-row issue)
    row = pd.get_dummies(row, columns=["type", "is_new", "duration"], drop_first=False)

    # drop raw county; we use encoded
    if "county" in row.columns:
        row = row.drop(columns=["county"])

    # Align to training matrix: add any missing columns = 0,
    # then keep only the training columns in the right order.
    if columns is not None:
        for c in columns:
            if c not in row.columns:
                row[c] = 0
        row = row[columns]

    return row


# ------------------------------------------------------------
# UI form
# ------------------------------------------------------------
with st.form("inputs"):
    st.subheader("Enter property details")

    type_code = st.selectbox("Property type", ["D", "S", "T", "F", "O"], index=2,
                             help="D=Detached, S=Semi-detached, T=Terraced, F=Flat, O=Other")
    is_new = st.selectbox("Is new build?", ["N", "Y"], index=0)
    duration = st.selectbox("Tenure (Duration)", ["F", "L"], index=0, help="F=Freehold, L=Leasehold")
    county = st.text_input("County", value="GREATER LONDON")
    year = st.number_input("Year of transfer", min_value=1995, max_value=2017, value=2015, step=1)

    submit = st.form_submit_button("Predict price")

# ------------------------------------------------------------
# Predict
# ------------------------------------------------------------
if submit:
    try:
        X_row = make_features(
            type_code=type_code,
            is_new=is_new,
            duration=duration,
            county=county.strip().upper(),
            year=year
        )

        # Predict (some joblib loads may wrap the estimator — handle generically)
        estimator = getattr(model, "predict", None)
        if callable(estimator):
            y_log = model.predict(X_row)[0]
        else:
            inner = getattr(model, "model", None)
            if inner is None or not hasattr(inner, "predict"):
                raise TypeError("Loaded object does not expose a usable .predict(...)")
            y_log = inner.predict(X_row)[0]

        # Inverse of log1p used during training
        y = float(np.expm1(y_log))

        st.success(f"Estimated price: **£{y:,.0f}**")
        with st.expander("Debug: model inputs"):
            st.write(X_row)

    except Exception as e:
        st.error(f"Prediction failed: {e}")
        with st.expander("Show traceback / details"):
            import traceback
            st.code("".join(traceback.format_exc()))