
# OutBard

![outbard-transformed](https://github.com/C-o-m-o-n/outBard/assets/94454803/44c0ede1-baaa-42bf-a37b-8782b659e0f4)

OutBard is a Streamlit-based application powered by a Gemini-pro AI writing assistant. It allows users to generate text for blog posts, emails, or any other writing project. Users can also chat with OutBard to get creative responses.

https://github.com/C-o-m-o-n/outBard/assets/94454803/57f94e0e-5a31-4b92-979a-d6c7b74d694e

## Features

- **User Authentication:** Users can create accounts, log in, and stay authenticated.
- **Conversation History:** Chat history is saved, allowing users to review previous interactions.
- **Firebase Integration:** User data, authentication, and conversation history are stored in Firebase Firestore.
- **Multiple Conversations:** Users can create and switch between different conversations.

## Getting Started

visit the https://outbard.streamlit.app to interact with it

### Prerequisites

- Python 3.7 or later
- Streamlit
- Firebase Admin SDK

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/OutBard.git
    cd OutBard
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up Firebase:

    - Create a Firebase project: [Firebase Console](https://console.firebase.google.com/).
    - Update `secrets.toml` with your Firebase credentials.

4. Run the app:

    ```bash
    streamlit run app.py
    ```

### Usage

1. Open the app in your browser.
2. Sign up or log in to your account.
3. Start a new conversation or continue existing ones.
4. Enjoy generating text or chatting with OutBard!

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is licensed under the [MIT License](LICENSE).
