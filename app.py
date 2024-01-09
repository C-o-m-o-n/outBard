import uuid
import streamlit as st
from streamlit_modal import Modal
import firebase_admin
from firebase_admin import credentials, auth, firestore
from geminiGenerate.generate import generateOutput
from google.oauth2 import id_token
from google.auth.transport import requests
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

# Initialize Firestore
db = firestore.client()

# Initialize user in session_state
if "user" not in st.session_state:
    st.session_state.user = None

# Initialize conversation ID in session_state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

#initialize active conversation in session_state
if "active_conversation" not in st.session_state:
    st.session_state.active_conversation = None

# Initialize selected conversation in session_state
if "selected_conversation" not in st.session_state:
    st.session_state.selected_conversation = None

#initialize conversation name in session_state
if "conversation_name" not in st.session_state:
    st.session_state.conversation_name = None

st.set_page_config(
            page_title="OutBard",
            page_icon="🌊",
            
        )

def authentication_page():
    st.title("🔐 Login/signup to continue")
    with st.form("login_form"):
        def login_callback():
            try:
                user = auth.get_user_by_email(email)
                st.session_state.user = user
                update_user_session(user.uid, True)  # Update user session in Firestore
                if not st.session_state.user.email_verified:
                    resend_verification_email()
                else:
                    st.snow()
            except Exception as e:
                st.info(f"click again to confirm Login")

        def signup_callback():
            try:
                user = auth.create_user(email=email, password=password)
                st.success(f"User created successfully: {user.email}")
                st.session_state.user = user
                update_user_session(user.uid, True)  # Update user session in Firestore
                if not st.session_state.user.email_verified:
                    resend_verification_email()
                else:
                    st.snow()
            except Exception as e:
                st.info(f"click again to confirm Signup")

        email = st.text_input(":blue[Enter your email]")
        password = st.text_input(":blue[Enter your password]", type="password")
        col1, col2, col3, col4, col5 = st.columns(5,gap="small")
        with col2:
            st.form_submit_button(":green[Login]", help="Login to your account", on_click=login_callback)
        with col3:
            st.write(":blue[or]")
        with col4:
            st.form_submit_button("Signup", help="Create an account", on_click=signup_callback)

# Function to check user session in Firestore
def check_user_session(uid):
    user_session_ref = db.collection("user_sessions").document(uid)
    user_session_data = user_session_ref.get()
    return user_session_data.exists

def update_user_session(uid, authenticated):
    user_session_ref = db.collection("user_sessions").document(uid)
    user_session_ref.set({"authenticated": authenticated})

def save_chat_history(conversation_id, uid, role, content):
    chat_history_ref = db.collection("chat_history").document(uid)
    chat_history = chat_history_ref.get()

    if chat_history.exists:
        chat_data = chat_history.to_dict()
        messages = chat_data.get("messages", [])
        messages.append({"role": role, "content": content})
        chat_history_ref.update({"messages": messages})
    else:
        chat_history_ref.set({"messages": [{"role": role, "content": content}]})
    
    #*** save with a different name
    user_email = st.session_state.user.email if st.session_state.user else None
    conversation_ref = db.collection("users").document(user_email).collection("conversations").document(str(conversation_id))
    conversation = conversation_ref.get()

    if conversation.exists:
        conversation_data = conversation.to_dict()
        messages = conversation_data.get("messages", [])
        messages.append({"role": role, "content": content})
        conversation_ref.update({"messages": messages,})
        # st.success(f"Conversation saved to id: {conversation_id}")
    else:
        conversation_ref.set({"messages": [{"role": role, "content": content}]}, merge=True)

def resend_verification_email():
    user = st.session_state.user
    if not user.email_verified:
        try:
            # auth.send_email_verification(st.session_state.user['idToken'])
            st.write(auth.generate_email_verification_link(user.email))
            st.success("It seems your email is not verified. Click the link above to verify.")
        except Exception as e:
            st.error(f"Failed to resend verification email: {e}")

#sidebar conversations
def create_new_conversation(conv_name):
    # Generate a new conversation ID
    if conv_name:
        conversation_id = str(conv_name)
    else:
        conversation_id = "Untitled--" + str(uuid.uuid4())
    st.session_state.conversation_id = conversation_id
    st.rerun()

def list_conversations():
    # import streamlit as st
    st.sidebar.title("Conversations")

    if st.session_state.user.email_verified:
        # Display a button to create a new conversation
        conv_name = st.text_input(label="rename", label_visibility="hidden", placeholder="Enter conversation name to start")
        if st.button("Start conversation", key="new_conversation"):
            create_new_conversation(conv_name=conv_name)

        # Retrieve user's conversations from Firestore
        user_email = st.session_state.user.email if st.session_state.user else None
        if user_email:
            user_doc_ref = db.collection("users").document(user_email)
            conversations_ref = user_doc_ref.collection("conversations")
            
            # Get all documents from the "conversations" subcollection
            conversations = conversations_ref.stream()

            if conversations:
                user_conversations = [conversation.id for conversation in conversations]

                selected_conversation = st.sidebar.selectbox("Select a previous conversation", user_conversations, index=None, placeholder="Lets talk about this")
                if selected_conversation:
                    if not st.session_state.conversation_id:
                        st.session_state.conversation_id = selected_conversation
                        st.rerun()
                    else:
                        st.session_state.conversation_id = selected_conversation
                        st.session_state.selected_conversation = selected_conversation
            else:
                st.info("No conversations available.")

        else:
            st.info("No user available.")
    else:
        st.sidebar.warning("Please verify your email to continue.")

#what to display before the user creates a conversation 
def display_welcome_message():
    st.title("Welcome to OutBard")
    st.write("👈 :blue[Select a previous conversation or create a new one from the sidebar to get started]")
    with st.sidebar:
        col1, col2, col3 = st.columns(3,gap="medium")
        with col2:
            st.image('images/outbard-icon.png', use_column_width='auto', width=40)
        st.divider()
              
        list_conversations()
        if st.session_state.conversation_id:
            st.empty()
    
    with st.container(border=True):
        st.write("🌊 :green[OutBard is an AI writing assistant web application powered by a Gemini-pro. It allows users to generate code, quotes, text for blog posts, emails, or any other writing project. Users can also chat with OutBard to get creative responses.]")

    
    st.subheader(":bird: What OutBard does")
    #more features coming soon
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.subheader(":large_green_circle: :green[Avaialble features]")
        with st.container(border=True):
                st.write(":book: :green[Generate text for your next blog post, email, or any other writing project.]")
        with st.container(border=True):
        #     st.write(":speech_balloon: :green[Chat with OutBard to get personalized responses.]")
        # with st.container(border=True):
            st.write(":computer: :green[Generate code for your next github project.]")
    with col2:
        st.subheader(":large_blue_circle: :grey[Comming features]")
        with st.container(border=True):
            st.write(":frame_with_picture: :grey[Use images as prompt for specific and personalised responses.]")
        with st.container(border=True):
            st.write(":email: :grey[Send generated content to your email or to your peers.]")

    st.toast("🎈 Collins Omondi")
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
    with col3:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.image('images/comontech-logo.png', use_column_width='auto', width=30)
        st.caption(":flag-ke: Pruodly Kenyan")


def main_app(conversation_id):
    st.title("Welcome to OutBard")
    with st.sidebar:
        col1, col2, col3 = st.columns(3)
        with col2:
            st.image('images/outbard-icon.png', use_column_width='auto', width=40)
        st.divider()

        list_conversations()
        # st.info("Hello, welcome to OutBard. You can use it to generate text for your next blog post, email, or any other writing project. Just type in your prompt and OutBard will generate a response for you. You can also use the app to chat with OutBard. OutBard is a Gemini-pro based AI writing assistant. I'm currently working on some more cool features to make it \"OutBard\". I hope you enjoy using it. If you have any feedback or suggestions, please feel free to reach out to me at [comon928@gmail.com](mailto:comon928@gmail.com)")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    # Retrieve chat history from Firestore
    # chat_history_ref = db.collection("chat_history").document(st.session_state.user.uid)
    # chat_history_data = chat_history_ref.get()

    user_email = st.session_state.user.email if st.session_state.user.email else None
    user_doc_ref = db.collection("users").document(user_email)
    conversations_ref = user_doc_ref.collection("conversations")
    active_conversation_id = st.session_state.active_conversation

    active_conversation_doc = conversations_ref.document(conversation_id).get()
    if active_conversation_doc.exists:
        active_conversation_data = active_conversation_doc.to_dict()

        messages = active_conversation_data.get("messages", [])
        for message in messages:
            st.session_state.messages[conversation_id] = messages  # Save messages for the specific conversation
            role = "user"
            if message["role"] == "assistant":
                role = "🌊"

            content = message["content"]
            with st.chat_message(role):
                st.markdown(content)
    else:
        st.info("No chat history available.")

    full_response = ""
     # Accept user input
    if st.session_state.user.email_verified:
        if prompt := st.chat_input("What's up?"):
            # Save user message to Firestore
            save_chat_history(conversation_id, st.session_state.user.uid, "user", prompt)

            # Save user message to the current conversation
            if conversation_id not in st.session_state.messages:
                st.session_state.messages[conversation_id] = []
            conversation_messages = st.session_state.messages.setdefault(conversation_id, [])
            conversation_messages.append({"role": "user", "content": prompt})

            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add user message to chat history
            conversation_messages = st.session_state.messages.setdefault(conversation_id, [])
            conversation_messages.append({"role": "user", "content": prompt})

            # Display assistant response in chat message container
            with st.chat_message("🌊"):
                message_placeholder = st.empty()

                with st.spinner('Generating....'):
                    assistant_response = generateOutput(prompt)

                # Save assistant response to Firestore
                save_chat_history(conversation_id, st.session_state.user.uid, "assistant", assistant_response)

                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.2)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.rerun()

        # Add assistant response to chat history
        conversation_messages = st.session_state.messages.setdefault(conversation_id, [])
        conversation_messages.append({"role": "assistant", "content": full_response})

if st.session_state.conversation_id:
    main_app(st.session_state.conversation_id)

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
        
        if not st.session_state.conversation_id:
            display_welcome_message()

    except Exception as e:
        st.warning(f"User authentication failed {e}")
else:
    authentication_page()