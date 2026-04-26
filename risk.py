import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.helpers import card_html, tag_html, metric_delta

def render():
    st.title("🩺 Health Intelligence Dashboard")
    st.markdown(
        tag_html("Active Session", "green") +
        tag_html("Moderate Risk", "orange") +
        tag_html("Self-Doubt Triggered", "red"),
        unsafe_allow_html=True
    )
    st.markdown("---")

    # ── Top Metrics ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Model Confidence", "78%", "-6% vs baseline",
                  delta_color="inverse")
    with c2:
        st.metric("Risk Score", "4.2 / 10", "▲ Moderate", delta_color="inverse")
    with c3:
        st.metric("Drift Index", "0.12", "✓ Within threshold")
    with c4:
        st.metric("Baseline Deviation", "+2.4σ", "Temp + SpO2 anomaly",
                  delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two column layout ───────────────────────────────────────────────────
    left, right = st.columns([1.2, 1])

    with left:
        # Self-Doubt Alert
        st.markdown(card_html("""
            <div style='color:#f59e0b;font-weight:600;margin-bottom:8px;font-size:13px;'>
                ⚡ Self-Doubt Engine — Alert
            </div>
            <div style='font-size:12px;color:rgba(226,240,249,0.8);font-style:italic;line-height:1.7;'>
                "High overlap between <strong style='color:#ff6b4a'>Influenza</strong> &
                <strong style='color:#f59e0b'>Pneumonia</strong>.
                Symptom vectors are 71% similar. I am NOT confident in differentiation.
                Recommend chest X-ray + CRP test before final diagnosis."
            </div>
            <div style='margin-top:10px;font-family:monospace;font-size:11px;color:#f59e0b;'>
                Confusion Score: 71% &nbsp;|&nbsp; Confidence Gap: 9%
            </div>
        """, variant="warn"), unsafe_allow_html=True)

        # Risk bar chart
        st.markdown("**Differential Diagnosis — Risk Breakdown**")
        diagnoses = ["Influenza A", "Pneumonia (CAP)", "Atypical Pneumonia", "Bronchitis", "Viral URTI"]
        scores    = [78, 69, 41, 22, 15]
        colors    = ["#ff6b4a", "#f59e0b", "#a78bfa", "#00e5c3", "#5b7a91"]

        fig = go.Figure(go.Bar(
            x=scores, y=diagnoses,
            orientation='h',
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{s}%" for s in scores],
            textposition='outside',
            textfont=dict(color='#e2f0f9', size=11)
        ))
        fig.update_layout(
            paper_bgcolor='#0b1f2e', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            xaxis=dict(showgrid=False, showticklabels=False, range=[0, 100]),
            yaxis=dict(showgrid=False),
            margin=dict(l=10, r=60, t=10, b=10),
            height=220
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        # Vitals summary
        st.markdown("**Current Vitals vs Baseline**")
        vitals = {
            "Temperature": ("39.4°C", "36.6°C", "🔴"),
            "SpO2":        ("96%",    "99%",    "🟡"),
            "Heart Rate":  ("98 bpm", "72 bpm", "🟡"),
            "BP":          ("118/78", "115/75", "🟢"),
        }
        for vital, (current, baseline, icon) in vitals.items():
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
                        padding:8px 0;border-bottom:1px solid #1a3347;font-size:13px;'>
                <span style='color:#5b7a91;'>{icon} {vital}</span>
                <span style='color:#e2f0f9;font-weight:500;'>{current}</span>
                <span style='color:#5b7a91;font-size:11px;font-family:monospace;'>
                    baseline: {baseline}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Mini sparkline
        st.markdown("**7-Day Temperature Trend**")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"]
        temps = [36.7, 36.9, 37.4, 38.8, 39.2, 39.1, 39.4]
        fig2 = go.Figure(go.Scatter(
            x=days, y=temps,
            mode='lines+markers',
            line=dict(color='#ff6b4a', width=2),
            marker=dict(color='#ff6b4a', size=6),
            fill='tozeroy',
            fillcolor='rgba(255,107,74,0.08)'
        ))
        fig2.add_hline(y=37.5, line_dash="dot", line_color="#00e5c3",
                       annotation_text="Baseline 37.5°C", annotation_font_color="#00e5c3")
        fig2.update_layout(
            paper_bgcolor='#0b1f2e', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, range=[35, 40.5]),
            margin=dict(l=10, r=10, t=10, b=10),
            height=180
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Primary Recommendation ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**🔍 AI Recommendation**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(card_html("""
            <div style='font-size:11px;color:#5b7a91;font-family:monospace;margin-bottom:6px;'>
                PRIMARY DIAGNOSIS</div>
            <div style='font-size:20px;color:#00e5c3;font-weight:600;'>Influenza Type A</div>
            <div style='font-size:12px;color:#5b7a91;margin-top:4px;'>Confidence: 78%</div>
        """, variant="accent"), unsafe_allow_html=True)
    with col2:
        st.markdown(card_html("""
            <div style='font-size:11px;color:#5b7a91;font-family:monospace;margin-bottom:6px;'>
                IMMEDIATE ACTION</div>
            <div style='font-size:13px;color:#f59e0b;font-weight:500;'>Chest X-Ray + CRP Test</div>
            <div style='font-size:12px;color:#5b7a91;margin-top:4px;'>Before prescribing antivirals</div>
        """, variant="warn"), unsafe_allow_html=True)
    with col3:
        st.markdown(card_html("""
            <div style='font-size:11px;color:#5b7a91;font-family:monospace;margin-bottom:6px;'>
                PHYSICIAN REVIEW</div>
            <div style='font-size:13px;color:#a78bfa;font-weight:500;'>Required — Ambiguity High</div>
            <div style='font-size:12px;color:#5b7a91;margin-top:4px;'>Cannot exclude pneumonia</div>
        """), unsafe_allow_html=True)
