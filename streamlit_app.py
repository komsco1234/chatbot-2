import streamlit as st
from openai import AuthenticationError, OpenAI, RateLimitError

LANGUAGES = {
    "한국어": {
        "name": "Korean",
        "chat_placeholder": "무엇이든 물어보세요.",
        "api_key_help": "계속하려면 OpenAI API 키를 입력해 주세요.",
    },
    "English": {
        "name": "English",
        "chat_placeholder": "Ask anything.",
        "api_key_help": "Please add your OpenAI API key to continue.",
    },
    "日本語": {
        "name": "Japanese",
        "chat_placeholder": "何でも聞いてください。",
        "api_key_help": "続行するにはOpenAI APIキーを入力してください。",
    },
    "中文": {
        "name": "Chinese",
        "chat_placeholder": "请随时提问。",
        "api_key_help": "请添加 OpenAI API 密钥以继续。",
    },
    "Français": {
        "name": "French",
        "chat_placeholder": "Posez votre question.",
        "api_key_help": "Veuillez ajouter votre clé API OpenAI pour continuer.",
    },
    "Español": {
        "name": "Spanish",
        "chat_placeholder": "Pregunta lo que quieras.",
        "api_key_help": "Agrega tu clave API de OpenAI para continuar.",
    },
    "Deutsch": {
        "name": "German",
        "chat_placeholder": "Frag mich etwas.",
        "api_key_help": "Bitte gib deinen OpenAI API-Schlüssel ein, um fortzufahren.",
    },
}

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

st.sidebar.header("Settings")

selected_language = st.sidebar.selectbox(
    "Response language",
    options=list(LANGUAGES.keys()),
    index=0,
)
language_config = LANGUAGES[selected_language]

try:
    saved_api_key = st.secrets.get("OPENAI_API_KEY", "")
except Exception:
    saved_api_key = ""

typed_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    value="",
    type="password",
    placeholder="sk-...",
    help="Paste your OpenAI API key here. The key is only used for this Streamlit session.",
)
openai_api_key = typed_api_key.strip() or saved_api_key

if saved_api_key and not typed_api_key.strip():
    st.sidebar.success("Using API key from Streamlit secrets.")

if st.sidebar.button("Clear chat"):
    st.session_state.messages = []
    st.rerun()

if not openai_api_key:
    st.info(language_config["api_key_help"], icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input(language_config["chat_placeholder"]):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        messages = [
            {
                "role": "system",
                "content": (
                    f"Always answer in {language_config['name']}. "
                    "If the user writes in another language, still respond in the selected language. "
                    "Keep answers helpful, natural, and concise."
                ),
            }
        ]
        messages.extend(
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        )

        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
            )

            # Stream the response to the chat using `st.write_stream`, then store it in
            # session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except AuthenticationError:
            st.error("OpenAI API key is invalid or missing. Please check the key in the sidebar and try again.")
        except RateLimitError:
            st.error("OpenAI API rate limit or quota was reached. Please check your OpenAI account usage and try again later.")
