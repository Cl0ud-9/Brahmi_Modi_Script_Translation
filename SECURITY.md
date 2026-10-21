# Security policy

## Reporting a vulnerability

Please do not open a public issue for a security problem.

Report it privately through GitHub: open the
[Security tab](https://github.com/Cl0ud-9/LipiYatra/security) and choose **Report a
vulnerability**, or go straight to
[the advisory form](https://github.com/Cl0ud-9/LipiYatra/security/advisories/new). Only the
maintainer sees what you send.

Please include what you found, how to reproduce it (a request or an image is ideal), and what you think an attacker
could do with it. The maintainer aims to answer within a week, and you will be credited in the fix unless you would
rather not be.

## What counts

- An uploaded image or request that makes the API run code, read files, or use far more memory or time than its
  limits (5 MB images, 40 million pixels, 5,000 characters of text) should allow.
- A way to make `scripts/download_dictionary.py` save a file it has not verified.
- Script injection through text shown in the app.

Not in scope: problems in FastAPI, Streamlit, ONNX Runtime or Pillow themselves (report those upstream), and settings
you changed yourself, such as exposing the API to a network.

## Keeping your own copy safe

- The API listens on `127.0.0.1` only. Put it behind authentication before exposing it to anyone else.
- `ALLOWED_ORIGINS` sets which web pages may call the API from a browser. Keep it to the app's own address.
- Only load ONNX models from this repository or ones you exported yourself.

## Supported versions

Only the current `main` gets fixes.
