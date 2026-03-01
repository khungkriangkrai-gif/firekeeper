import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from mpl_toolkits.mplot3d import Axes3D

# --------------------------
# Core Model
# --------------------------

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


@dataclass
class ThermodynamicLayer:
    entropy: float
    empathy: float
    alpha: float = 0.6

    def effective_entropy(self):
        return max(0, self.entropy - self.alpha * self.empathy)


@dataclass
class BioInformationLayer:
    identity_coherence: float


@dataclass
class MeaningLayer:
    purpose_clarity: float


class NICSModel:

    def __init__(self,
                 beta_identity=0.04,
                 beta_purpose=0.05,
                 beta_entropy=0.06):
        self.beta_identity = beta_identity
        self.beta_purpose = beta_purpose
        self.beta_entropy = beta_entropy

    def compute(self, thermo, bio, meaning):

        eff_entropy = thermo.effective_entropy()

        linear_score = (
            self.beta_identity * bio.identity_coherence +
            self.beta_purpose * meaning.purpose_clarity -
            self.beta_entropy * eff_entropy
        )

        coherence = sigmoid(linear_score)
        nics_score = round(coherence * 100, 2)

        return nics_score, eff_entropy

    @staticmethod
    def classify(score):
        if score < 40:
            return "Collapse"
        elif score < 70:
            return "Survival"
        else:
            return "Resilience"


# --------------------------
# Streamlit UI
# --------------------------

st.set_page_config(layout="wide")
st.title("🔥 FireKeeper Unified Theory Dashboard")
st.subheader("NICS Index & Phase Portrait Visualization")

col1, col2 = st.columns(2)

with col1:
    entropy = st.slider("Entropy", 0, 100, 70)
    empathy = st.slider("Empathy", 0, 100, 40)
    identity = st.slider("Identity Coherence", 0, 100, 60)
    purpose = st.slider("Purpose Clarity", 0, 100, 75)

# Model computation
thermo = ThermodynamicLayer(entropy, empathy)
bio = BioInformationLayer(identity)
meaning = MeaningLayer(purpose)

model = NICSModel()
nics_score, eff_entropy = model.compute(thermo, bio, meaning)
state = model.classify(nics_score)

with col2:
    st.metric("NICS Score", nics_score)
    st.metric("Effective Entropy", round(eff_entropy, 2))
    st.metric("System State", state)

# --------------------------
# 2D Sensitivity Plot
# --------------------------

st.subheader("📈 NICS Sensitivity to Entropy")

entropy_range = np.linspace(0, 100, 200)
scores = []

for e in entropy_range:
    temp = ThermodynamicLayer(e, empathy)
    score, _ = model.compute(temp, bio, meaning)
    scores.append(score)

fig1 = plt.figure()
plt.plot(entropy_range, scores)
plt.xlabel("Entropy")
plt.ylabel("NICS Score")
plt.title("NICS vs Entropy")
st.pyplot(fig1)

# --------------------------
# 3D Phase Portrait
# --------------------------

st.subheader("🌌 3D Phase Portrait (Entropy–Identity–Purpose)")

E = np.linspace(0, 100, 20)
I = np.linspace(0, 100, 20)
P = np.linspace(0, 100, 20)

E_grid, I_grid = np.meshgrid(E, I)
P_fixed = purpose

Z = []

for i in range(len(E)):
    row = []
    for j in range(len(I)):
        thermo = ThermodynamicLayer(E_grid[i][j], empathy)
        bio = BioInformationLayer(I_grid[i][j])
        meaning = MeaningLayer(P_fixed)
        score, _ = model.compute(thermo, bio, meaning)
        row.append(score)
    Z.append(row)

Z = np.array(Z)

fig2 = plt.figure()
ax = fig2.add_subplot(111, projection='3d')
ax.plot_surface(E_grid, I_grid, Z)

ax.set_xlabel("Entropy")
ax.set_ylabel("Identity")
ax.set_zlabel("NICS Score")

st.pyplot(fig2)

st.caption("Model: Nonlinear bounded coherence model using sigmoid stability mapping.")
