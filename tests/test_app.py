"""The Streamlit app, run headless with Streamlit's own test harness. No API process is needed."""
import os

import pytest
from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def app(monkeypatch):
    monkeypatch.delenv('API_BASE_URL', raising=False)
    at = AppTest.from_file(os.path.join(ROOT, 'app.py'), default_timeout=60)
    return at.run()


def last_reply(at):
    return at.chat_message[-1].markdown[-1].value


@pytest.mark.parametrize('prompt, expected', [
    ('convert brahmi: 𑀫𑀫 𑀦𑀸𑀫', 'Sanskrit (IAST): mama nāma'),
    ('convert modi: 𑘦𑘻𑘟𑘲', 'Sanskrit (IAST): modī'),
    ('convert iast: mama nāma', 'English: my name'),
])
def test_chat_converts_without_an_api(app, prompt, expected):
    app.chat_input[0].set_value(prompt).run()
    assert not app.exception
    assert last_reply(app) == expected


def test_chat_explains_what_it_understands(app):
    app.chat_input[0].set_value('hello').run()
    assert 'convert brahmi' in last_reply(app)


def test_image_tab_reads_a_sample(app):
    app.selectbox[0].set_value('brahmi_1.png').run()
    assert not app.exception
    text = ' '.join(m.value for m in app.markdown)
    assert 'Brahmi:' in text and 'IAST:' in text
    assert any('Correct' in c.value or 'actually says' in c.value for c in app.caption)
