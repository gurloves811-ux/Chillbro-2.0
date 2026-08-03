import streamlit as st
from groq import Groq
import edge_tts
import asyncio
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from io import BytesIO
import time
import json
from datetime import datetime
from streamlit_js_eval import get_from_local_storage, set_to_local_storage

st.set_page_config(page_title="Chillbro", page_icon="😎", layout="centered", initial_sidebar_state="expanded")

# ---------- Load saved name ----------
if "username" not in st.session_state:
    saved_name = get_from_local_storage("chillbro_username")
    st.session_state.username = saved_name if saved_name else ""

# ---------- Theme ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

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
    time.sleep(1.8)
    st.session_state.opened = True
    st.rerun()

# ---------- Name Input (Only First Time) ----------
if st.session_state.username == "":
    st.markdown("<h2 style='text-align:center;'>😎 Welcome to Chillbro</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Enter your name (only one time)</p>", unsafe_allow_html=True)
    
    with st.form("name_form"):
        name = st.text_input("Your Name", placeholder="Type your name...")
        submit = st.form_submit_button("Continue", use_container_width=True)
        
        if submit and name.strip() != "":
            st.session_state.username = name.strip()
            set_to_local_storage("chillbro_username", name.strip())
            st.rerun()
        elif submit:
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
    "Marathi": "mr-IN-ManoharNeural"
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

# ---------- Initialize ----------
for key in ["toxic_messages", "love_messages", "knowledge_messages", "music_messages"]:
    if key not in st.session_state:
        st.session_state[key] = []

if "last_reply" not in st.session_state:
    st.session_state.last_reply = ""

# ---------- Sidebar ----------
with st.sidebar:
    st.title("😎 Chillbro")
    st.success(f"Hello, {st.session_state.username}!")
    
    mode = st.radio(
        "Choose Mode",
        ["🔥 Toxic Mode", "💕 Love Mode", "🧠 Knowledge Mode", "🎵 Music Mode"],
        index=0
    )
    
    selected_lang = st.selectbox("Language", list(VOICE_OPTIONS.keys()), index=0)
    
    # Creativity Slider
    temperature = st.slider("Creativity", 0.1, 1.3, 0.9, 0.1)
    
    # Dark Mode
    dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_mode
    
    st.markdown("---")
    
    # Clear with confirmation
    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        st.session_state.confirm_clear = True
    
    if st.session_state.get("confirm_clear", False):
        st.warning("Are you sure?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes", use_container_width=True):
                if mode == "🔥 Toxic Mode":
                    st.session_state.toxic_messages = []
                elif mode == "💕 Love Mode":
                    st.session_state.love_messages = []
                elif mode == "🧠 Knowledge Mode":
                    st.session_state.knowledge_messages = []
                else:
                    st.session_state.music_messages = []
                st.session_state.confirm_clear = False
                st.rerun()
        with col2:
            if st.button("No", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()
    
    # Export Chat
    if mode == "🔥 Toxic Mode":
        current_messages = st.session_state.toxic_messages
    elif mode == "💕 Love Mode":
        current_messages = st.session_state.love_messages
    elif mode == "🧠 Knowledge Mode":
        current_messages = st.session_state.knowledge_messages
    else:
        current_messages = st.session_state.music_messages
    
    if len(current_messages) > 0:
        # Export as TXT
        txt_content = f"Chillbro Chat - {st.session_state.username}\nMode: {mode}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        for msg in current_messages:
            role = "You" if msg["role"] == "user" else "Chillbro"
            txt_content += f"{role}: {msg['content']}\n\n"
        
        st.download_button("📄 Export as TXT", txt_content, "chillbro_chat.txt", "text/plain", use_container_width=True)
        
        # Export as JSON
        chat_json = json.dumps(current_messages, ensure_ascii=False, indent=2)
        st.download_button("💾 Save JSON", chat_json, "chillbro_chat.json", "application/json", use_container_width=True)
    
    if st.button("🚪 Reset Name", use_container_width=True):
        st.session_state.username = ""
        set_to_local_storage("chillbro_username", "")
        st.rerun()

    with st.expander("Credits"):
        st.markdown("**Chillbro**\nMultiple AI Modes + Voice\nPowered by Groq")

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
Rules: Keep replies short (1-3 lines). Be warm, flirty and affectionate."""
    messages = st.session_state.love_messages

elif mode == "🧠 Knowledge Mode":
    SYSTEM_PROMPT = f"""You are Chillbro in Knowledge Mode — a smart helpful AI.
{lang_instruction}
Rules: Be clear, accurate and helpful."""
    messages = st.session_state.knowledge_messages

else:
    SYSTEM_PROMPT = f"""You are Chillbro in Music Mode — expert music AI.
{lang_instruction}
Rules: Suggest playlists based on mood and genre."""
    messages = st.session_state.music_messages

# ---------- Main ----------
st.title("😎 Chillbro")
st.caption(f"Hello {st.session_state.username}  |  {mode}  |  {selected_lang}")

# Show messages
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- Action Buttons ----------
if st.session_state.last_reply:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Copy Last Reply"):
            st.code(st.session_state.last_reply, language=None)
            st.success("Copied! (Select & copy manually)")
    with col2:
        if st.button("🔄 Regenerate"):
            if len(messages) >= 2:
                messages.pop()  # remove last AI reply
                st.session_state.regenerate = True
                st.rerun()

# ---------- Mic + Input ----------
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
        st.error("Could not understand.")

text_input = st.chat_input("Type something...")
if text_input:
    user_input = text_input

# Handle Regenerate
if st.session_state.get("regenerate", False):
    st.session_state.regenerate = False
    if messages and messages[-1]["role"] == "user":
        user_input = messages[-1]["content"]
        messages.pop()

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

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            reply = response.choices[0].message.content
            st.markdown(reply)
            messages.append({"role": "assistant", "content": reply})
            st.session_state.last_reply = reply

            # Voice
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
