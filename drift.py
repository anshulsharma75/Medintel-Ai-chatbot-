import streamlit as st
import plotly.graph_objects as go
from utils.helpers import card_html, tag_html

RISK_DATA = [
    {"name": "Influenza Type A",    "score": 78, "color": "#ff6b4a", "severity": "High"},
    {"name": "Pneumonia (CAP)",     "score": 69, "color": "#f59e0b", "severity": "High"},
    {"name": "Atypical Pneumonia",  "score": 41, "color": "#a78bfa", "severity": "Moderate"},
    {"name": "Acute Bronchitis",    "score": 22, "color": "#00e5c3", "severity": "Low"},
    {"name": "Viral URTI",          "score": 15, "color": "#5b7a91", "severity": "Low"},
]

def render():
    st.title("⚠️ Risk Analysis")
    st.markdown(
        tag_html("Differential Diagnosis", "orange") +
        tag_html("5 Conditions Evaluated", "green"),
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Primary verdict
    st.markdown(card_html("""
        <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;'>
            <div>
                <div style='font-family:monospace;font-size:11px;color:#5b7a91;margin-bottom:6px;'>
                    PRIMARY DIAGNOSIS</div>
                <div style='font-size:24px;color:#00e5c3;font-weight:700;'>Influenza Type A</div>
                <div style='font-size:13px;color:#5b7a91;margin-top:4px;'>
                    Confidence: 78% &nbsp;|&nbsp; Risk Level: <span style='color:#ff6b4a;'>HIGH</span>
                </div>
            </div>
            <div style='text-align:right;'>
                <div style='font-family:monospace;font-size:11px;color:#5b7a91;margin-bottom:6px;'>
                    OVERALL RISK SCORE</div>
                <div style='font-size:40px;color:#ff6b4a;font-weight:700;'>4.2</div>
                <div style='font-size:12px;color:#5b7a91;'>/10 · Moderate-High</div>
            </div>
        </div>
    """, variant="accent"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown("### 📊 Differential Diagnosis Scores")
        fig = go.Figure()
        for d in RISK_DATA:
            fig.add_trace(go.Bar(
                x=[d["score"]], y=[d["name"]],
                orientation='h',
                marker=dict(
                    color=d["color"],
                    line=dict(width=0),
                    opacity=0.85
                ),
                text=f"  {d['score']}%  {d['severity']}",
                textposition='outside',
                textfont=dict(color='#e2f0f9', size=11),
                name=d["name"],
                showlegend=False
            ))
        fig.update_layout(
            paper_bgcolor='#040d14', plot_bgcolor='#0b1f2e',
            font=dict(color='#e2f0f9', family='Sora'),
            barmode='stack',
            xaxis=dict(showgrid=False, showticklabels=False, range=[0, 115]),
            yaxis=dict(showgrid=False),
            margin=dict(l=10, r=100, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig, use_container_width=True)

        # Risk factors
        st.markdown("### 🔴 Key Risk Factors")
        factors = [
            ("High Fever (39.4°C)", "Critical", "#ff6b4a"),
            ("SpO2 at 96%", "Warning", "#f59e0b"),
            ("Chest Tightness", "Warning", "#f59e0b"),
            ("Rapid Onset (< 24h)", "Moderate", "#a78bfa"),
            ("Age Group: 18–35", "Low Risk", "#00e5c3"),
        ]
        for name, level, color in factors:
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;
                         padding:8px 0;border-bottom:1px solid #1a3347;'>
                <span style='font-size:13px;color:rgba(226,240,249,0.8);'>• {name}</span>
                <span style='font-family:monospace;font-size:11px;color:{color};
                              background:rgba(255,255,255,0.04);padding:2px 8px;border-radius:4px;'>
                    {level}</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🎯 Risk Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=4.2,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Risk Score", 'font': {'color': '#e2f0f9', 'size': 14}},
            number={'font': {'color': '#ff6b4a', 'size': 40}},
            gauge={
                'axis': {'range': [0, 10], 'tickcolor': '#5b7a91', 'tickfont': {'color': '#5b7a91'}},
                'bar': {'color': "#ff6b4a", 'thickness': 0.3},
                'bgcolor': '#0b1f2e',
                'bordercolor': '#1a3347',
                'steps': [
                    {'range': [0, 3],   'color': 'rgba(0,229,195,0.15)'},
                    {'range': [3, 6],   'color': 'rgba(245,158,11,0.15)'},
                    {'range': [6, 10],  'color': 'rgba(255,107,74,0.15)'},
                ],
                'threshold': {
                    'line': {'color': '#e2f0f9', 'width': 2},
                    'thickness': 0.75, 'value': 4.2
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='#040d14',
            font=dict(color='#e2f0f9'),
            margin=dict(l=20, r=20, t=30, b=20),
            height=250
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("### 💊 Treatment Suggestions")
        st.markdown(card_html("""
            <div style='font-size:12px;line-height:2;color:rgba(226,240,249,0.8);'>
                <div style='color:#f59e0b;font-weight:600;margin-bottom:8px;'>
                    ⚠ Pending Confirmation</div>
                🔬 Order: Chest X-Ray, CRP, CBC<br>
                💊 If Flu confirmed: Oseltamivir (Tamiflu)<br>
                💊 If Pneumonia: Amoxicillin + rest<br>
                🏥 Hospitalization: Not required yet<br>
                📅 Follow-up: 48 hours<br>
                <div style='margin-top:10px;font-size:11px;color:#5b7a91;font-style:italic;'>
                    * AI suggestions only — physician must verify</div>
            </div>
        """, variant="warn"), unsafe_allow_html=True)
