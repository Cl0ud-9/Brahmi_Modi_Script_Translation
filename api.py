"""HTTP API: transliteration, IAST to English, and Brahmi text recognition.

The Streamlit app does not need it; it is for other clients. Run it with `uvicorn api:app --port 8001`, or
`python api.py`.
"""
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from brahmi_modi import __version__
from brahmi_modi.service import MAX_IMAGE_BYTES, MAX_TEXT, InputError, convert, read_brahmi
from brahmi_modi.translate import load_dictionary

app = FastAPI(title='LipiYatra', version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('ALLOWED_ORIGINS', 'http://localhost:8501').split(','),
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)


class TextInput(BaseModel):
    text: str = Field(max_length=MAX_TEXT)


def answer(work, *args):
    try:
        return work(*args)
    except InputError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@app.get('/health')
def health():
    return {'status': 'ok', 'version': __version__, 'dictionary_entries': len(load_dictionary())}


@app.post('/brahmi-to-iast')
def convert_brahmi(body: TextInput):
    return {'output': answer(convert, 'brahmi', body.text)}


@app.post('/modi-to-iast')
def convert_modi(body: TextInput):
    return {'output': answer(convert, 'modi', body.text)}


@app.post('/iast-to-english')
def convert_iast(body: TextInput):
    return {'output': answer(convert, 'iast', body.text)}


@app.post('/ocr/brahmi')
async def ocr_brahmi(image: UploadFile = File(...)):
    data = await image.read(MAX_IMAGE_BYTES + 1)
    return answer(read_brahmi, data)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8001)
