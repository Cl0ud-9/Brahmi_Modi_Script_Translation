"""What the app and the API both offer, with the same limits: convert text, and read a Brahmi image.

The Streamlit app calls these directly, so it runs on its own; api.py serves them over HTTP for other clients.
"""
import io

from PIL import Image, UnidentifiedImageError

from .ocr import get_ocr
from .translate import iast_to_english
from .transliterate import brahmi_to_iast, modi_to_iast

MAX_TEXT = 5000
MAX_IMAGE_BYTES = 5 * 1024 * 1024
# Refuse decompression bombs: far more pixels than any real photo of a line of text
Image.MAX_IMAGE_PIXELS = 40_000_000

CONVERTERS = {'brahmi': brahmi_to_iast, 'modi': modi_to_iast, 'iast': iast_to_english}


class InputError(ValueError):
    """The input cannot be used; the message says why, in words a visitor understands."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def convert(script, text):
    """Brahmi or Modi to IAST, or IAST to English."""
    if script not in CONVERTERS:
        raise InputError(f"Unknown script {script!r}: use brahmi, modi or iast.")
    if len(text) > MAX_TEXT:
        raise InputError(f'Text is limited to {MAX_TEXT:,} characters.', status=422)
    try:
        return CONVERTERS[script](text)
    except ValueError as e:
        raise InputError(str(e)) from e


def read_brahmi(data):
    """The Brahmi text in an image (the file's bytes) and its IAST, as {'brahmi': ..., 'iast': ...}."""
    if len(data) > MAX_IMAGE_BYTES:
        raise InputError('Images must be 5 MB or smaller.', status=413)
    try:
        picture = Image.open(io.BytesIO(data))
        picture.load()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError):
        raise InputError('That file is not an image this app can read.')
    brahmi = get_ocr().read(picture)
    return {'brahmi': brahmi, 'iast': brahmi_to_iast(brahmi) if brahmi else ''}
