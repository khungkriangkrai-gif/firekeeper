import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore
import random

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="OCRS v2 - Institutional Edition",
    layout="wide"
)

# Dark institutional styling
st.markdown("""
<style>
body {background-color:#0e1117;}
.metric-label {color:white !important;}
</style>
""", unsafe_allow_html=True)

st.title("Organizational Credit Rating System (OCRS) v2")
st.markdown("Institutional Investor Dashboard")

# =========================================
# CONFIGURATION
# =========================================

DIM_WEIGHTS = {
    "Governance": 0.25,
    "Financial Resilience": 0.30,
    "Operational Strength": 0.25,
    "Innovation & Sustainability": 0.20
}

RATING_SCALE = {
    90: "AAA",
    80: "AA",
    70: "A",
    60: "BBB",
    50: "BB",
    40: "B",
    0: "CCC"
}

# =========================================
# HELPER FUNCTIONS
# =========================================

def map_rating(score):
    for threshold, rating in RATING_SCALE.items():
        if score >= threshold:
            return rating
    return "CCC"

def logistic_adjust(rcs):
    return 100 / (1 + np.exp(-0.08*(rcs-50)))

def committee_vote(rcs):
    base_rating = map_rating(rcs)
    possible = ["AAA","AA","A","BBB","BB","B","CCC"]
    idx = possible.index(base_rating)
    shift = random.choice([-1,0,0,0,1])  # committee bias
    new_idx = min(max(idx-shift,0),len(possible)-1)
    return possible[new_idx]

# =========================================
# TABS
# =========================================

tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Survey",
    "2️⃣ Credit Model",
    "3️⃣ Statistical Layer",
    "4️⃣ Rating Committee"
])

# =========================================
# TAB 1 — SURVEY
# =========================================

with tab1:
    st.header("Organizational Assessment Questionnaire")

    def dimension_block(title):
        st.subheader(title)
        q1 = st.slider(f"{title} - Leadership & Policy Strength", 1, 5, 3)
        q2 = st.slider(f"{title} - Risk Management Structure", 1, 5, 3)
        q3 = st.slider(f"{title} - Transparency & Reporting", 1, 5, 3)
        return np.mean([q1,q2,q3]) * 20  # scale to 100

    scores = {}
    scores["Governance"] = dimension_block("Governance")
    scores["Financial Resilience"] = dimension_block("Financial Resilience")
    scores["Operational Strength"] = dimension_block("Operational Strength")
    scores["Innovation & Sustainability"] = dimension_block("Innovation & Sustainability")

    st.success("Survey Completed")

# =========================================
# COMPUTE CORE SCORES
# =========================================

rcs = sum(scores[d]*DIM_WEIGHTS[d] for d in DIM_WEIGHTS)
ors = logistic_adjust(rcs)
rating = map_rating(rcs)

# =========================================
# TAB 2 — CREDIT MODEL
# =========================================

with tab2:
    st.header("Core Credit Metrics")

    c1, c2, c3 = st.columns(3)
    c1.metric("RCS", round(rcs,2))
    c2.metric("ORS", round(ors,2))
    c3.metric("Indicative Rating", rating)

    st.subheader("Dimension Breakdown")
    df_break = pd.DataFrame({
        "Dimension": list(scores.keys()),
        "Score": list(scores.values())
    })
    st.dataframe(df_break)

# =========================================
# TAB 3 — STATISTICAL LAYER
# =========================================

with tab3:
    st.header("Quantitative Validation Layer")

    np.random.seed(42)
    benchmark = pd.DataFrame({
        "Governance": np.random.normal(65,10,200),
        "Financial Resilience": np.random.normal(60,12,200),
        "Operational Strength": np.random.normal(62,9,200),
        "Innovation & Sustainability": np.random.normal(58,11,200),
    })

    benchmark["RCS"] = (
        benchmark["Governance"]*0.25 +
        benchmark["Financial Resilience"]*0.30 +
        benchmark["Operational Strength"]*0.25 +
        benchmark["Innovation & Sustainability"]*0.20
    )

    X = benchmark[list(DIM_WEIGHTS.keys())]
    y = benchmark["RCS"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LinearRegression()
    model.fit(X_scaled, y)

    betas = pd.DataFrame({
        "Factor": DIM_WEIGHTS.keys(),
        "Beta": model.coef_
    })

    st.subheader("Regression Coefficients")
    st.dataframe(betas)

    st.write("Model R²:", round(model.score(X_scaled, y),3))

    z_rcs = zscore(np.append(benchmark["RCS"].values, rcs))[-1]
    st.write("Z-Score vs Market:", round(z_rcs,2))

    fig, ax = plt.subplots()
    ax.hist(benchmark["RCS"], bins=25)
    ax.axvline(rcs)
    ax.set_title("RCS Market Distribution")
    st.pyplot(fig)

# =========================================
# TAB 4 — RATING COMMITTEE SIMULATION
# =========================================

with tab4:
    st.header("Rating Committee Simulation")

    committee_results = []
    for i in range(7):
        committee_results.append(committee_vote(rcs))

    committee_df = pd.DataFrame({
        "Committee Member": [f"Member {i+1}" for i in range(7)],
        "Vote": committee_results
    })

    st.dataframe(committee_df)

    final_committee_rating = max(set(committee_results), key=committee_results.count)

    st.subheader("Final Committee Decision")
    st.metric("Final Assigned Rating", final_committee_rating)

    if final_committee_rating in ["AAA","AA"]:
        st.success("Low Risk Institutional Grade")
    elif final_committee_rating in ["A","BBB"]:
        st.info("Investment Grade")
    elif final_committee_rating in ["BB","B"]:
        st.warning("Speculative Grade")
    else:
        st.error("Distressed Grade")

# =========================================
# EXPORT
# =========================================

st.sidebar.header("Export Report")
report_df = pd.DataFrame({
    "Dimension": list(scores.keys()),
    "Score": list(scores.values())
})

csv = report_df.to_csv(index=False).encode("utf-8")

st.sidebar.download_button(
    label="Download CSV",
    data=csv,
    file_name="OCRS_v2_Report.csv",
    mime="text/csv"
)
