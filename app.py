import streamlit as st
from geminiGenerate.generate import generateOutput
import random
import time

st.title("Welcome to OutBard")
st.sidebar.title("OutBard")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

full_response = ""

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        assistant_response = generateOutput(prompt)

        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.2)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
# Add assistant response to chat history
st.session_state.messages.append({"role": "assistant", "content": full_response})