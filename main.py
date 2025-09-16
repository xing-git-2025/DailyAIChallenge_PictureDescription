# I will use a chatbox for this challenge, where use can upload a picture to the chatbox
# and the chatbox can give the description of the picture

import streamlit as st
from openai import OpenAI
import os
# the .env file needs to be in the same folder as main.py. .env is the file that save my OPENAI Key. it is also called environment variable
from dotenv import load_dotenv

import base64

# Here we load the OpenAI API key from the environment variable and set it
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("API key not found. Please set the OPENAI_API_KEY in the .env file.")

# Create an Open AI client object and set the API key
client = OpenAI(api_key=api_key)

# (1) Create a title for the streamlit page,
st.title("Picture description Chatbox")

with st.chat_message("ai"):
    st.write("hello, please upload the picture that you want me to describe")

# Initialize an object to store the message history (in the session state)
if "messages" not in st.session_state:
    st.session_state.messages = []

# (2) display message, including the previous message history using streamlit's chat_message() and markdown() functions, and
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user" and isinstance(message["content"], list):
            # User content may have text + image parts
            for c in message["content"]:
                if c["type"] == "text":
                    st.write(c["text"])
                elif c["type"] == "image_url":
                    st.image(c["image_url"]["url"], width=250)
        else:
            # Assistant just has plain text replies
            st.write(message["content"])

# Upload image or input text as user input
user_text = st.chat_input("Type your message or just upload an image...")
user_image = st.file_uploader("Attach an image (optional)", type=["jpg","jpeg","png"], key=f"uploader_{len(st.session_state.messages)}")

if user_image or user_text:
    # show user message
    with st.chat_message("user"):
        if user_text:
            st.write(user_text)
        if user_image:
            st.image(user_image, width=250)
    # Build content payload
    user_content = []
    if user_text:
        user_content.append({"type": "text", "text": user_text})
    if user_image:
        img_bytes = user_image.read()
        img_b64 = base64.b64encode(img_bytes).decode()
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
        })

    # Add user image or text to chat history
    st.session_state.messages.append({
        "role": "user",
        "type": "mixed",
        "content": user_content
    })

    # Prepare history for OpenAI
    api_messages = []
    for message in st.session_state.messages:
        if message["role"] == "user":
            api_messages.append({"role": "user", "content": message["content"]})
        else:
            api_messages.append({"role": "assistant", "content": [{"type":"text","text": message["content"]}]})

    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages
        )
    description = response.choices[0].message.content.strip()

    # Add bot reply to chat
    st.session_state.messages.append({
        "role": "assistant",
        "type": "text",
        "content": description
    })
    with st.chat_message("assistant"):
        st.write(description)
