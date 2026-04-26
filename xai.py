import streamlit as st
import time
from utils.helpers import card_html, tag_html

# ── Simulated STT (plug in Whisper or Google STT here) ──────────────────────
SAMPLE_TRANSCRIPTS = [
    "Main kaafi dino se fever aur body aches se pareshan hoon. Raat ko aur bura lagta hai. Chest mein thoda tightness bhi hai.",
    "I have had a high fever since 3 days, dry cough, and severe body pain. No breathlessness but chest feels heavy.",
    "Mujhe kal se sar dard aur naak bhi band hai. Thakaan bahut zyada hai.",
]

def simulate_stt(audio_file=None) -> str:
    """Simulate STT — replace with: openai.Audio.transcribe() or SpeechRecognition."""
    time.sleep(1.5)
    return SAMPLE_TRANSCRIPTS[0]

def simulate_tts(text: str) -> str:
    """Placeholder — replace with: gTTS, ElevenLabs, or Google TTS."""
    return f"[TTS] Would speak: {text[:80]}..."


def render():
    st.title("🎙️ Speech-to-Text Input")
    st.markdown(
        tag_html("STT Ready", "green") + tag_html("Hindi + English", "purple"),
        unsafe_allow_html=True
    )
    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### 🎤 Record or Upload Audio")

        # Upload option
        uploaded = st.file_uploader(
            "Upload audio file (WAV, MP3, M4A)",
            type=["wav", "mp3", "m4a", "ogg"],
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Simulate recording
        st.markdown(card_html("""
            <div style='text-align:center;padding:10px 0;'>
                <div style='font-size:36px;margin-bottom:10px;'>🎤</div>
                <div style='font-size:13px;color:#5b7a91;'>
                    Click <strong style='color:#00e5c3;'>Start Recording</strong> to capture your symptoms
                </div>
                <div style='font-size:11px;color:#5b7a91;margin-top:6px;font-family:monospace;'>
                    Supports Hindi, English, Hinglish
                </div>
            </div>
        """, variant="accent"), unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            record_btn = st.button("🔴 Start Recording", use_container_width=True)
        with col_b:
            transcribe_btn = st.button("⚡ Transcribe", use_container_width=True)

        if record_btn:
            with st.spinner("Recording for 5 seconds..."):
                time.sleep(2)
            st.success("✅ Recording captured! Click Transcribe to process.")

        if transcribe_btn or uploaded:
            with st.spinner("Transcribing audio..."):
                transcript = simulate_stt(uploaded)
            st.session_state["last_transcript"] = transcript
            st.success("✅ Transcription complete!")

        # Show transcript
        if "last_transcript" in st.session_state:
            st.markdown("---")
            st.markdown("**📝 Transcript**")
            st.text_area(
                "Transcript",
                st.session_state["last_transcript"],
                height=100,
                label_visibility="collapsed"
            )

            # Highlight keywords
            t = st.session_state["last_transcript"]
            keywords = ["fever", "cough", "chest", "pain", "aches", "breathless",
                        "tightness", "thakaan", "sar dard", "naak"]
            highlighted = t
            for kw in keywords:
                highlighted = highlighted.replace(
                    kw, f"<span style='color:#ff6b4a;font-weight:600;'>{kw}</span>"
                )
            st.markdown(f"""
            <div style='background:#040d14;border:1px solid #1a3347;border-radius:8px;
                         padding:12px;font-family:monospace;font-size:13px;line-height:1.8;'>
                {highlighted}
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### 🔊 Text-to-Speech Response")

        response_text = st.text_area(
            "AI Response to speak aloud",
            value="Based on your symptoms, I suspect Influenza Type A. However, "
                  "there is significant overlap with pneumonia. Please consult a "
                  "doctor and get a chest X-ray done.",
            height=120,
            label_visibility="collapsed"
        )

        language = st.selectbox("Language", ["English", "Hindi", "Hinglish"])
        voice_speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)

        if st.button("🔊 Play Response", use_container_width=True):
            with st.spinner("Generating speech..."):
                time.sleep(1)
            st.info("🔊 " + simulate_tts(response_text))
            st.markdown("""
            > **To enable real TTS:** Install `gtts` and replace `simulate_tts()`
            > with `gTTS(text=response_text, lang='en').save('response.mp3')`
            """)

        st.markdown("---")
        st.markdown("**⚙️ Integration Guide**")
        st.markdown(card_html("""
            <div style='font-family:monospace;font-size:11px;color:#5b7a91;line-height:2;'>
                STT Options:<br>
                <span style='color:#00e5c3;'>→</span> OpenAI Whisper (offline)<br>
                <span style='color:#00e5c3;'>→</span> Google Speech-to-Text API<br>
                <span style='color:#00e5c3;'>→</span> SpeechRecognition (free)<br><br>
                TTS Options:<br>
                <span style='color:#a78bfa;'>→</span> gTTS (Google, free)<br>
                <span style='color:#a78bfa;'>→</span> ElevenLabs (premium)<br>
                <span style='color:#a78bfa;'>→</span> pyttsx3 (offline)
            </div>
        """), unsafe_allow_html=True)

        # Extracted symptoms
        st.markdown("**🏷️ Extracted Symptoms**")
        symptoms = ["High Fever", "Body Aches", "Dry Cough", "Chest Tightness", "Fatigue"]
        cols = st.columns(2)
        for i, sym in enumerate(symptoms):
            with cols[i % 2]:
                st.markdown(f"""
                <div style='background:rgba(0,229,195,0.08);border:1px solid rgba(0,229,195,0.2);
                             border-radius:6px;padding:6px 10px;margin:3px 0;
                             font-size:12px;color:#00e5c3;'>✓ {sym}</div>
                """, unsafe_allow_html=True)
