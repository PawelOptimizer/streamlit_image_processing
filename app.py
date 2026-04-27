import streamlit as st
import os
import time
from datetime import date
from streamlit.errors import StreamlitSecretNotFoundError
from openai import OpenAI
from utils import get_image_description, resolve_api_key

DEFAULT_PROMPT = (
    "Describe what you see in this image in simple language. "
    "Mention key objects, scene, and possible context."
)
FALLBACK_MODELS = ["gpt-4.1-mini", "gpt-4.1-nano"]

def get_secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except StreamlitSecretNotFoundError:
        return default

DISABLE_MANUAL_API_KEY_INPUT = (
    str(get_secret("DISABLE_MANUAL_API_KEY_INPUT", "")).lower() in {"1", "true", "yes"}
)

def get_int_config(name, default):
    raw_value = get_secret(name, os.environ.get(name, default))
    try:
        value = int(raw_value)
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default

MAX_REQUESTS_PER_MINUTE = get_int_config("MAX_REQUESTS_PER_MINUTE", 5)
MAX_REQUESTS_PER_DAY = get_int_config("MAX_REQUESTS_PER_DAY", 100)

def fetch_available_gpt_models(client):
    models = client.models.list()
    available_model_ids = {model.id for model in models.data}
    allowed_models = [model for model in FALLBACK_MODELS if model in available_model_ids]
    return allowed_models

# Streamlit app layout
st.set_page_config(page_title="Image Description Workshop", page_icon=":camera:")
st.title("Image Description with OpenAI Vision")
st.write("Upload an image, enter your own prompt, and get a model response.")
st.caption(
    f"Rate limits: {MAX_REQUESTS_PER_MINUTE} request(s)/minute and {MAX_REQUESTS_PER_DAY} request(s)/day per user session."
)

api_key = resolve_api_key()
if not api_key:
    api_key = get_secret("OPENAI_API_KEY", "")

if not DISABLE_MANUAL_API_KEY_INPUT:
    manual_api_key = st.text_input(
        "OpenAI API key (optional if OPENAI_API_KEY is set)",
        type="password",
        help="If empty, the app will use OPENAI_API_KEY from environment variables or Streamlit secrets.",
    )
    if manual_api_key:
        api_key = manual_api_key

if api_key:
    client = OpenAI(api_key=api_key)
    try:
        available_models = fetch_available_gpt_models(client)
    except Exception as e:
        available_models = FALLBACK_MODELS
        st.warning(f"Could not fetch models from API. Using fallback list. Details: {e}")

    if not available_models:
        available_models = FALLBACK_MODELS
        st.warning("No GPT models were returned by the API. Using fallback model list.")

    default_model = "gpt-4.1-mini" if "gpt-4.1-mini" in available_models else available_models[0]
    default_index = available_models.index(default_model)
    model_choice = st.selectbox("Select model", available_models, index=default_index)
    custom_model = st.text_input(
        "Custom model ID (optional)",
        value="",
        help="If set, this value overrides the model selected above.",
    )

    prompt = st.text_area(
        "Prompt",
        value=DEFAULT_PROMPT,
        height=120,
    )

    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        try:
            st.image(uploaded_file, caption="Uploaded image", use_container_width=True)

            if st.button("Analyze image", type="primary"):
                if "request_timestamps" not in st.session_state:
                    st.session_state["request_timestamps"] = []
                if "daily_usage" not in st.session_state:
                    st.session_state["daily_usage"] = {"date": date.today().isoformat(), "count": 0}

                now = time.time()
                recent_timestamps = [
                    ts for ts in st.session_state["request_timestamps"] if now - ts < 60
                ]
                st.session_state["request_timestamps"] = recent_timestamps

                if len(recent_timestamps) >= MAX_REQUESTS_PER_MINUTE:
                    st.error("Rate limit reached: too many requests in the last minute. Please wait.")
                    st.stop()

                today = date.today().isoformat()
                if st.session_state["daily_usage"]["date"] != today:
                    st.session_state["daily_usage"] = {"date": today, "count": 0}

                if st.session_state["daily_usage"]["count"] >= MAX_REQUESTS_PER_DAY:
                    st.error("Daily limit reached for this session. Please try again tomorrow.")
                    st.stop()

                st.session_state["request_timestamps"].append(now)
                st.session_state["daily_usage"]["count"] += 1

                with st.spinner("Calling model..."):
                    final_prompt = prompt.strip() or DEFAULT_PROMPT
                    final_model = custom_model.strip() or model_choice
                    description = get_image_description(client, uploaded_file, final_prompt, final_model)
                st.subheader("Model response")
                st.write(description)
        except Exception as e:
            st.error(f"Error: {e}")
else:
    if DISABLE_MANUAL_API_KEY_INPUT:
        st.warning("No API key configured. Set OPENAI_API_KEY in environment variables or Streamlit secrets.")
    else:
        st.warning("Please provide an API key in the field above or set OPENAI_API_KEY locally.")
