import streamlit as st
from streamlit_modal import Modal
import firebase_admin
from firebase_admin import credentials, auth, firestore

# from firebase import Firebase
from geminiGenerate.generate import generateOutput
from google.oauth2 import id_token
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport import requests
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

# ... (previous imports and code)

# Initialize Firebase connection
# firebase = Firebase({
#     'apiKey': st.secrets["FIREBASE_API_KEY"],
#     'authDomain': st.secrets["FIREBASE_AUTH_DOMAIN"],
#     # 'databaseURL': st.secrets["FIREBASE_DATABASE_URL"],
#     'projectId': st.secrets["FIREBASE_PROJECT_ID"],
#     'storageBucket': st.secrets["FIREBASE_STORAGE_BUCKET"],
#     'messagingSenderId': st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
#     'appId': st.secrets["FIREBASE_APP_ID"],
#     'measurementId': st.secrets["FIREBASE_MEASUREMENT_ID"]
# })

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Initialize user in session_state
if "user" not in st.session_state:
    st.session_state.user = None
    
st.set_page_config(
            page_title="OutBard",
            page_icon="ocean",
        )

def authentication_page():
    st.title("Login or signup to continue")
    email = st.text_input("Enter your email:")
    password = st.text_input("Enter your password:", type="password")
    col1, col2 = st.columns(2,gap="small")
    with col1:
        login_button = st.button("Login", help="Login to your account",)
    with col2:
        signup_button = st.button("Signup", help="Create an account",type="secondary",)
    
    if signup_button:
        try:
            user = auth.create_user(email=email, password=password)
            st.success(f"User created successfully: {user.email}")
            st.session_state.user = user
            update_user_session(user.uid, True)  # Update user session in Firestore

            st.empty()
            with st.spinner("Please wait..."):
                # time.sleep(2)
                st.rerun()
            main_app()

        except Exception as e:
            st.error(f"Signup failed: {e}")

    if login_button:
        try:
            user = auth.get_user_by_email(email)
            st.session_state.user = user
            # st.success(f"Login successfuly as {user.email}")
            update_user_session(user.uid, True)  # Update user session in Firestore

            st.empty()
            with st.spinner("Please wait..."):
                # time.sleep(2)
                st.rerun()
            main_app()

        except Exception as e:
            st.error(f"Login failed: {e}")
# Function to check user session in Firestore
def check_user_session(uid):
    user_session_ref = db.collection("user_sessions").document(uid)
    user_session_data = user_session_ref.get()
    return user_session_data.exists

def update_user_session(uid, authenticated):
    user_session_ref = db.collection("user_sessions").document(uid)
    user_session_ref.set({"authenticated": authenticated})

def save_chat_history(uid, role, content):
    chat_history_ref = db.collection("chat_history").document(uid)
    chat_history = chat_history_ref.get()

    if chat_history.exists:
        chat_data = chat_history.to_dict()
        messages = chat_data.get("messages", [])
        messages.append({"role": role, "content": content})
        chat_history_ref.update({"messages": messages})
    else:
        chat_history_ref.set({"messages": [{"role": role, "content": content}]})


def resend_verification_email():
    user = st.session_state.user
    if not user.email_verified:
        try:
            # auth.send_email_verification(st.session_state.user['idToken'])
            st.write(auth.generate_email_verification_link(user.email))
            st.success("Click the link above to verify your email.")
        except Exception as e:
            st.error(f"Failed to resend verification email: {e}")

def main_app():

    st.title("Welcome to OutBard")

    with st.sidebar:

        col1, col2 = st.columns(2,gap="medium")
        with col1:
            st.title("OutBard")
        with col2:
            logout_button = st.button("Logout", help="Logout",type="primary",)
            # Logout button
            if logout_button:
                user = st.session_state.user
                update_user_session(user.uid, False)
                st.success("Logout successful!")
                st.session_state.user = None
                st.rerun()
        st.info("Hello, welcome to OutBard. You can use it to generate text for your next blog post, email, or any other writing project. Just type in your prompt and OutBard will generate a response for you. You can also use the app to chat with OutBard. OutBard is a Gemini-pro based AI writing assistant. I'm currently working on some more cool features to make it \"OutBard\". I hope you enjoy using it. If you have any feedback or suggestions, please feel free to reach out to me at [comon928@gmail.com](mailto:comon928@gmail.com)")
        
    # Check if user is already authenticated
    if st.session_state.user:
        # Retrieve user data from Firebase Authentication
        try:
            user = auth.get_user(st.session_state.user.uid)
            st.session_state.user = user
            # Check if user's email is verified
            if user.email_verified:
                # Check user session in Firestore
                if not check_user_session(user.uid):
                    # Update user session in Firestore
                    update_user_session(user.uid, True)
                # Display the main app
                with st.success(f"Welcome back, {user.email}!",):
                    time.sleep(3)
                    st.empty()
                
            else:
                st.info("Please check your email for a verification link. If you have not received it, click the button below. You wont be able to send your prompts before verifying your email.")
                st.button("Generate Verification Link", on_click=resend_verification_email, key="verify")
        except Exception as e:
            st.warning(f"User authentication failed: {e}")
    else:
        authentication_page()


    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Retrieve chat history from Firestore
    chat_history_ref = db.collection("chat_history").document(st.session_state.user.uid)
    chat_history_data = chat_history_ref.get()

    if chat_history_data.exists:
        chat_data = chat_history_data.to_dict()
        messages = chat_data.get("messages", [])
        for message in messages:
            role = message["role"]
            content = message["content"]
            with st.chat_message(role):
                st.markdown(content)
    else:
        st.info("No chat history available.")

    full_response = ""
     # Accept user input
    if user.email_verified:
        if prompt := st.chat_input("What's up?"):
            # Save user message to Firestore
            save_chat_history(st.session_state.user.uid, "user", prompt)

            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                with st.spinner('Wait for it...'):
                    assistant_response = generateOutput(prompt)

                # Save assistant response to Firestore
                save_chat_history(st.session_state.user.uid, "assistant", assistant_response)
                
                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.2)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})



# Check if user is already authenticated
if st.session_state.user :
    # Retrieve user data from Firebase Authentication
    try:
        user = auth.get_user(st.session_state.user.uid)
        st.session_state.user = user
        # Check user session in Firestore
        if not check_user_session(user.uid):
            # Update user session in Firestore
            update_user_session(user.uid, True)
        main_app()
    except Exception as e:
        st.warning(f"User authentication failed: {e}")
else:
    authentication_page()
