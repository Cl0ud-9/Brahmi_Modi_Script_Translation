"""LipiYatra in the browser: `streamlit run app.py`.

Everything runs in this one process. To use a separately running API instead (`python api.py`), set API_BASE_URL.
"""
import json
import os
import re
import time

import streamlit as st
from PIL import Image

from brahmi_modi import service
from brahmi_modi.dictionary import ensure as ensure_dictionary

API_BASE_URL = os.environ.get('API_BASE_URL', '').rstrip('/')
SAMPLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samples')

ENDPOINTS = {'brahmi': 'brahmi-to-iast', 'iast': 'iast-to-english', 'modi': 'modi-to-iast'}
LABELS = {'brahmi': 'Sanskrit (IAST)', 'iast': 'English', 'modi': 'Sanskrit (IAST)'}
HELP = ("I can convert text with 'convert brahmi: <text>', 'convert iast: <text>' or 'convert modi: <text>'. "
        "For example, try 'convert brahmi: 𑀫𑀫 𑀦𑀸𑀫'.")


@st.cache_resource(show_spinner='Fetching the Sanskrit-English dictionary (about 9 MB, first run only)...')
def dictionary_ready():
    """Download the dictionary once per server. Without it, only the built-in word list is translated."""
    try:
        return ensure_dictionary()
    except (OSError, ValueError):
        return False


def call_api(path, **kwargs):
    """POST to a separately running API. Returns (json, None) or (None, error message)."""
    import requests

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


def convert(script, text):
    """(output, None) or (None, error message)."""
    if API_BASE_URL:
        result, error = call_api(ENDPOINTS[script], json={'text': text})
        return (result['output'], None) if result else (None, error)
    try:
        return service.convert(script, text), None
    except service.InputError as e:
        return None, str(e)


def read_image(name, data):
    """({'brahmi', 'iast'}, None) or (None, error message)."""
    if API_BASE_URL:
        return call_api('ocr/brahmi', files={'image': (name, data)})
    try:
        return service.read_brahmi(data), None
    except service.InputError as e:
        return None, str(e)


def answer(prompt):
    match = re.match(r'convert\s+(brahmi|iast|modi)\s*[:\s]\s*(.+)', prompt, re.IGNORECASE | re.DOTALL)
    if not match:
        return HELP
    script, text = match.group(1).lower(), match.group(2).strip()
    output, error = convert(script, text)
    return f'Error: {error}' if error else f'{LABELS[script]}: {output}'


st.set_page_config(page_title='LipiYatra', page_icon='🌍')
st.title('🌍 LipiYatra')
st.caption('A travel companion for Brahmi and Modi inscriptions: convert them to romanised Sanskrit (IAST), '
           'and IAST to English.')

if not API_BASE_URL and not dictionary_ready():
    st.warning('The Sanskrit-English dictionary could not be downloaded, so IAST to English only knows the built-in '
               'word list. Check the internet connection and reload.')

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
                for i in range(1, len(reply), 3):
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
        with open(os.path.join(SAMPLES, choice), 'rb') as f:
            name, data = choice, f.read()
    elif upload is not None:
        name, data = upload.name, upload.getvalue()
    else:
        name, data = None, None

    if data:
        result, error = read_image(name, data)
        if error:
            st.error(error)
        else:
            st.image(Image.open(upload or os.path.join(SAMPLES, choice)), caption=name)
            if not result['brahmi']:
                st.warning('No Brahmi text was recognised in this image.')
            else:
                st.markdown(f"**Brahmi:** {result['brahmi']}  \n**IAST:** {result['iast']}")
                expected = next((s['text'] for s in samples if s['file'] == name and choice != 'Upload my own'), None)
                if expected is not None:
                    st.caption('Correct ✓' if expected == result['brahmi'] else f'The image actually says {expected}')
