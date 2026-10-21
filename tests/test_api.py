import io
import json
import os

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api import app

client = TestClient(app)
SAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'samples')


def test_health():
    body = client.get('/health').json()
    assert body['status'] == 'ok'


@pytest.mark.parametrize('path, text, expected', [
    ('brahmi-to-iast', '𑀫𑀫 𑀦𑀸𑀫', 'mama nāma'),
    ('modi-to-iast', '𑘦𑘻𑘟𑘲', 'modī'),
    ('iast-to-english', 'mama nāma', 'my name'),
])
def test_text_endpoints(path, text, expected):
    response = client.post(f'/{path}', json={'text': text})
    assert response.status_code == 200
    assert response.json() == {'output': expected}


def test_bad_input_is_a_client_error():
    assert client.post('/iast-to-english', json={'text': ' '}).status_code == 400
    assert client.post('/brahmi-to-iast', json={'text': 'x' * 5001}).status_code == 422
    assert client.post('/brahmi-to-iast', json={}).status_code == 422


def test_ocr_reads_a_sample():
    with open(os.path.join(SAMPLES, 'samples.json'), encoding='utf-8') as f:
        sample = json.load(f)[0]
    with open(os.path.join(SAMPLES, sample['file']), 'rb') as f:
        response = client.post('/ocr/brahmi', files={'image': (sample['file'], f, 'image/png')})
    assert response.status_code == 200
    assert response.json() == {'brahmi': sample['text'], 'iast': sample['iast']}


def test_ocr_rejects_files_that_are_not_images():
    response = client.post('/ocr/brahmi', files={'image': ('notes.txt', b'hello', 'text/plain')})
    assert response.status_code == 400


def test_ocr_rejects_oversized_uploads():
    big = io.BytesIO()
    Image.effect_noise((1800, 1800), 100).convert('RGB').save(big, 'PNG')
    assert big.tell() > 5 * 1024 * 1024
    response = client.post('/ocr/brahmi', files={'image': ('big.png', big.getvalue(), 'image/png')})
    assert response.status_code == 413
