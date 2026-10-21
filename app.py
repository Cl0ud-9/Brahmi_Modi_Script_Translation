"""Streamlit front end. Start the API first (`python api.py`), then `streamlit run app.py`."""
import json
import os
import re
import time

import requests
import streamlit as st
from PIL import Image

API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8001')
SAMPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samples')

ENDPOINTS = {'brahmi': 'brahmi-to-iast', 'iast': 'iast-to-english', 'modi': 'modi-to-iast'}
LABELS = {'brahmi': 'Sanskrit (IAST)', 'iast': 'English', 'modi': 'Sanskrit (IAST)'}
HELP = ("I can convert text with 'convert brahmi: <text>', 'convert iast: <text>' or 'convert modi: <text>'. "
        "For example, try 'convert brahmi: 𑀫𑀫 𑀦𑀸𑀫'.")


def call_api(path, **kwargs):
    """POST to the API. Returns (json, None) or (None, error message)."""
    try:
        response = requests.post(f'{API_BASE_URL}/{path}', timeout=60, **kwargs)
    except requests.RequestException:
        return None, f'Could not reach the API at {API_BASE_URL}. Is `python api.py` running?'
    if response.ok:
        return response.json(), None
    try:
        return None, response.json().get('detail', response.text)
    except ValueError:
        return None, response.text


def answer(prompt):
    match = re.match(r'convert\s+(brahmi|iast|modi)\s*[:\s]\s*(.+)', prompt, re.IGNORECASE | re.DOTALL)
    if not match:
        return HELP
    script, text = match.group(1).lower(), match.group(2).strip()
    result, error = call_api(ENDPOINTS[script], json={'text': text})
    return f'Error: {error}' if error else f"{LABELS[script]}: {result['output']}"


st.set_page_config(page_title='Travel Bot', page_icon='🌍')
st.title('🌍 Travel Bot')
st.caption('Read Brahmi and Modi inscriptions: convert them to romanised Sanskrit (IAST), and IAST to English.')

if 'messages' not in st.session_state or st.button('🔁 Reset chat'):
    st.session_state.messages = []

chat_tab, ocr_tab = st.tabs(['💬 Convert text', '🖼️ Read a Brahmi image'])

with chat_tab:
    # Messages go in a container above the input, so new ones do not appear below it
    history = st.container()
    prompt = st.chat_input("e.g. 'convert brahmi: 𑀫𑀫 𑀦𑀸𑀫', 'convert iast: mama nāma', 'convert modi: 𑘦𑘻𑘟𑘲'")
    with history:
        for message in st.session_state.messages:
            with st.chat_message(message['role'], avatar=message['avatar']):
                st.markdown(message['content'])
        if prompt:
            st.session_state.messages.append({'role': 'user', 'content': prompt, 'avatar': '👤'})
            with st.chat_message('user', avatar='👤'):
                st.markdown(prompt)
            reply = answer(prompt)
            st.session_state.messages.append({'role': 'assistant', 'content': reply, 'avatar': '🐣'})
            with st.chat_message('assistant', avatar='🐣'):
                placeholder = st.empty()
                for i in range(1, len(reply) + 1):
                    placeholder.markdown(reply[:i] + '▌')
                    time.sleep(0.01)
                placeholder.markdown(reply)

with ocr_tab:
    st.info('The recogniser was trained on printed Brahmi lines of up to seven characters, dark on light, like the '
            'samples below. It does not read photographs of weathered inscriptions yet.')
    with open(os.path.join(SAMPLES, 'samples.json'), encoding='utf-8') as f:
        samples = json.load(f)
    choice = st.selectbox('Try a sample', ['Upload my own'] + [s['file'] for s in samples])
    upload = st.file_uploader('Brahmi image', type=['png', 'jpg', 'jpeg']) if choice == 'Upload my own' else None

    if choice != 'Upload my own':
        name, data = choice, open(os.path.join(SAMPLES, choice), 'rb').read()
    elif upload is not None:
        name, data = upload.name, upload.getvalue()
    else:
        name, data = None, None

    if data:
        st.image(Image.open(upload or os.path.join(SAMPLES, choice)), caption=name)
        with st.spinner('Reading the image...'):
            result, error = call_api('ocr/brahmi', files={'image': (name, data)})
        if error:
            st.error(error)
        elif not result['brahmi']:
            st.warning('No Brahmi text was recognised in this image.')
        else:
            st.markdown(f"**Brahmi:** {result['brahmi']}  \n**IAST:** {result['iast']}")
            expected = next((s['text'] for s in samples if s['file'] == name and choice != 'Upload my own'), None)
            if expected is not None:
                st.caption('Correct ✓' if expected == result['brahmi'] else f'The image actually says {expected}')
