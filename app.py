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

# ---------- Maximum Stable Voices ----------
VOICE_OPTIONS = {
    "Hindi": "hi-IN-MadhurNeural",
    "English (US)": "en-US-GuyNeural",
    "English (UK)": "en-GB-RyanNeural",
    "English (India)": "en-IN-PrabhatNeural",
    "English (Australia)": "en-AU-WilliamNeural",
    "Spanish (Spain)": "es-ES-AlvaroNeural",
    "Spanish (Mexico)": "es-MX-JorgeNeural",
    "French": "fr-FR-HenriNeural",
    "German": "de-DE-ConradNeural",
    "Arabic": "ar-SA-HamedNeural",
    "Portuguese (Brazil)": "pt-BR-AntonioNeural",
    "Portuguese (Portugal)": "pt-PT-DuarteNeural",
    "Italian": "it-IT-DiegoNeural",
    "Japanese": "ja-JP-KeitaNeural",
    "Korean": "ko-KR-InJoonNeural",
    "Chinese (Mandarin)": "zh-CN-YunxiNeural",
    "Russian": "ru-RU-DmitryNeural",
    "Turkish": "tr-TR-AhmetNeural",
    "Dutch": "nl-NL-MaartenNeural",
    "Polish": "pl-PL-MarekNeural",
    "Indonesian": "id-ID-ArdiNeural",
    "Vietnamese": "vi-VN-NamMinhNeural",
    "Thai": "th-TH-NiwatNeural",
    "Swedish": "sv-SE-MattiasNeural",
    "Greek": "el-GR-NestorasNeural",
    "Czech": "cs-CZ-AntoninNeural",
    "Romanian": "ro-RO-EmilNeural",
    "Hungarian": "hu-HU-TamasNeural",
    "Finnish": "fi-FI-HarriNeural",
    "Danish": "da-DK-JonNeural",
    "Norwegian": "nb-NO-FinnNeural",
    "Ukrainian": "uk-UA-OstapNeural",
    "Hebrew": "he-IL-AvriNeural",
    "Catalan": "ca-ES-EnricNeural",
    "Croatian": "hr-HR-SreckoNeural",
    "Slovak": "sk-SK-LukasNeural",
    "Bulgarian": "bg-BG-BorislavNeural",
    "Malay": "ms-MY-OsmanNeural",
    "Filipino": "fil-PH-AngeloNeural",
    "Urdu": "ur-PK-AsadNeural",
    "Bengali": "bn-IN-BashkarNeural",
    "Tamil": "ta-IN-ValluvarNeural",
    "Telugu": "te-IN-MohanNeural",
    "Marathi": "mr-IN-ManoharNeural",
    "Gujarati": "gu-IN-NiranjanNeural",
    "Kannada": "kn-IN-GaganNeural",
    "Malayalam": "ml-IN-MidhunNeural",
    "Punjabi": "pa-IN-VaaniNeural",
    "Afrikaans": "af-ZA-WillemNeural",
    "Swahili": "sw-KE-RafikiNeural",
    "Irish": "ga-IE-ColmNeural",
    "Welsh": "cy-GB-AledNeural",
    "Basque": "eu-ES-AnderNeural",
    "Galician": "gl-ES-SantiNeural",
    "Icelandic": "is-IS-GunnarNeural",
    "Latvian": "lv-LV-NilsNeural",
    "Lithuanian": "lt-LT-LeonasNeural",
    "Estonian": "et-EE-KertNeural",
    "Slovenian": "sl-SI-RokNeural",
    "Serbian": "sr-RS-NicholasNeural",
    "Macedonian": "mk-MK-AleksandarNeural",
    "Albanian": "sq-AL-IlirNeural",
    "Georgian": "ka-GE-GiorgiNeural",
    "Armenian": "hy-AM-DavitNeural",
    "Azerbaijani": "az-AZ-BabekNeural",
    "Kazakh": "kk-KZ-DauletNeural",
    "Uzbek": "uz-UZ-SardorNeural",
    "Mongolian": "mn-MN-BataaNeural"
}

# ---------- Sidebar ----------
with st.sidebar:
    st.title("😎 Chillbro")
    
    mode = st.radio("Choose Mode", ["🔥 Toxic Mode", "💕 Love Mode"], index=0)
    
    selected_voice = st.selectbox("Voice Language", list(VOICE_OPTIONS.keys()), index=0)
    
    st.markdown("---")
    
    with st.expander("🔒 Privacy Policy"):
        st.markdown("""
        **Privacy Policy for Chillbro**
        - Messages and voice are only used to generate replies
        - We do not store your chats permanently
        - We do not sell any data
        - Third-party services: Groq, Google Speech, Edge TTS
        """)
    
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
st.caption(f"Mode: {mode} | Voice: {selected_voice}")

if "last_mode" not in st.session_state:
    st.session_state.last_mode = mode

if st.session_state.last_mode != mode:
    st.session_state.messages = []
    st.session_state.last_mode = mode
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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

text_input = st.chat_input("Type in any language...")
if text_input:
    user_input = text_input

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
