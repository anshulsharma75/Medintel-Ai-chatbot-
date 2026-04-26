import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.helpers import card_html, tag_html

# ── Core self-doubt logic ────────────────────────────────────────────────────
def compute_self_doubt(symptoms: list[str], confidence_scores: dict) -> dict:
    """
    Computes ambiguity between top-2 diagnoses.
    Replace with: actual model softmax output + entropy calculation.
    """
    sorted_diag = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)
    top1, top2 = sorted_diag[0], sorted_diag[1]
    gap = top1[1] - top2[1]
    confusion = round((1 - gap / 100) * 100, 1)
    entropy = round(-sum((v/100) * np.log((v/100)+1e-9) for v in confidence_scores.values()), 3)

    # Flag self-doubt if gap < 15%
    triggered = gap < 15

    return {
        "top1": top1,
        "top2": top2,
        "gap": gap,
        "confusion": confusion,
        "entropy": entropy,
        "triggered": triggered,
        "recommendation": "Chest X-Ray + CRP test before prescribing" if triggered else "Proceed with primary diagnosis",
        "reason": f"Only {gap:.0f}% gap between {top1[0]} ({top1[1]}%) and {top2[0]} ({top2[1]}%). Cannot differentiate reliably.",
    }


def render():
    st.title("🧠 Self-Doubt Engine")
    st.markdown(
        tag_html("XAI Feature", "green") +
        tag_html("Entropy-Based", "purple") +
        tag_html("Unique to MedIntel", "orange"),
        unsafe_allow_html=True
    )
    st.markdown("---")
    st.markdown("""
    <div style='background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.2);
                 border-radius:10px;padding:14px;margin-bottom:20px;font-size:13px;
                 color:rgba(226,240,249,0.8);line-height:1.7;'>
        <strong style='color:#f59e0b;'>What is the Self-Doubt Engine?</strong><br>
        Unlike traditional AI that always gives an answer with false confidence,
        MedIntel's Self-Doubt Engine monitors the <em>gap between top diagnoses</em>.
        When the gap is small (ambiguous), the AI explicitly flags its own uncertainty
        and asks for more tests — just like a careful doctor would.
    </div>
    """, unsafe_allow_html=True)

    # ── Interactive Symptom Selector ─────────────────────────────────────────
    st.markdown("### ⚙️ Simulate Self-Doubt Engine")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Select Symptoms**")
        fever     = st.checkbox("High Fever (≥38.5°C)", value=True)
        cough     = st.checkbox("Dry Cough", value=True)
        bodyache  = st.checkbox("Body Aches / Myalgia", value=True)
        chest     = st.checkbox("Chest Tightness", value=True)
        breath    = st.checkbox("Shortness of Breath", value=False)
        runny     = st.checkbox("Runny Nose / Congestion", value=False)
        sore      = st.checkbox("Sore Throat", value=False)

        symptoms = [s for s, v in {
            "Fever": fever, "Dry Cough": cough, "Body Aches": bodyache,
            "Chest Tightness": chest, "Breathlessness": breath,
            "Runny Nose": runny, "Sore Throat": sore
        }.items() if v]

    with col2:
        st.markdown("**Adjust Diagnosis Confidence**")
        flu_conf  = st.slider("Influenza A", 0, 100, 78)
        pneu_conf = st.slider("Pneumonia (CAP)", 0, 100, 69)
        atyp_conf = st.slider("Atypical Pneumonia", 0, 100, 41)
        bron_conf = st.slider("Bronchitis", 0, 100, 22)

    # Normalize to 0-100 range (keep relative)
    confidence_scores = {
        "Influenza A": flu_conf,
        "Pneumonia": pneu_conf,
        "Atypical Pneumonia": atyp_conf,
        "Bronchitis": bron_conf,
    }

    result = compute_self_doubt(symptoms, confidence_scores)

    st.markdown("---")
    st.markdown("### 🔍 Self-Doubt Analysis Result")

    # Alert state
    if result["triggered"]:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(245,158,11,0.1),rgba(255,107,74,0.06));
                     border:1px solid rgba(245,158,11,0.3);border-left:4px solid #f59e0b;
                     border-radius:10px;padding:18px;margin-bottom:16px;'>
            <div style='color:#f59e0b;font-weight:700;font-size:15px;margin-bottom:10px;'>
                ⚡ SELF-DOUBT TRIGGERED
            </div>
            <div style='font-size:13px;color:rgba(226,240,249,0.85);font-style:italic;line-height:1.8;'>
                "{result['reason']}"
            </div>
            <div style='margin-top:12px;background:rgba(0,0,0,0.2);border-radius:8px;padding:10px;'>
                <div style='font-size:12px;color:#f59e0b;font-weight:600;'>⚕ Recommended Action:</div>
                <div style='font-size:13px;color:#e2f0f9;margin-top:4px;'>{result['recommendation']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"✅ No doubt triggered. Confidence gap is {result['gap']:.0f}%. Proceed with: **{result['top1'][0]}**")

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Top Diagnosis", result["top1"][0], f"{result['top1'][1]}% confidence")
    with m2:
        st.metric("2nd Hypothesis", result["top2"][0], f"{result['top2'][1]}%")
    with m3:
        st.metric("Confidence Gap", f"{result['gap']:.0f}%",
                  "⚠ Too small" if result["triggered"] else "✓ Safe",
                  delta_color="inverse" if result["triggered"] else "normal")
    with m4:
        st.metric("Entropy Score", str(result["entropy"]),
                  "High ambiguity" if result["entropy"] > 1.0 else "Low ambiguity",
                  delta_color="inverse" if result["entropy"] > 1.0 else "normal")

    # Polar chart — symptom overlap
    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Symptom Profile Overlap (Flu vs Pneumonia)**")
        categories = ["Fever", "Cough", "Body Ache", "Chest Pain", "Breathlessness", "Fatigue"]
        flu_vals  = [0.9, 0.7, 0.9, 0.4, 0.3, 0.8]
        pneu_vals = [0.8, 0.8, 0.5, 0.8, 0.7, 0.7]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=flu_vals + [flu_vals[0]], theta=categories + [categories[0]],
            fill='toself', name='Influenza A',
            line=dict(color='#ff6b4a'), fillcolor='rgba(255,107,74,0.15)'))
        fig.add_trace(go.Scatterpolar(r=pneu_vals + [pneu_vals[0]], theta=categories + [categories[0]],
            fill='toself', name='Pneumonia',
            line=dict(color='#f59e0b'), fillcolor='rgba(245,158,11,0.1)'))
        fig.update_layout(
            polar=dict(
                bgcolor='#0b1f2e',
                radialaxis=dict(visible=True, range=[0, 1], gridcolor='#1a3347', color='#5b7a91'),
                angularaxis=dict(gridcolor='#1a3347', color='#5b7a91')
            ),
            paper_bgcolor='#040d14', plot_bgcolor='#040d14',
            font=dict(color='#e2f0f9', family='Sora'),
            legend=dict(bgcolor='#0b1f2e', bordercolor='#1a3347'),
            margin=dict(l=30, r=30, t=20, b=20),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Shaded area overlap = source of AI confusion")

    with col_b:
        st.markdown("**Confidence Distribution**")
        diags = list(confidence_scores.keys())
        vals  = list(confidence_scores.values())
        colors = ["#ff6b4a", "#f59e0b", "#a78bfa", "#00e5c3"]

        fig2 = go.Figure(go.Bar(
            x=diags, y=vals,
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{v}%" for v in vals],
            textposition='outside',
            textfont=dict(color='#e2f0f9')
        ))
        fig2.add_hline(y=60, line_dash="dot", line_color="#5b7a91",
                       annotation_text="60% threshold", annotation_font_color="#5b7a91")
        fig2.update_layout(
            paper_bgcolor='#040d14', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, range=[0, 110]),
            margin=dict(l=10, r=10, t=20, b=10),
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Self-doubt triggers when gap between top-2 < 15%")
