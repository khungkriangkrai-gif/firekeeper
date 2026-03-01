import streamlit as st
import numpy as np
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Frame
from reportlab.platypus import PageTemplate
from reportlab.platypus import KeepTogether
import tempfile
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

st.set_page_config(layout="wide")

# --------------------------------------------------
# EXECUTIVE THEME SWITCH
# --------------------------------------------------

theme = st.sidebar.selectbox("Executive Theme", ["Dark Boardroom", "Light Policy"])
presentation_mode = st.sidebar.toggle("4K Presentation Mode")
animate_phase = st.sidebar.toggle("Animated Phase Portrait")
export_pdf = st.sidebar.button("Export Executive PDF Snapshot")

if theme == "Dark Boardroom":
    bg = "#0f172a"
    panel = "#1e293b"
    text = "#e2e8f0"
    accent = "#22c55e"
else:
    bg = "#f8fafc"
    panel = "#ffffff"
    text = "#0f172a"
    accent = "#15803d"

max_width = "1800px" if presentation_mode else "1200px"
title_size = "56px" if presentation_mode else "36px"

st.markdown(f"""
<style>
body {{
    background-color: {bg};
}}
.main {{
    background-color: {bg};
    max-width: {max_width};
    margin: auto;
}}
.metric-card {{
    background-color: {panel};
    padding: 40px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 6px 30px rgba(0,0,0,0.3);
}}
.metric-value {{
    font-size: 48px;
    font-weight: 600;
    color: {accent};
}}
.metric-label {{
    font-size: 14px;
    letter-spacing: 1px;
    color: #94a3b8;
}}
h1 {{
    font-size: {title_size};
    color: {text};
}}
h2,h3,h4 {{
    color: {text};
}}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(f"<h1>🔥 FireKeeper Unified Theory</h1>", unsafe_allow_html=True)
st.markdown("### Executive Resilience Intelligence Dashboard")

# --------------------------------------------------
# INPUT SLIDERS
# --------------------------------------------------

colA, colB, colC, colD = st.columns(4)
entropy = colA.slider("Entropy", 0, 100, 70)
empathy = colB.slider("Empathy", 0, 100, 40)
identity = colC.slider("Identity", 0, 100, 60)
purpose = colD.slider("Purpose", 0, 100, 75)

# --------------------------------------------------
# CORE MODEL
# --------------------------------------------------

effective_entropy = entropy - (empathy * 0.4)
nics_score = (
    0.35 * purpose +
    0.25 * identity +
    0.25 * empathy +
    0.15 * (100 - effective_entropy)
)

if nics_score > 75:
    system_state = "Resilient"
elif nics_score > 50:
    system_state = "Adaptive"
else:
    system_state = "At Risk"

# --------------------------------------------------
# EXECUTIVE KPI CARDS
# --------------------------------------------------

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">NICS SCORE</div>
        <div class="metric-value">{nics_score:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">EFFECTIVE ENTROPY</div>
        <div class="metric-value">{effective_entropy:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">SYSTEM STATE</div>
        <div class="metric-value">{system_state}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# GAUGE
# --------------------------------------------------

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=nics_score,
    number={'font': {'size': 50}},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': accent},
        'bgcolor': panel
    }
))

fig_gauge.update_layout(
    paper_bgcolor=bg,
    font={'color': text}
)

# --------------------------------------------------
# 3D SURFACE
# --------------------------------------------------

x = np.linspace(0, 100, 30)
y = np.linspace(0, 100, 30)
X, Y = np.meshgrid(x, y)
Z = 0.4 * Y + 0.6 * X - 0.002 * (X * Y)

fig_surface = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale="Viridis")])

fig_surface.update_layout(
    paper_bgcolor=bg,
    scene=dict(
        xaxis=dict(backgroundcolor=bg),
        yaxis=dict(backgroundcolor=bg),
        zaxis=dict(backgroundcolor=bg),
    )
)

# --------------------------------------------------
# PHASE PORTRAIT (Animated Option)
# --------------------------------------------------

theta = np.linspace(0, 4*np.pi, 200)
r = np.linspace(10, 50, 200)

x_phase = r * np.cos(theta)
y_phase = r * np.sin(theta)

fig_phase = go.Figure()

if animate_phase:
    frames = []
    for i in range(20, len(theta), 5):
        frames.append(go.Frame(
            data=[go.Scatter(x=x_phase[:i], y=y_phase[:i], mode="lines")]
        ))

    fig_phase.add_trace(go.Scatter(x=x_phase[:20], y=y_phase[:20], mode="lines"))
    fig_phase.frames = frames
    fig_phase.update_layout(
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None])]
        )]
    )
else:
    fig_phase.add_trace(go.Scatter(x=x_phase, y=y_phase, mode="lines"))

fig_phase.update_layout(
    paper_bgcolor=bg,
    plot_bgcolor=bg,
    font={'color': text}
)

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------

col_left, col_right = st.columns(2)

with col_left:
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.plotly_chart(fig_phase, use_container_width=True)

with col_right:
    st.plotly_chart(fig_surface, use_container_width=True)

# --------------------------------------------------
# PDF EXPORT
# --------------------------------------------------

if export_pdf:
    tmpdir = tempfile.mkdtemp()
    image_path = os.path.join(tmpdir, "snapshot.png")
    fig_gauge.write_image(image_path)

    pdf_path = os.path.join(tmpdir, "Executive_Report.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    style = ParagraphStyle(
        name='Title',
        fontSize=18,
        textColor=colors.black
    )

    elements.append(Paragraph("FireKeeper Executive Snapshot", style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(RLImage(image_path, width=4*inch, height=4*inch))

    doc.build(elements)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Executive PDF",
            data=f,
            file_name="FireKeeper_Executive_Report.pdf",
            mime="application/pdf"
        )
