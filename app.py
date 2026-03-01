import streamlit as st
import numpy as np
import plotly.graph_objects as go
import io
from datetime import datetime

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(layout="wide")

# =============================
# SIDEBAR CONTROLS
# =============================
st.sidebar.title("Executive Theme")

theme = st.sidebar.selectbox(
    "Theme Mode",
    ["Light Boardroom", "Dark Boardroom"]
)

presentation_4k = st.sidebar.toggle("4K Presentation Mode")
animated = st.sidebar.toggle("Animated Phase Portrait")

# =============================
# THEME CONFIG
# =============================
if theme == "Dark Boardroom":
    bg_color = "#0b1c2d"
    text_color = "white"
else:
    bg_color = "white"
    text_color = "black"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# MODEL (Example Dynamics)
# =============================
def compute_model(x):
    return x - x**3

x = np.linspace(-2, 2, 400)
y = compute_model(x)

# =============================
# PHASE PORTRAIT
# =============================
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(width=3),
        name="Phase Curve"
    )
)

fig.update_layout(
    template="plotly_dark" if theme == "Dark Boardroom" else "plotly_white",
    height=800 if presentation_4k else 500,
    title="Phase Portrait"
)

if animated:
    frames = []
    for shift in np.linspace(0, 2, 30):
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(
                        x=x,
                        y=compute_model(x + shift),
                        mode="lines"
                    )
                ]
            )
        )
    fig.frames = frames

st.plotly_chart(fig, use_container_width=True)

# =============================
# METRICS PANEL
# =============================
st.markdown("### Executive Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Stability Index", "0.87")

with col2:
    st.metric("Critical Threshold", "1.32")

with col3:
    st.metric("System Risk", "Moderate")

# =============================
# CLOUD-PROOF PDF EXPORT
# =============================
def generate_pdf():

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph("FireKeeper Executive Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"Generated: {datetime.now()}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Stability Index: 0.87", normal_style))
    elements.append(Paragraph("Critical Threshold: 1.32", normal_style))
    elements.append(Paragraph("System Risk: Moderate", normal_style))

    doc.build(elements)

    buffer.seek(0)
    return buffer

if st.button("Export Executive PDF Snapshot"):
    pdf = generate_pdf()

    st.download_button(
        label="Download PDF",
        data=pdf,
        file_name="FireKeeper_Executive_Report.pdf",
        mime="application/pdf"
    )
