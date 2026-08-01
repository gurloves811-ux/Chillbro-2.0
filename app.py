import streamlit as st
from groq import Groq

# Page settings
st.set_page_config(
    page_title="Chillbro",
    page_icon="😎",
    layout="centered"
)

# Chillbro's personality
SYSTEM_PROMPT = """
You are Chillbro — a funny, chill, and real AI friend.
Talk casually like a close friend. Use humor, light sarcasm, slang, and meme energy when it fits.
Keep replies natural, not too long, and always keep a positive, relaxed vibe.
You're supportive but never boring or robotic.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title
st.title("😎 Chillbro")
st.caption("Your funny & chill AI friend")

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
                temperature=0.85,
                max_tokens=800
            )

            reply = response.choices[0].message.content
            st.markdown(reply)

            # Save assistant reply
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error("Something went wrong. Check your API key or try again.")
