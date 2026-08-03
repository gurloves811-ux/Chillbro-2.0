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
    time.sleep(2.0)
    st.session_state.opened = True
    st.rerun()

# ---------- Name Login ----------
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.username == "":
    st.markdown("<h2 style='text-align:center;'>😎 Welcome to Chillbro</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Enter your name to continue</p>", unsafe_allow_html=True)
    
    with st.form("name_form"):
        name = st.text_input("Your Name", placeholder="Type your name...")
        submit = st.form_submit_button("Continue", use_container_width=True)
        
        if submit:
            if name.strip() != "":
                st.session_state.username = name.strip()
                st.rerun()
            else:
                st.warning("Please enter your name")
    st.stop()

# ---------- Languages ----------
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
    "Chinese (Mandarin)": "zh-CN-YunxiNeural",
    "Russian": "ru-RU-DmitryNeural",
    "Turkish": "tr-TR-AhmetNeural",
    "Urdu": "ur-PK-AsadNeural",
    "Bengali": "bn-IN-BashkarNeural",
    "Tamil": "ta-IN-ValluvarNeural",
    "Telugu": "te-IN-MohanNeural",
    "Marathi": "mr-IN-ManoharNeural",
    "Gujarati": "gu-IN-NiranjanNeural",
    "Indonesian": "id-ID-ArdiNeural",
    "Vietnamese": "vi-VN-NamMinhNeural",
    "Thai": "th-TH-NiwatNeural"
}

SPEECH_LANG_CODES = {
    "Hindi": "hi-IN",
    "English (US)": "en-US",
    "English (UK)": "en-GB",
    "English (India)": "en-IN",
    "Spanish (Mexico)": "es-MX",
    "French": "fr-FR",
    "German": "de-DE",
    "Arabic": "ar-SA",
    "Portuguese (Brazil)": "pt-BR",
    "Italian": "it-IT",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Chinese (Mandarin)": "zh-CN",
    "Russian": "ru-RU",
    "Turkish": "tr-TR",
    "Urdu": "ur-PK",
    "Bengali": "bn-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Marathi": "mr-IN"
}

# ---------- Initialize chats ----------
for key in ["toxic_messages", "love_messages", "knowledge_messages", "music_messages"]:
    if key not in st.session_state:
        st.session_state[key] = []

# ---------- Sidebar ----------
with st.sidebar:
    st.title("😎 Chillbro")
    st.markdown(f"**Hello, {st.session_state.username}!**")
    
    mode = st.radio(
        "Choose Mode",
        ["🔥 Toxic Mode", "💕 Love Mode", "🧠 Knowledge Mode", "🎵 Music Mode"],
        index=0
    )
    
    selected_lang = st.selectbox("Select Language", list(VOICE_OPTIONS.keys()), index=0)
    
    st.markdown("---")
    st.subheader("Chat History")
    
    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        if mode == "🔥 Toxic Mode":
            st.session_state.toxic_messages = []
        elif mode == "💕 Love Mode":
            st.session_state.love_messages = []
        elif mode == "🧠 Knowledge Mode":
            st.session_state.knowledge_messages = []
        else:
            st.session_state.music_messages = []
        st.rerun()
    
    if mode == "🔥 Toxic Mode":
        current_messages = st.session_state.toxic_messages
    elif mode == "💕 Love Mode":
        current_messages = st.session_state.love_messages
    elif mode == "🧠 Knowledge Mode":
        current_messages = st.session_state.knowledge_messages
    else:
        current_messages = st.session_state.music_messages
    
    if len(current_messages) > 0:
        chat_json = json.dumps(current_messages, ensure_ascii=False, indent=2)
        st.download_button("💾 Save Chat", chat_json, "chillbro_chat.json", "application/json", use_container_width=True)
    
    if st.button("🚪 Change Name", use_container_width=True):
        st.session_state.username = ""
        st.rerun()

    with st.expander("Credits"):
        st.markdown("**Chillbro**\nMade for entertainment")

# ---------- System Prompts ----------
lang_instruction = f"You must always reply only in {selected_lang} language."

if mode == "🔥 Toxic Mode":
    SYSTEM_PROMPT = f"""You are Chillbro in Toxic Mode — extremely toxic and savage.
{lang_instruction}
Rules: Keep replies very short (1-3 lines). Be rude, insulting, roasting. Never be nice."""
    messages = st.session_state.toxic_messages

elif mode == "💕 Love Mode":
    SYSTEM_PROMPT = f"""You are Chillbro in Love Mode — a real romantic partner with peak rizz.
{lang_instruction}
Rules: Keep replies short (1-3 lines). Be warm, flirty and affectionate like a real partner."""
    messages = st.session_state.love_messages

elif mode == "🧠 Knowledge Mode":
    SYSTEM_PROMPT = f"""You are Chillbro in Knowledge Mode — a smart helpful AI like ChatGPT and Grok.
{lang_instruction}
Rules: Be clear, accurate and helpful."""
    messages = st.session_state.knowledge_messages

else:
    SYSTEM_PROMPT = f"""You are Chillbro in Music Mode — expert music recommendation AI.
{lang_instruction}
Rules: Suggest playlists and songs based on mood, genre or activity."""
    messages = st.session_state.music_messages

# ---------- Main ----------
st.title(f"😎 Chillbro")
st.caption(f"Hello {st.session_state.username} | Mode: {mode} | Language: {selected_lang}")

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- Mic + Input ----------
st.markdown("---")
col1, col2 = st.columns([1, 5])

with col1:
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#3498db",
        icon_name="microphone",
        icon_size="2x",
        pause_threshold=1.5,
        sample_rate=16000
    )

with col2:
    st.caption("Tap mic to speak")

user_input = None

if audio_bytes:
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
            lang_code = SPEECH_LANG_CODES.get(selected_lang, "en-US")
            user_input = recognizer.recognize_google(audio_data, language=lang_code)
            st.success(f"You said: {user_input}")
    except:
        st.error("Could not understand. Try again.")

text_input = st.chat_input(f"Type something...")
if text_input:
    user_input = text_input

# ---------- Generate Reply ----------
if user_input:
    messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

            max_tokens = 1024 if mode in ["🧠 Knowledge Mode", "🎵 Music Mode"] else 150
            temperature = 0.7 if mode in ["🧠 Knowledge Mode", "🎵 Music Mode"] else 0.9

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            reply = response.choices[0].message.content
            st.markdown(reply)
            messages.append({"role": "assistant", "content": reply})

            voice_id = VOICE_OPTIONS[selected_lang]

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
