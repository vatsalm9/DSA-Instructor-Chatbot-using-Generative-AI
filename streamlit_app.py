import os
import streamlit as st
from google import genai
from google.genai import types


def get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY") or "AIzaSyDMOQ-W_7yc-haZL0W4doW5HJCmzsXMKSU"
    return genai.Client(api_key=api_key)


SYSTEM_INSTRUCTION = (
    "You are a Data structure and Algorithm Instructor. You will only reply to the problem related to Data structure and Algorithm. "
    "You have to solve query of user in simplest way"
    "If user ask any question which is not related to Data structure and Algorithm, reply him rudely "
    "Example: If user ask, How are you"
    "You will reply: You dumb ask me some sensible question, like this message you can reply anything more rudely "
    "You have to reply him rudely if question is not related to Data structure and Algorithm. Else reply him politely with simple explanation"
)


def generate_response(client: genai.Client, prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        contents=prompt,
    )
    return response.text or ""


def format_history_as_prompt(history: list[dict[str, str]], latest_user_message: str) -> str:
    lines: list[str] = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "").strip()
        if not content:
            continue
        prefix = "User:" if role == "user" else "Assistant:"
        lines.append(f"{prefix} {content}")
    lines.append(f"User: {latest_user_message.strip()}")
    lines.append("Assistant:")
    return "\n".join(lines)


def main() -> None:
    st.set_page_config(page_title="DSA Instructor", page_icon="🎓")
    st.title("DSA Instructor")

    if "client" not in st.session_state:
        st.session_state.client = get_client()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a DSA question…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        prompt = format_history_as_prompt(st.session_state.messages[:-1], user_input)
        try:
            assistant_text = generate_response(st.session_state.client, prompt).strip()
        except Exception as e:
            assistant_text = f"Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": assistant_text})
        with st.chat_message("assistant"):
            st.markdown(assistant_text)


if __name__ == "__main__":
    main()


