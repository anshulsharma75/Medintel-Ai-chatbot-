import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from utils.helpers import card_html, tag_html

def render():
    st.title("🔄 Model Drift + Reality Check")
    st.markdown(
        tag_html("PSI Monitor", "green") +
        tag_html("KL Divergence", "purple") +
        tag_html("Auto Retrain Alert", "orange"),
        unsafe_allow_html=True
    )
    st.markdown("---")

    # ── Summary metrics ───────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        ("30d Accuracy",   "91.4%", "+0.2%",  "normal"),
        ("PSI Score",      "0.08",  "✓ Stable", "normal"),
        ("KL Divergence",  "0.12",  "⚠ Watch",  "inverse"),
        ("Last Retrain",   "12d ago","Scheduled in 3d", "off"),
        ("Reality Check",  "PASS",  "All checks green", "normal"),
    ]
    for col, (label, val, delta, dc) in zip([c1,c2,c3,c4,c5], metrics):
        with col:
            st.metric(label, val, delta, delta_color=dc)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        # Accuracy over time
        st.markdown("**Model Accuracy — Last 90 Days**")
        days = pd.date_range(end=pd.Timestamp.today(), periods=90, freq='D')
        np.random.seed(42)
        acc = np.clip(91 + np.cumsum(np.random.normal(0, 0.15, 90)), 85, 97)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days, y=acc,
            mode='lines',
            line=dict(color='#00e5c3', width=2),
            fill='tozeroy', fillcolor='rgba(0,229,195,0.07)',
            name="Accuracy"
        ))
        fig.add_hline(y=88, line_dash="dot", line_color="#ff6b4a",
                      annotation_text="Min threshold 88%", annotation_font_color="#ff6b4a")
        fig.update_layout(
            paper_bgcolor='#040d14', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            xaxis=dict(showgrid=False, color='#5b7a91'),
            yaxis=dict(showgrid=False, color='#5b7a91', range=[80, 100]),
            margin=dict(l=10, r=10, t=10, b=10), height=240
        )
        st.plotly_chart(fig, use_container_width=True)

        # PSI over time
        st.markdown("**PSI Score — Population Stability Index**")
        psi_vals = np.clip(0.05 + np.cumsum(np.random.normal(0, 0.003, 90)), 0.01, 0.3)
        psi_colors = ['#ff6b4a' if v > 0.2 else '#f59e0b' if v > 0.1 else '#00e5c3' for v in psi_vals]

        fig2 = go.Figure(go.Scatter(
            x=days, y=psi_vals, mode='lines',
            line=dict(color='#a78bfa', width=2),
            fill='tozeroy', fillcolor='rgba(167,139,250,0.07)'
        ))
        fig2.add_hline(y=0.1,  line_dash="dot", line_color="#f59e0b",
                       annotation_text="Warning 0.10", annotation_font_color="#f59e0b")
        fig2.add_hline(y=0.25, line_dash="dot", line_color="#ff6b4a",
                       annotation_text="Critical 0.25", annotation_font_color="#ff6b4a")
        fig2.update_layout(
            paper_bgcolor='#040d14', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            xaxis=dict(showgrid=False, color='#5b7a91'),
            yaxis=dict(showgrid=False, color='#5b7a91'),
            margin=dict(l=10, r=10, t=10, b=10), height=220
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        # Reality Check panel
        st.markdown("**✅ Reality Check — System Health**")
        checks = [
            ("Prediction Calibration",    True,  "ECE = 0.04"),
            ("Class Distribution Stable", True,  "PSI = 0.08"),
            ("Feature Drift",             True,  "All features stable"),
            ("Label Shift",               False, "⚠ Slight shift in pneumonia labels"),
            ("Data Quality",              True,  "No nulls or outliers"),
            ("Latency < 500ms",           True,  "Avg: 312ms"),
            ("API Uptime",                True,  "99.8% (30d)"),
        ]
        for name, passed, detail in checks:
            icon  = "✅" if passed else "⚠️"
            color = "#00e5c3" if passed else "#f59e0b"
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
                         padding:9px 0;border-bottom:1px solid #1a3347;'>
                <span style='font-size:13px;color:rgba(226,240,249,0.85);'>{icon} {name}</span>
                <span style='font-family:monospace;font-size:11px;color:{color};'>{detail}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🔁 Retrain Schedule**")
        st.markdown(card_html("""
            <div style='font-size:12px;color:rgba(226,240,249,0.8);line-height:2;'>
                <div style='color:#a78bfa;font-weight:600;margin-bottom:8px;'>Auto-Retrain Policy</div>
                🔄 Trigger: PSI > 0.25 OR Accuracy < 88%<br>
                📅 Scheduled: Every 15 days<br>
                ⏳ Next retrain: <strong style='color:#00e5c3;'>3 days</strong><br>
                📊 Training data: Last 6 months<br>
                🧪 Validation: Hold-out 20% + clinical review<br>
            </div>
        """), unsafe_allow_html=True)

        if st.button("🚀 Trigger Manual Retrain", use_container_width=True):
            import time
            with st.spinner("Initiating retrain pipeline..."):
                time.sleep(2)
            st.success("✅ Retrain job queued. ETA: ~45 minutes. You'll be notified on completion.")
