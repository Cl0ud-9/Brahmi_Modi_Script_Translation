import json
import os

import numpy as np
import pytest
from PIL import Image, ImageOps

from brahmi_modi.ocr import HEIGHT, WIDTH, get_ocr, prepare

SAMPLES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'samples')
with open(os.path.join(SAMPLES, 'samples.json'), encoding='utf-8') as f:
    MANIFEST = json.load(f)


def test_prepare_matches_the_training_input():
    array = prepare(Image.new('RGB', (500, 120), 'white'))
    assert array.shape == (HEIGHT, WIDTH)
    assert array.dtype == np.float32
    assert array.min() >= -1 and array.max() <= 1


def test_light_text_on_dark_is_inverted():
    image = Image.open(os.path.join(SAMPLES, MANIFEST[0]['file']))
    assert np.allclose(prepare(ImageOps.invert(image.convert('L'))), prepare(image), atol=0.02)


@pytest.mark.parametrize('sample', MANIFEST[:5], ids=lambda s: s['file'])
def test_reads_held_out_samples(sample):
    assert get_ocr().read(Image.open(os.path.join(SAMPLES, sample['file']))) == sample['text']


def test_the_model_has_one_output_per_character_plus_blank():
    ocr = get_ocr()
    logits = ocr.session.run(None, {ocr.input_name: prepare(Image.new('L', (256, 64), 255))[None, None]})[0]
    assert logits.shape[-1] == len(ocr.chars) + 1
