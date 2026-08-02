import streamlit as st
from groq import Groq
import edge_tts
import asyncio
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from io import BytesIO

st.set_page_config(page_title="Chillbro", page_icon="😎", layout="centered")

SYSTEM_PROMPT = """
You are Chillbro — an extremely toxic and savage AI.
Talk like the most toxic Instagram comments.

Rules:
- Keep every reply very short (1 to 3 lines maximum)
- Be extremely rude, insulting, and roasting
- Use slang, swear words, and heavy sarcasm
- Never write long responses
- No mercy, pure toxic energy
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("😎 Chillbro")
st.caption("Toxic mode + Male Voice")

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- Voice Input ----------
st.write("Or speak:")
audio_bytes = audio_recorder(pause_threshold=1.5, sample_rate=16000)

user_input = None

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
            user_input = recognizer.recognize_google(audio_data)
            st.success(f"You said: {user_input}")
    except:
        st.error("Could not understand the audio. Try again.")

# ---------- Text Input ----------
text_input = st.chat_input("Or type something...")
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
                temperature=0.95,
                max_tokens=150
            )

            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # ---------- Male Voice Output ----------
            async def generate_voice():
                communicate = edge_tts.Communicate(reply, "en-US-GuyNeural")  # Male voice
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data

            audio_bytes = asyncio.run(generate_voice())
            st.audio(audio_bytes, format="audio/mp3")

        except Exception as e:
            st.error(f"Error: {e}")        
