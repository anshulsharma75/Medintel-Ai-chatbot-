import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import io
import time
from utils.helpers import card_html, tag_html

# ── Simulated model inference ────────────────────────────────────────────────
def analyze_xray(image) -> dict:
    """
    Simulate Grad-CAM + classification.
    Replace with: torchvision ResNet50 + pytorch-grad-cam
    """
    time.sleep(2)
    return {
        "findings": [
            {"label": "Consolidation (R. Lower Lobe)", "confidence": 0.62, "color": "#f59e0b"},
            {"label": "Normal Lung Parenchyma",        "confidence": 0.28, "color": "#00e5c3"},
            {"label": "Pleural Effusion",              "confidence": 0.10, "color": "#5b7a91"},
        ],
        "ai_note": (
            "Subtle opacity detected in the right lower lobe. "
            "Pattern is consistent with early consolidation. "
            "Pneumonia cannot be excluded — recommend clinical correlation and CRP test."
        ),
        "regions": {
            "Right Lower Lobe": "⚠ Opacity detected",
            "Left Lobe":        "✓ Clear",
            "Hilar Region":     "✓ Normal",
            "Pleural Space":    "✓ No effusion",
        }
    }


def render():
    st.title("🖼️ Medical Image Analysis")
    st.markdown(
        tag_html("Vision AI", "purple") +
        tag_html("Grad-CAM XAI", "green") +
        tag_html("DICOM / PNG / JPEG", "orange"),
        unsafe_allow_html=True
    )
    st.markdown("---")

    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.markdown("### 📤 Upload Medical Image")
        uploaded_img = st.file_uploader(
            "Upload X-Ray, CT, or MRI",
            type=["png", "jpg", "jpeg", "dcm", "bmp"],
            label_visibility="collapsed"
        )

        img_type = st.selectbox("Image Type", ["Chest X-Ray", "CT Scan", "MRI Brain", "Abdominal CT"])
        analyze_btn = st.button("🔬 Analyze Image", use_container_width=True)

        if uploaded_img:
            img = Image.open(uploaded_img).convert("RGB")
            st.image(img, caption="Uploaded Image", use_column_width=True)

        else:
            # Placeholder demo image (gradient noise)
            st.markdown(card_html("""
                <div style='text-align:center;padding:30px;'>
                    <div style='font-size:48px;'>🫁</div>
                    <div style='font-size:13px;color:#5b7a91;margin-top:8px;'>
                        Upload an X-Ray to begin analysis
                    </div>
                    <div style='font-size:11px;color:#1a3347;margin-top:4px;font-family:monospace;'>
                        Supports PNG · JPG · DICOM
                    </div>
                </div>
            """), unsafe_allow_html=True)

    with col_right:
        st.markdown("### 🔍 Analysis Results")

        if analyze_btn or st.session_state.get("img_analyzed"):
            st.session_state["img_analyzed"] = True
            with st.spinner("Running ResNet-50 + Grad-CAM..."):
                result = analyze_xray(uploaded_img)

            # Confidence bars
            st.markdown("**Classification Confidence**")
            for finding in result["findings"]:
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
                    <div style='font-size:12px;width:220px;color:rgba(226,240,249,0.8);'>
                        {finding["label"]}</div>
                    <div style='flex:1;height:6px;background:rgba(255,255,255,0.06);
                                border-radius:3px;overflow:hidden;'>
                        <div style='height:100%;width:{int(finding["confidence"]*100)}%;
                                    background:{finding["color"]};border-radius:3px;'></div>
                    </div>
                    <div style='font-family:monospace;font-size:11px;color:{finding["color"]};
                                width:36px;text-align:right;'>
                        {int(finding["confidence"]*100)}%</div>
                </div>
                """, unsafe_allow_html=True)

            # Grad-CAM heatmap simulation
            st.markdown("**Grad-CAM Attention Heatmap**")
            np.random.seed(42)
            w, h = 200, 160
            heatmap = np.zeros((h, w))
            # simulate hotspot in lower right (lung)
            for cx, cy, r, intensity in [(150, 110, 35, 1.0), (140, 90, 20, 0.6), (160, 130, 15, 0.4)]:
                Y, X = np.ogrid[:h, :w]
                dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
                heatmap += intensity * np.exp(-dist**2 / (2 * r**2))
            heatmap = np.clip(heatmap, 0, 1)

            fig = go.Figure(go.Heatmap(
                z=heatmap,
                colorscale=[[0, "#040d14"], [0.4, "#1a3347"],
                             [0.7, "#f59e0b"], [1.0, "#ff6b4a"]],
                showscale=False
            ))
            fig.update_layout(
                paper_bgcolor='#0b1f2e', plot_bgcolor='#0b1f2e',
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                margin=dict(l=0, r=0, t=0, b=0),
                height=180
            )
            st.plotly_chart(fig, use_container_width=True)

            # Region findings
            st.markdown("**Regional Findings**")
            for region, status in result["regions"].items():
                color = "#ff6b4a" if "⚠" in status else "#00e5c3"
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;
                             padding:7px 0;border-bottom:1px solid #1a3347;font-size:12px;'>
                    <span style='color:#5b7a91;'>{region}</span>
                    <span style='color:{color};font-family:monospace;'>{status}</span>
                </div>
                """, unsafe_allow_html=True)

            # AI note
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(card_html(f"""
                <div style='font-size:11px;color:#5b7a91;font-family:monospace;margin-bottom:6px;'>
                    AI INTERPRETATION</div>
                <div style='font-size:12px;color:rgba(226,240,249,0.75);
                             font-style:italic;line-height:1.7;'>
                    "{result['ai_note']}"</div>
            """, variant="warn"), unsafe_allow_html=True)

        else:
            st.markdown(card_html("""
                <div style='text-align:center;padding:20px;color:#5b7a91;font-size:13px;'>
                    Upload an image and click <strong style='color:#00e5c3;'>Analyze Image</strong>
                    to see results
                </div>
            """), unsafe_allow_html=True)

    # Integration guide
    st.markdown("---")
    st.markdown("**🔧 Real Model Integration**")
    with st.expander("How to plug in a real chest X-ray model"):
        st.code("""
# Option 1: TorchXRayVision (pre-trained chest X-ray models)
pip install torchxrayvision

import torchxrayvision as xrv
import torchvision.transforms as transforms

model = xrv.models.DenseNet(weights="densenet121-res224-all")
transform = transforms.Compose([xrv.datasets.XRayCenterCrop(), xrv.datasets.XRayResizer(224)])

img_array = np.array(pil_image.convert("L")) / 255.0
img_tensor = transform(img_array[None])
predictions = model(img_tensor.unsqueeze(0))

# Option 2: Grad-CAM visualization
pip install grad-cam
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

cam = GradCAM(model=model, target_layers=[model.features[-1]])
grayscale_cam = cam(input_tensor=img_tensor)
        """, language="python")
