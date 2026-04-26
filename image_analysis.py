import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.helpers import card_html, tag_html

SHAP_DATA = [
    {"feature": "Fever (39.4°C)",     "shap": +0.88, "direction": "↑ Flu/Pneumonia"},
    {"feature": "Body Aches",          "shap": +0.72, "direction": "↑ Influenza"},
    {"feature": "Dry Cough",           "shap": +0.58, "direction": "↑ Both"},
    {"feature": "Rapid Onset < 24h",   "shap": +0.44, "direction": "↑ Influenza"},
    {"feature": "SpO2 96%",            "shap": -0.43, "direction": "↓ Away from mild"},
    {"feature": "No Breathlessness",   "shap": -0.35, "direction": "↓ Against severe pneumonia"},
    {"feature": "Age 22",              "shap": -0.21, "direction": "↓ Lower severity"},
    {"feature": "No Chest X-Ray",      "shap":  0.00, "direction": "N/A — data missing"},
]

REASONING_STEPS = [
    ("Symptom Pattern Recognition",
     "Patient presents with sudden-onset high fever (39.4°C), diffuse myalgia, and dry cough. "
     "This triad is strongly associated with systemic viral infection, particularly Influenza A."),
    ("Competing Hypothesis Evaluation",
     "Chest tightness and SpO2 at 96% introduce ambiguity. These findings, while mild, "
     "overlap with early community-acquired pneumonia. Model flags this as a competing hypothesis."),
    ("Missing Data Penalty",
     "No chest X-ray available. This is the single most important discriminating test "
     "between Flu and Pneumonia. Absence of this data increases uncertainty score by +0.18."),
    ("Self-Doubt Activation",
     "Confidence gap between Influenza A (78%) and Pneumonia (69%) is only 9%. "
     "This falls below the 15% safe threshold. Self-Doubt Engine activates. "
     "AI explicitly withholds confident recommendation."),
    ("Final Recommendation",
     "Primary hypothesis: Influenza A. However, pneumonia CANNOT be excluded. "
     "Recommend: CRP blood test + Chest X-Ray before any prescription. "
     "Do NOT prescribe antibiotics without ruling out bacterial pneumonia."),
]


def render():
    st.title("🔍 XAI Decision Explainer")
    st.markdown(
        tag_html("SHAP Values", "green") +
        tag_html("Human-Like Reasoning", "purple") +
        tag_html("Trustworthy AI", "orange"),
        unsafe_allow_html=True
    )
    st.markdown("---")

    col_l, col_r = st.columns([1.2, 1])

    with col_l:
        st.markdown("### 📊 Feature Importance (SHAP)")
        features = [d["feature"] for d in SHAP_DATA]
        shap_vals = [d["shap"] for d in SHAP_DATA]
        colors = ["#ff6b4a" if v > 0 else "#00e5c3" for v in shap_vals]

        fig = go.Figure(go.Bar(
            x=shap_vals,
            y=features,
            orientation='h',
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{v:+.2f}" for v in shap_vals],
            textposition='outside',
            textfont=dict(color='#e2f0f9', size=11)
        ))
        fig.add_vline(x=0, line_color='#5b7a91', line_width=1)
        fig.update_layout(
            paper_bgcolor='#040d14', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            xaxis=dict(showgrid=False, range=[-0.6, 1.1], title="SHAP value", color='#5b7a91'),
            yaxis=dict(showgrid=False, autorange='reversed'),
            margin=dict(l=10, r=80, t=10, b=10),
            height=340
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div style='font-size:12px;color:#5b7a91;margin-top:-10px;margin-bottom:16px;'>
            🔴 Red = pushes toward diagnosis &nbsp;|&nbsp; 🟢 Green = pushes against
        </div>
        """, unsafe_allow_html=True)

        # Feature table
        with st.expander("View Full SHAP Table"):
            st.markdown("""
            <table style='width:100%;font-size:12px;border-collapse:collapse;'>
                <tr style='color:#5b7a91;font-family:monospace;font-size:11px;'>
                    <th style='text-align:left;padding:6px 4px;border-bottom:1px solid #1a3347;'>Feature</th>
                    <th style='text-align:right;padding:6px 4px;border-bottom:1px solid #1a3347;'>SHAP</th>
                    <th style='text-align:right;padding:6px 4px;border-bottom:1px solid #1a3347;'>Direction</th>
                </tr>
            """ + "".join([f"""
                <tr>
                    <td style='padding:6px 4px;border-bottom:1px solid #0b1f2e;
                               color:rgba(226,240,249,0.8);'>{d['feature']}</td>
                    <td style='text-align:right;padding:6px 4px;border-bottom:1px solid #0b1f2e;
                               font-family:monospace;
                               color:{"#ff6b4a" if d["shap"] > 0 else "#00e5c3"};'>
                        {d['shap']:+.2f}</td>
                    <td style='text-align:right;padding:6px 4px;border-bottom:1px solid #0b1f2e;
                               font-size:11px;color:#5b7a91;'>{d['direction']}</td>
                </tr>
            """ for d in SHAP_DATA]) + "</table>",
            unsafe_allow_html=True)

    with col_r:
        st.markdown("### 🧠 Human-Like Reasoning Chain")
        for i, (title, body) in enumerate(REASONING_STEPS, 1):
            is_doubt = "Self-Doubt" in title
            border = "rgba(245,158,11,0.4)" if is_doubt else "rgba(0,229,195,0.2)"
            num_color = "#f59e0b" if is_doubt else "#00e5c3"
            st.markdown(f"""
            <div style='display:flex;gap:12px;margin-bottom:14px;'>
                <div style='width:24px;height:24px;border-radius:50%;
                             background:rgba(0,229,195,0.08);
                             border:1px solid {border};
                             color:{num_color};font-family:monospace;font-size:11px;
                             display:flex;align-items:center;justify-content:center;
                             flex-shrink:0;margin-top:2px;'>{i}</div>
                <div>
                    <div style='font-size:12px;font-weight:600;color:#e2f0f9;margin-bottom:4px;'>
                        {title}</div>
                    <div style='font-size:12px;color:rgba(226,240,249,0.7);line-height:1.7;'>
                        {body}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**📋 Integration: Real SHAP**")
        with st.expander("How to use real SHAP values"):
            st.code("""
import shap
import numpy as np

# After training your model:
explainer = shap.TreeExplainer(your_model)  # or shap.Explainer()
shap_values = explainer.shap_values(X_patient)

# For a single patient:
shap.plots.waterfall(explainer(X_patient)[0])

# Feature importance:
shap.summary_plot(shap_values, X_patient,
                  feature_names=feature_names)
            """, language="python")
