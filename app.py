import streamlit as st
from groq import Groq
import edge_tts
import asyncio
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from io import BytesIO
import time

st.set_page_config(page_title="Chillbro", page_icon="😎", layout="centered")

# ---------- Opening Animation ----------
if "opened" not in st.session_state:
    st.session_state.opened = False

if not st.session_state.opened:
    st.markdown("""
        <style>
        .big-title {
            font-size: 60px;
            font-weight: bold;
            text-align: center;
            color: #ff4b4b;
            animation: zoomIn 1.2s ease;
        }
        .subtitle {
            text-align: center;
            font-size: 22px;
            color: #aaaaaa;
            animation: fadeIn 2s ease;
        }
        @keyframes zoomIn {
            from { transform: scale(0.3); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        </style>
        <div class="big-title">😎 Chillbro</div>
        <div class="subtitle">Loading...</div>
    """, unsafe_allow_html=True)
    
    time.sleep(2.2)
    st.session_state.opened = True
    st.rerun()

# ---------- Sidebar ----------
with st.sidebar:
    st.title("😎 Chillbro")
    
    mode = st.radio(
        "Choose Mode",
        ["🔥 Toxic Mode", "💕 Love Mode"],
        index=0
    )
    
    st.markdown("---")
    
    with st.expander("🔒 Privacy Policy"):
        st.markdown("""
        **Privacy Policy for Chillbro**

        - Messages and voice are only used to generate replies
        - We do not store your chats permanently
        - We do not sell any data
        - Third-party services: Groq, Google Speech, Edge TTS

        By using this app, you agree to this policy.
        """)
    
    st.markdown("---")
    st.caption("For entertainment only")

# ---------- System Prompts ----------
if mode == "🔥 Toxic Mode":
    SYSTEM_PROMPT = """
You are Chillbro in Toxic Mode — extremely toxic, savage and roasting AI.
Talk like the most toxic Instagram comment section.

Rules:
- Always reply in the same language the user used
- Keep every reply very short (1 to 3 lines maximum)
- Be extremely rude, insulting, sarcastic and toxic
- Use heavy slang and roasting
- Never be nice
"""
else:
    SYSTEM_PROMPT = """
You are Chillbro in Love Mode — a real romantic partner with peak rizz.

Rules:
- Always reply in the same language the user used
- Keep every reply short (1 to 3 lines maximum)
- Talk like a real boyfriend/girlfriend (natural, warm and flirty)
- Use high-level rizz, soft compliments and affectionate language
- Make the user feel special and desired
- Do not write long paragraphs
- Sound realistic, not over-dramatic
"""

# ---------- Main App ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("😎 Chillbro")
st.caption(f"Current Mode: {mode}")

# Clear chat when mode changes
if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

if st.session_state.last_mode != mode:
    st.session_state.messages = []
    st.session_state.last_mode = mode
    st.rerun()

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- Voice Input ----------
st.write("Speak:")
audio_bytes = audio_recorder(pause_threshold=1.5, sample_rate=16000)

user_input = None

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
            user_input = recognizer.recognize_google(audio_data, language="hi-IN")
            st.success(f"You said: {user_input}")
    except:
        st.error("Could not understand. Try again.")

# ---------- Text Input ----------
text_input = st.chat_input("Type in any language...")
if text_input:
    user_input = text_input

# ---------- Generate Reply ----------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.9,
                max_tokens=150
            )

            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Voice Output
            async def generate_voice():
                communicate = edge_tts.Communicate(reply, "hi-IN-MadhurNeural")
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            audio_bytes = asyncio.run(generate_voice())
            st.audio(audio_bytes, format="audio/mp3")

        except Exception as e:
            st.error(f"Error: {e}")
        
