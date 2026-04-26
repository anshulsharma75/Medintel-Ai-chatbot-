import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.helpers import card_html, tag_html

def render():
    st.title("📈 Personalized Baseline Deviation")
    st.markdown(
        tag_html("User-Specific Tracking", "purple") +
        tag_html("Z-Score Analysis", "green"),
        unsafe_allow_html=True
    )
    st.markdown("---")

    st.markdown("""
    <div style='background:rgba(167,139,250,0.06);border:1px solid rgba(167,139,250,0.2);
                 border-radius:10px;padding:14px;margin-bottom:20px;font-size:13px;
                 color:rgba(226,240,249,0.8);line-height:1.7;'>
        <strong style='color:#a78bfa;'>How it works:</strong>
        MedIntel tracks each user's individual vitals history and computes
        <em>personal baselines</em>. A reading that's "normal" for one person
        may be abnormal for another. Deviations are measured in standard deviations (σ).
    </div>
    """, unsafe_allow_html=True)

    # ── Vitals history ────────────────────────────────────────────────────────
    days = pd.date_range(end=pd.Timestamp.today(), periods=14, freq='D')
    np.random.seed(7)

    data = {
        "Date": days,
        "Temperature": [36.6,36.7,36.5,36.8,36.6,36.7,36.9,37.2,37.8,38.5,39.0,39.2,39.1,39.4],
        "SpO2":        [99,99,98,99,99,98,98,97,97,96,96,96,95,96],
        "Heart Rate":  [68,70,72,69,71,73,75,80,85,92,96,98,97,98],
        "Systolic BP": [115,116,114,118,115,117,116,118,120,119,118,119,120,118],
    }
    df = pd.DataFrame(data)

    # Baselines (personal average from first 7 days)
    baselines = {
        "Temperature": 36.67,
        "SpO2": 98.7,
        "Heart Rate": 71.1,
        "Systolic BP": 115.9,
    }
    stds = {
        "Temperature": 0.14,
        "SpO2": 0.49,
        "Heart Rate": 2.1,
        "Systolic BP": 1.2,
    }

    vital = st.selectbox("Select Vital Sign", list(baselines.keys()))

    vals     = df[vital].tolist()
    baseline = baselines[vital]
    std      = stds[vital]
    z_scores = [(v - baseline) / std for v in vals]

    # Color by severity
    colors = []
    for z in z_scores:
        if abs(z) < 1: colors.append("#00e5c3")
        elif abs(z) < 2: colors.append("#f59e0b")
        else: colors.append("#ff6b4a")

    col1, col2 = st.columns([1.6, 1])

    with col1:
        st.markdown(f"**{vital} — 14-Day Trend vs Personal Baseline**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df[vital],
            mode='lines+markers',
            name=vital,
            line=dict(color='#a78bfa', width=2),
            marker=dict(color=colors, size=8, line=dict(width=0))
        ))
        fig.add_hline(y=baseline, line_dash="dot", line_color="#00e5c3",
                      annotation_text=f"Baseline {baseline}", annotation_font_color="#00e5c3")
        fig.add_hline(y=baseline + 2*std, line_dash="dash", line_color="#f59e0b",
                      annotation_text="+2σ", annotation_font_color="#f59e0b")
        fig.add_hline(y=baseline - 2*std, line_dash="dash", line_color="#f59e0b")
        fig.update_layout(
            paper_bgcolor='#040d14', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            xaxis=dict(showgrid=False, color='#5b7a91'),
            yaxis=dict(showgrid=False, color='#5b7a91'),
            legend=dict(bgcolor='#0b1f2e', bordercolor='#1a3347'),
            margin=dict(l=10, r=20, t=20, b=10),
            height=280
        )
        st.plotly_chart(fig, use_container_width=True)

        # Z-score bars
        st.markdown(f"**Z-Score Deviation (σ from personal baseline)**")
        fig2 = go.Figure(go.Bar(
            x=[str(d.strftime("%d %b")) for d in days],
            y=z_scores,
            marker=dict(color=colors, line=dict(width=0))
        ))
        fig2.add_hline(y=2,  line_dash="dot", line_color="#f59e0b")
        fig2.add_hline(y=-2, line_dash="dot", line_color="#f59e0b")
        fig2.update_layout(
            paper_bgcolor='#040d14', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            xaxis=dict(showgrid=False, color='#5b7a91'),
            yaxis=dict(showgrid=False, color='#5b7a91', title="σ"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=200
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("**Current Status**")
        latest_z = z_scores[-1]
        level = "Normal" if abs(latest_z) < 1 else "Warning" if abs(latest_z) < 2 else "Critical"
        level_color = "#00e5c3" if level == "Normal" else "#f59e0b" if level == "Warning" else "#ff6b4a"

        st.markdown(card_html(f"""
            <div style='text-align:center;padding:10px 0;'>
                <div style='font-family:monospace;font-size:11px;color:#5b7a91;margin-bottom:8px;'>
                    LATEST Z-SCORE</div>
                <div style='font-size:42px;font-weight:700;color:{level_color};'>
                    {latest_z:+.1f}σ</div>
                <div style='font-size:14px;color:{level_color};margin-top:4px;font-weight:600;'>
                    {level}</div>
                <div style='font-size:12px;color:#5b7a91;margin-top:8px;'>
                    Current: {vals[-1]} &nbsp;|&nbsp; Baseline: {baseline}
                </div>
            </div>
        """, variant="accent" if level == "Normal" else "warn"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**All Vitals — Deviation Summary**")
        for v_name, b in baselines.items():
            current = data[v_name][-1]
            z = (current - b) / stds[v_name]
            color = "#00e5c3" if abs(z) < 1 else "#f59e0b" if abs(z) < 2 else "#ff6b4a"
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
                         padding:8px 0;border-bottom:1px solid #1a3347;font-size:12px;'>
                <span style='color:rgba(226,240,249,0.7);'>{v_name}</span>
                <span style='color:{color};font-family:monospace;'>{z:+.1f}σ</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(card_html("""
            <div style='font-size:11px;color:#5b7a91;font-family:monospace;line-height:2;'>
                🟢 < 1σ = Normal<br>
                🟡 1–2σ = Watch<br>
                🔴 > 2σ = Alert
            </div>
        """), unsafe_allow_html=True)
