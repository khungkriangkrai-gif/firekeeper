import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.title("Organizational Credit Rating System (OCRS)")

# =====================================================
# FUNCTIONS
# =====================================================

def normalize_0_100(series):
    if series.max() == series.min():
        return pd.Series(np.zeros(len(series)))
    return 100 * (series - series.min()) / (series.max() - series.min())

def normalize_likert(avg_score):
    return (avg_score - 1) / 4 * 100

def cronbach_alpha(df):
    items = df.values
    item_vars = items.var(axis=0, ddof=1)
    total_var = items.sum(axis=1).var(ddof=1)
    n = df.shape[1]
    if total_var == 0:
        return 0
    return (n/(n-1)) * (1 - item_vars.sum()/total_var)

def calculate_dimension_score(df, cols, reverse=False):
    avg = df[cols].mean(axis=1)
    score = normalize_likert(avg)
    if reverse:
        score = 100 - score
    return score

def compute_rcs(df_dims, financial_outcome):
    X = df_dims.copy()
    X["Entropy"] = -X["Entropy"]

    model = LinearRegression()
    model.fit(X, financial_outcome)

    betas = model.coef_
    r2 = model.score(X, financial_outcome)

    rcs_raw = (X * betas).sum(axis=1)
    rcs_scaled = normalize_0_100(rcs_raw)

    return rcs_scaled, betas, r2

def compute_ors(risk_df):
    weights = np.ones(risk_df.shape[1]) / risk_df.shape[1]
    ors_raw = risk_df.values @ weights
    ors_scaled = normalize_0_100(pd.Series(ors_raw))
    return ors_scaled

def assign_rating(rcs, ors):
    if rcs >= 85 and ors <= 30:
        return "AAA"
    elif rcs >= 75 and ors <= 35:
        return "AA"
    elif rcs >= 65 and ors <= 45:
        return "A"
    elif rcs >= 55 and ors <= 55:
        return "BBB"
    elif rcs >= 45 and ors <= 65:
        return "BB"
    elif rcs >= 35 and ors <= 75:
        return "B"
    else:
        return "CCC/C"

# =====================================================
# DEMO DATA
# =====================================================

np.random.seed(42)
n = 50

survey_df = pd.DataFrame(np.random.randint(1,6,(n,16)),
                         columns=[
                             "E1","E2","E3","E4",
                             "EM1","EM2","EM3","EM4",
                             "I1","I2","I3","I4",
                             "P1","P2","P3","P4"
                         ])

financial_outcome = np.random.normal(0.1, 0.03, n)

entropy = calculate_dimension_score(survey_df, ["E1","E2","E3","E4"], True)
empathy = calculate_dimension_score(survey_df, ["EM1","EM2","EM3","EM4"])
identity = calculate_dimension_score(survey_df, ["I1","I2","I3","I4"])
purpose = calculate_dimension_score(survey_df, ["P1","P2","P3","P4"])

df_dims = pd.DataFrame({
    "Entropy": entropy,
    "Empathy": empathy,
    "Identity": identity,
    "Purpose": purpose
})

rcs, betas, r2 = compute_rcs(df_dims, financial_outcome)

risk_df = pd.DataFrame(np.random.rand(n,4),
                       columns=[
                           "RevenueVolatility",
                           "LeadershipChurn",
                           "StrategyDrift",
                           "TalentFlightRisk"
                       ])

ors = compute_ors(risk_df)

final_rcs = rcs.mean()
final_ors = ors.mean()
rating = assign_rating(final_rcs, final_ors)

# =====================================================
# OUTPUT
# =====================================================

st.subheader("Final Scores")
st.write("RCS:", round(final_rcs,2))
st.write("ORS:", round(final_ors,2))
st.write("Rating:", rating)

st.subheader("Model Statistics")
st.write("Regression Betas:", betas)
st.write("R-squared:", round(r2,3))

# Plot 1
fig1, ax1 = plt.subplots()
ax1.plot(rcs.values)
ax1.set_title("RCS Distribution")
st.pyplot(fig1)

# Plot 2
fig2, ax2 = plt.subplots()
ax2.scatter(rcs, ors)
ax2.set_title("RCS vs ORS")
st.pyplot(fig2)
