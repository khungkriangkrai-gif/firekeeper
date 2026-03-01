import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# =====================================================
# 1. NORMALIZATION UTILITIES
# =====================================================

def normalize_0_100(series):
    return 100 * (series - series.min()) / (series.max() - series.min())

def normalize_likert(avg_score):
    return (avg_score - 1) / 4 * 100


# =====================================================
# 2. CRONBACH ALPHA (RELIABILITY)
# =====================================================

def cronbach_alpha(df):
    items = df.values
    item_vars = items.var(axis=0, ddof=1)
    total_var = items.sum(axis=1).var(ddof=1)
    n = df.shape[1]
    return (n/(n-1)) * (1 - item_vars.sum()/total_var)


# =====================================================
# 3. DIMENSION SCORING
# =====================================================

def calculate_dimension_score(df, cols, reverse=False):
    avg = df[cols].mean(axis=1)
    score = normalize_likert(avg)
    if reverse:
        score = 100 - score
    return score.round(2)


# =====================================================
# 4. COMPUTE RCS (REGRESSION WEIGHTED)
# =====================================================

def compute_rcs(df_dims, financial_outcome):

    X = df_dims.copy()
    X["Entropy"] = -X["Entropy"]  # negative driver

    model = LinearRegression()
    model.fit(X, financial_outcome)

    betas = model.coef_
    r_squared = model.score(X, financial_outcome)

    rcs_raw = (X * betas).sum(axis=1)
    rcs_scaled = normalize_0_100(rcs_raw)

    return rcs_scaled.round(2), betas, r_squared


# =====================================================
# 5. COMPUTE ORS (RISK ENGINE)
# =====================================================

def compute_ors(risk_df, weights=None):
    if weights is None:
        weights = np.ones(risk_df.shape[1]) / risk_df.shape[1]

    ors_raw = risk_df.values @ weights
    ors_scaled = normalize_0_100(pd.Series(ors_raw))

    return ors_scaled.round(2)


# =====================================================
# 6. CREDIT RATING ASSIGNMENT
# =====================================================

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
# 7. SAMPLE DATA GENERATION (DEMO)
# =====================================================

np.random.seed(42)
n = 50

survey_df = pd.DataFrame({
    "E1": np.random.randint(1,6,n),
    "E2": np.random.randint(1,6,n),
    "E3": np.random.randint(1,6,n),
    "E4": np.random.randint(1,6,n),

    "EM1": np.random.randint(1,6,n),
    "EM2": np.random.randint(1,6,n),
    "EM3": np.random.randint(1,6,n),
    "EM4": np.random.randint(1,6,n),

    "I1": np.random.randint(1,6,n),
    "I2": np.random.randint(1,6,n),
    "I3": np.random.randint(1,6,n),
    "I4": np.random.randint(1,6,n),

    "P1": np.random.randint(1,6,n),
    "P2": np.random.randint(1,6,n),
    "P3": np.random.randint(1,6,n),
    "P4": np.random.randint(1,6,n),
})

# Fake financial outcome (e.g., revenue growth)
financial_outcome = np.random.normal(0.1, 0.03, n)


# =====================================================
# 8. COMPUTE DIMENSIONS
# =====================================================

entropy = calculate_dimension_score(survey_df, ["E1","E2","E3","E4"], reverse=True)
empathy = calculate_dimension_score(survey_df, ["EM1","EM2","EM3","EM4"])
identity = calculate_dimension_score(survey_df, ["I1","I2","I3","I4"])
purpose = calculate_dimension_score(survey_df, ["P1","P2","P3","P4"])

df_dims = pd.DataFrame({
    "Entropy": entropy,
    "Empathy": empathy,
    "Identity": identity,
    "Purpose": purpose
})

# Reliability check
alpha_entropy = cronbach_alpha(survey_df[["E1","E2","E3","E4"]])
alpha_empathy = cronbach_alpha(survey_df[["EM1","EM2","EM3","EM4"]])
alpha_identity = cronbach_alpha(survey_df[["I1","I2","I3","I4"]])
alpha_purpose = cronbach_alpha(survey_df[["P1","P2","P3","P4"]])

print("Reliability (Cronbach Alpha)")
print("Entropy:", round(alpha_entropy,3))
print("Empathy:", round(alpha_empathy,3))
print("Identity:", round(alpha_identity,3))
print("Purpose:", round(alpha_purpose,3))


# =====================================================
# 9. COMPUTE RCS
# =====================================================

rcs, betas, r2 = compute_rcs(df_dims, financial_outcome)

print("\nRegression Betas:", betas)
print("R-squared:", round(r2,3))


# =====================================================
# 10. COMPUTE ORS (SIMULATED RISK DATA)
# =====================================================

risk_df = pd.DataFrame({
    "RevenueVolatility": np.random.rand(n),
    "LeadershipChurn": np.random.rand(n),
    "StrategyDrift": np.random.rand(n),
    "TalentFlightRisk": np.random.rand(n)
})

ors = compute_ors(risk_df)


# =====================================================
# 11. FINAL RATING
# =====================================================

final_rcs = rcs.mean()
final_ors = ors.mean()
rating = assign_rating(final_rcs, final_ors)

print("\nFinal RCS:", round(final_rcs,2))
print("Final ORS:", round(final_ors,2))
print("Organizational Credit Rating:", rating)


# =====================================================
# 12. VISUALIZATION
# =====================================================

plt.figure()
plt.plot(rcs.values)
plt.title("RCS Distribution")
plt.xlabel("Observation")
plt.ylabel("RCS Score")
plt.show()

plt.figure()
plt.scatter(rcs, ors)
plt.title("RCS vs ORS")
plt.xlabel("RCS")
plt.ylabel("ORS")
plt.show()
