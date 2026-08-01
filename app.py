import streamlit as st
from groq import Groq

# Page settings
st.set_page_config(
    page_title="Chillbro",
    page_icon="😎",
    layout="centered"
)

# Toxic + Funny personality
SYSTEM_PROMPT = """
You are Chillbro — a toxic but funny AI friend.
You roast people, use sarcasm, slang, and savage humor for entertainment.
You can be rude, blunt, and slightly mean, but keep it fun and not actually hateful or serious.
Talk like a chaotic friend who teases a lot.
Use casual language, emojis sometimes, and keep the vibe entertaining.
Never be boring or too nice.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.title("😎 Chillbro")
st.caption("Your toxic & funny AI friend")

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's good?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate reply
    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])

            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.9,
                max_tokens=800
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

            # Save assistant reply
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error("Something went wrong. Check your API key or try again.")
