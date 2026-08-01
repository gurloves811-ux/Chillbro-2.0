import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Chillbro",
    page_icon="😎",
    layout="centered"
)

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
st.caption("Toxic mode")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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

        except Exception as e:
            st.error(f"Error: {e}")
