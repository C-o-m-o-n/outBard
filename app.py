import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from geminiGenerate.generate import generateOutput
import random
import time

SERVICE_ACCOUNT_KEY_PATH = st.secrets["SERVICE_ACCOUNT_KEY_PATH"]

FIREBASE_TYPE = st.secrets["FIREBASE_TYPE"]
FIREBASE_PROJECT_ID = st.secrets["FIREBASE_PROJECT_ID"]
FIREBASE_PRIVATE_KEY_ID = st.secrets["FIREBASE_PRIVATE_KEY_ID"]
FIREBASE_PRIVATE_KEY = st.secrets["FIREBASE_PRIVATE_KEY"]
FIREBASE_CLIENT_EMAIL = st.secrets["FIREBASE_CLIENT_EMAIL"]
FIREBASE_CLIENT_ID = st.secrets["FIREBASE_CLIENT_ID"]
FIREBASE_AUTH_URI = st.secrets["FIREBASE_AUTH_URI"]
FIREBASE_TOKEN_URI = st.secrets["FIREBASE_TOKEN_URI"]
FIREBASE_AUTH_PROVIDER_X509_CERT_URL = st.secrets["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"]
FIREBASE_CLIENT_X509_CERT_URL = st.secrets["FIREBASE_CLIENT_X509_CERT_URL"]
FIREBASE_UNIVERSE_DOMAIN = st.secrets["FIREBASE_UNIVERSE_DOMAIN"]


firebase_config = {
    "type": FIREBASE_TYPE,
    "project_id": FIREBASE_PROJECT_ID,
    "private_key_id": FIREBASE_PRIVATE_KEY_ID,
    "private_key": FIREBASE_PRIVATE_KEY,
    "client_email": FIREBASE_CLIENT_EMAIL,
    "client_id": FIREBASE_CLIENT_ID,
    "auth_uri": FIREBASE_AUTH_URI,
    "token_uri": FIREBASE_TOKEN_URI,
    "auth_provider_x509_cert_url": FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": FIREBASE_CLIENT_X509_CERT_URL,
    "universe_domain": FIREBASE_UNIVERSE_DOMAIN
}


# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# Initialize session_state
if "user" not in st.session_state:
    st.session_state.user = None

st.set_page_config(
            page_title="OutBard",
            page_icon="ocean",
        )

def authentication_page():
    st.title("Login or signup to continue")
    # st.sidebar.title("OutBardAuthentication")
    
    email = st.text_input("Enter your email:")
    password = st.text_input("Enter your password:", type="password")

    col1, col2 = st.columns(2,gap="small")

    with col1:
        login_button = st.button("Login", help="Login to your account",)

    with col2:
        signup_button = st.button("Signup", help="Create an account",type="primary",)

    if signup_button:
        try:
            user = auth.create_user(email=email, password=password)
            st.success(f"User created successfully: {user.email}")
            st.session_state.user = user
            # st.success("Signup successful!")

            st.empty()
            with st.spinner("Please wait..."):
                time.sleep(2)
                st.experimental_rerun()
            main_app()

        except Exception as e:
            st.error(f"Signup failed: {e}")

    if login_button:
        try:
            user = auth.get_user_by_email(email)
            st.session_state.user = user
            st.success(f"Login successfuly as {user.email}")

            st.empty()
            with st.spinner("Please wait..."):
                time.sleep(2)
                st.experimental_rerun()
            main_app()

        except Exception as e:
            st.error(f"Login failed: {e}")
            
def main_app():

    st.title("Welcome to OutBard")
    st.sidebar.title("OutBard")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    full_response = ""

    # Accept user input
    if prompt := st.chat_input("What's up?"):
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

if st.session_state.user:
    main_app()
else:
    authentication_page()
