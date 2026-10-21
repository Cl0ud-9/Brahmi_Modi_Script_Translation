"""Brahmi text recognition with the CRNN trained in notebooks/brahmi_crnn.ipynb, exported to ONNX.

The model was trained on synthetic lines: up to seven Brahmi characters rendered in black on a white 256x64 image.
It reads images in that format well (11.1% character error on held-out lines), and does not read photographs
of inscriptions, whose lighting, wear and layout it has never seen.
"""
import functools
import json
import os

import numpy as np
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT, 'models', 'brahmi_crnn.onnx')
CHARS_PATH = os.path.join(ROOT, 'models', 'brahmi_chars.json')

WIDTH, HEIGHT = 256, 64


def prepare(image):
    """Grey 256x64 array scaled to [-1, 1], as in training. Light text on a dark background is inverted."""
    grey = ImageOps.exif_transpose(image).convert('L').resize((WIDTH, HEIGHT), Image.BILINEAR)
    pixels = np.asarray(grey, dtype=np.float32)
    if pixels.mean() < 128:
        pixels = 255 - pixels
    return (pixels / 255.0 - 0.5) / 0.5


class BrahmiOCR:
    def __init__(self, model_path=MODEL_PATH, chars_path=CHARS_PATH):
        import onnxruntime

        self.session = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        with open(chars_path, encoding='utf-8') as f:
            self.chars = json.load(f)['chars']

    def decode(self, logits):
        """Greedy CTC decoding: merge repeats, drop the blank (the last class)."""
        text, previous = [], -1
        for index in logits.argmax(axis=-1):
            if index != previous and index < len(self.chars):
                text.append(self.chars[index])
            previous = index
        return ''.join(text).strip()

    def read(self, image):
        """Brahmi text in a PIL image."""
        batch = prepare(image)[None, None]
        logits = self.session.run(None, {self.input_name: batch})[0]
        return self.decode(logits[:, 0])


@functools.lru_cache(maxsize=1)
def get_ocr():
    return BrahmiOCR()
