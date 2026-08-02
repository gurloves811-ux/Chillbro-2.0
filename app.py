import streamlit as st
from groq import Groq
import edge_tts
import asyncio
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from io import BytesIO
import time
import json

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

# ---------- Voices ----------
VOICE_OPTIONS = {
    "Hindi": "hi-IN-MadhurNeural",
    "English (US)": "en-US-GuyNeural",
    "English (UK)": "en-GB-RyanNeural",
    "English (India)": "en-IN-PrabhatNeural",
    "Spanish (Mexico)": "es-MX-JorgeNeural",
    "French": "fr-FR-HenriNeural",
    "German": "de-DE-ConradNeural",
    "Arabic": "ar-SA-HamedNeural",
    "Portuguese (Brazil)": "pt-BR-AntonioNeural",
    "Italian": "it-IT-DiegoNeural",
    "Japanese": "ja-JP-KeitaNeural",
    "Korean": "ko-KR-InJoonNeural",
    "Chinese": "zh-CN-YunxiNeural",
    "Russian": "ru-RU-DmitryNeural",
    "Turkish": "tr-TR-AhmetNeural",
    "Urdu": "ur-PK-AsadNeural",
    "Bengali": "bn-IN-BashkarNeural",
    "Tamil": "ta-IN-ValluvarNeural",
    "Telugu": "te-IN-MohanNeural",
    "Marathi": "mr-IN-ManoharNeural"
}

# ---------- Sidebar ----------
with st.sidebar:
    st.title("😎 Chillbro")
    
    mode = st.radio("Choose Mode", ["🔥 Toxic Mode", "💕 Love Mode"], index=0)
    selected_voice = st.selectbox("Voice Language", list(VOICE_OPTIONS.keys()), index=0)
    
    st.markdown("---")
    st.subheader("Chat History")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        chat_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
        st.download_button(
            label="💾 Save Chat",
            data=chat_json,
            file_name="chillbro_chat.json",
            mime="application/json",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader("📂 Load Chat", type="json")
    if uploaded_file is not None:
        try:
            loaded_messages = json.load(uploaded_file)
            st.session_state.messages = loaded_messages
            st.success("Chat loaded!")
            time.sleep(0.5)
            st.rerun()
        except:
            st.error("Failed to load file.")
    
    st.markdown("---")
    
    with st.expander("🔒 Privacy Policy"):
        st.markdown("""
        **Privacy Policy**
        - Messages are only used to generate replies
        - We do not store your chats on any server
        - For entertainment only
        """)
    
    st.caption("Save your chat to keep history")

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
- Sound realistic, not over-dramatic
"""

# ---------- Main App ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("😎 Chillbro")
st.caption(f"Mode: {mode} | Voice: {selected_voice}")

# Show messages (Chat will NOT clear when switching modes)
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

            # Voice
            voice_id = VOICE_OPTIONS[selected_voice]

            async def generate_voice():
                communicate = edge_tts.Communicate(reply, voice_id)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            audio_bytes = asyncio.run(generate_voice())
            st.audio(audio_bytes, format="audio/mp3")

        except Exception as e:
            st.error(f"Error: {e}")
