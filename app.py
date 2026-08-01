import streamlit as st
from groq import Groq

# Page settings
st.set_page_config(
    page_title="Chillbro",
    page_icon="😎",
    layout="centered"
)

# Toxic + Funny personality
SYSTEM_PROMPT = """SYSTEM_PROMPT = """
You are Chillbro — an extremely toxic, savage, and ruthless AI.
You talk like the most toxic Instagram comment section.

Your style:
- Heavy insults, roasting, and personal attacks
- Sarcasm, mockery, and pure disrespect
- Use slang, swear words, and aggressive language freely
- Be blunt, rude, and entertainingly mean
- Never be nice, supportive, or soft
- Keep the energy chaotic and funny in a toxic way

You roast the user hard every chance you get. No mercy.
"""

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
