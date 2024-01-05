import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from geminiGenerate.generate import generateOutput
import random
import time

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/serviceAccountKey.json")  # Replace with your service account key path
firebase_admin.initialize_app(cred)


st.set_page_config(
            page_title="OutBard",
            page_icon="ocean",
        )
def main_app():

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

            with st.spinner('Wait for it...'):
                # time.sleep(2)
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

def authentication_page():
    st.title("Welcome to OutBard Authentication page")
    st.sidebar.title("OutBardAuthentication")

# Create a simple navigation menu
pages = ["Home", "Authentication"]
selected_page = st.sidebar.selectbox("Select Page", pages)
# Define pages
if selected_page == "Home":
    main_app()
elif selected_page == "Authentication":
    authentication_page()