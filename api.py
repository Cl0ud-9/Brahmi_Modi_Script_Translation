"""HTTP API for the app: transliteration, IAST to English, and Brahmi text recognition.

Run it with `uvicorn api:app --port 8001`, or `python api.py`.
"""
import io
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field

from brahmi_modi import __version__
from brahmi_modi.ocr import get_ocr
from brahmi_modi.translate import iast_to_english, load_dictionary
from brahmi_modi.transliterate import brahmi_to_iast, modi_to_iast

MAX_TEXT = 5000
MAX_IMAGE_BYTES = 5 * 1024 * 1024
# Refuse decompression bombs: far more pixels than any real photo of a line of text
Image.MAX_IMAGE_PIXELS = 40_000_000

app = FastAPI(title='Brahmi and Modi Script Translation', version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('ALLOWED_ORIGINS', 'http://localhost:8501').split(','),
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)


class TextInput(BaseModel):
    text: str = Field(max_length=MAX_TEXT)


def output(convert, text):
    try:
        return {'output': convert(text)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/health')
def health():
    return {'status': 'ok', 'version': __version__, 'dictionary_entries': len(load_dictionary())}


@app.post('/brahmi-to-iast')
def convert_brahmi(body: TextInput):
    return output(brahmi_to_iast, body.text)


@app.post('/modi-to-iast')
def convert_modi(body: TextInput):
    return output(modi_to_iast, body.text)


@app.post('/iast-to-english')
def convert_iast(body: TextInput):
    return output(iast_to_english, body.text)


@app.post('/ocr/brahmi')
async def read_brahmi(image: UploadFile = File(...)):
    data = await image.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail='Images must be 5 MB or smaller.')
    try:
        picture = Image.open(io.BytesIO(data))
        picture.load()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError):
        raise HTTPException(status_code=400, detail='That file is not an image this API can read.')
    brahmi = get_ocr().read(picture)
    return {'brahmi': brahmi, 'iast': brahmi_to_iast(brahmi)}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8001)
