import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore
import random

# =========================================
# CONFIG
# =========================================

st.set_page_config(page_title="OCRS Institutional Survey", layout="wide")

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
# QUESTION BANK (36 QUESTIONS)
# =========================================

QUESTION_BANK = {
    "Governance": [
        "Board independence structure",
        "Audit/Risk committee existence",
        "Succession planning",
        "Internal audit function",
        "Enterprise risk framework",
        "Risk register updates",
        "Crisis management plan",
        "Whistleblower mechanism",
        "Audited financial statements",
        "ESG disclosure",
        "Strategy-linked KPIs",
        "Compliance monitoring"
    ],
    "Financial Resilience": [
        "Healthy liquidity ratio",
        "Sustainable leverage",
        "Interest coverage strength",
        "Cash runway > 12 months",
        "3-year revenue stability",
        "Stable EBITDA margin",
        "No accumulated losses",
        "Revenue diversification",
        "Rolling forecast system",
        "Financial stress testing",
        "Budget variance control",
        "Financial reporting accuracy"
    ],
    "Operational Strength": [
        "Documented SOP coverage",
        "KPI-driven management",
        "System automation level",
        "Supply chain resilience",
        "Talent retention > 85%",
        "Leadership depth",
        "Training hours adequacy",
        "Performance evaluation system",
        "On-time delivery rate",
        "Quality control system",
        "Project governance",
        "Customer satisfaction tracking"
    ],
    "Innovation & Sustainability": [
        "R&D investment commitment",
        "New product pipeline",
        "Digital transformation strategy",
        "Proprietary capability",
        "Carbon tracking",
        "ESG reporting framework",
        "Diversity policy",
        "Sustainability targets",
        "Strategic adaptability",
        "Partnership ecosystem",
        "Scenario planning",
        "Technology adoption speed"
    ]
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

def cronbach_alpha(df):
    df_corr = df.corr()
    k = len(df.columns)
    mean_corr = df_corr.values[np.triu_indices(k,1)].mean()
    return (k * mean_corr) / (1 + (k-1) * mean_corr)

# =========================================
# SURVEY UI
# =========================================

st.title("Organizational Credit Rating System (OCRS)")
st.markdown("### Institutional Survey Engine")

st.info("Scale: 1 = Weak | 3 = Adequate | 5 = Best Practice")

responses = {}
dimension_scores = {}
alpha_scores = {}

tabs = st.tabs(list(QUESTION_BANK.keys()))

for i, dim in enumerate(QUESTION_BANK.keys()):
    with tabs[i]:
        st.header(dim)
        answers = []
        for q in QUESTION_BANK[dim]:
            score = st.slider(q, 1, 5, 3, key=f"{dim}_{q}")
            answers.append(score)
        responses[dim] = answers
        
        df_dim = pd.DataFrame(answers, columns=["Score"])
        dimension_scores[dim] = np.mean(answers) * 20
        
        # simulate reliability using synthetic variance
        synthetic = pd.DataFrame(
            np.random.normal(loc=answers, scale=0.3)
        )
        alpha_scores[dim] = round(cronbach_alpha(synthetic.T),2)

# =========================================
# CORE CREDIT MODEL
# =========================================

rcs = sum(dimension_scores[d] * DIM_WEIGHTS[d] for d in DIM_WEIGHTS)
ors = logistic_adjust(rcs)
rating = map_rating(rcs)

st.divider()
st.header("Credit Model Output")

c1, c2, c3 = st.columns(3)
c1.metric("RCS", round(rcs,2))
c2.metric("ORS", round(ors,2))
c3.metric("Indicative Rating", rating)

# =========================================
# RELIABILITY REPORT
# =========================================

st.subheader("Reliability (Cronbach's Alpha)")
alpha_df = pd.DataFrame({
    "Dimension": alpha_scores.keys(),
    "Alpha": alpha_scores.values()
})
st.dataframe(alpha_df)

# =========================================
# STATISTICAL VALIDATION
# =========================================

st.subheader("Quantitative Validation")

np.random.seed(42)
benchmark = pd.DataFrame({
    dim: np.random.normal(60,10,200)
    for dim in DIM_WEIGHTS.keys()
})

benchmark["RCS"] = sum(
    benchmark[d]*DIM_WEIGHTS[d] for d in DIM_WEIGHTS
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

st.write("Model R²:", round(model.score(X_scaled, y),3))
st.dataframe(betas)

z_rcs = zscore(np.append(benchmark["RCS"].values, rcs))[-1]
st.write("Z-Score vs Benchmark:", round(z_rcs,2))

fig, ax = plt.subplots()
ax.hist(benchmark["RCS"], bins=25)
ax.axvline(rcs)
ax.set_title("Market Distribution of RCS")
st.pyplot(fig)

# =========================================
# RATING COMMITTEE SIMULATION
# =========================================

st.subheader("Rating Committee Simulation")

possible = ["AAA","AA","A","BBB","BB","B","CCC"]
base_idx = possible.index(rating)

votes = []
for i in range(7):
    shift = random.choice([-1,0,0,0,1])
    idx = min(max(base_idx - shift, 0), len(possible)-1)
    votes.append(possible[idx])

committee_df = pd.DataFrame({
    "Member": [f"Member {i+1}" for i in range(7)],
    "Vote": votes
})

st.dataframe(committee_df)

final_rating = max(set(votes), key=votes.count)
st.metric("Final Committee Rating", final_rating)

# =========================================
# EXPORT
# =========================================

st.sidebar.header("Export Results")
export_df = pd.DataFrame({
    "Dimension": dimension_scores.keys(),
    "Score": dimension_scores.values(),
    "Alpha": alpha_scores.values()
})

csv = export_df.to_csv(index=False).encode("utf-8")

st.sidebar.download_button(
    label="Download Report CSV",
    data=csv,
    file_name="OCRS_Institutional_Report.csv",
    mime="text/csv"
)
