# Changelog

What changed in each version of LipiYatra.

The format follows [Keep a Changelog](https://keepachangelog.com), and the versions follow
[Semantic Versioning](https://semver.org).

## [1.1.1] - 2026-10-22

### Changed

- Python 3.14 is supported: the tests pass on it, and continuous integration now runs on Python 3.11 to 3.14.

## [1.1.0] - 2026-10-21

### Changed

- The project is now called LipiYatra, from *lipi*, script, and *yātrā*, journey. The repository moved from
  `Cl0ud-9/Brahmi_Modi_Script_Translation` to `Cl0ud-9/LipiYatra`; the old addresses redirect to it.
- The app and the API carry the new name.

## [1.0.0] - 2026-10-21

The first complete public version: the app, the API, the trained recogniser and the notebooks behind them.

### Added

- The Travel Bot app (Streamlit): convert Brahmi, Modi and IAST text in a chat, and read Brahmi images.
- Brahmi text recognition with the CRNN trained on 10,000 synthetic lines, exported to ONNX: 11.1% character error
  and 78.9% of lines exactly right on 1,999 held-out lines.
- `POST /ocr/brahmi`, which reads an uploaded image, and `GET /health`.
- `scripts/download_dictionary.py`, which fetches the Sanskrit-English dictionary pinned to one version and checks it.
- The research notebooks: dataset generation, the CRNN, preprocessing, IAST translation, and earlier experiments.
- Sample images, tests, continuous integration, and the security, contributing and conduct guides.
- The training data and checkpoints on
  [Kaggle](https://www.kaggle.com/datasets/paragtonpe/brahmi-ocr-synthetic-dataset).

### Fixed

- Modi to IAST mapped most vowel signs, the anusvara, the visarga and the virama to the wrong code points, so most
  Modi text came out wrong (𑘦𑘻𑘟𑘲 gave "maidā" instead of "modī"). The tables are now built from the Unicode
  character names.
- Brahmi to IAST read the vowel sign u as ū, and the letters e, ai, o and au as their neighbours.
- IAST to English looked words up in a form the dictionary does not use, so only the small built-in word list was
  ever found. Words are now matched in the dictionary's own transliteration, with case endings and its spellings,
  and nouns are preferred over verb roots.
- The recogniser's inference code scaled pixels differently from training, which made it read almost nothing
  correctly (98.6% character error). It now uses the training scale.
- The app's image tabs returned stored text for a few known file names instead of reading the image. That is replaced
  by the real recogniser, and the Modi image tab, which had no model behind it, is removed.

### Changed

- The code is split into the `brahmi_modi` package (`transliterate`, `translate`, `ocr`), with `api.py` and `app.py`
  as thin layers on top. `end.py` is now `app.py`.
- The API listens on `127.0.0.1`, limits text to 5,000 characters and images to 5 MB, and the app reads its address
  from `API_BASE_URL`.
- The `indic-nlp-library` dependency is gone: on romanised text it changed nothing.

## Before 1.0.0

The repository held the transliteration API (`api.py`), published on 2025-05-14. The app and the trained models stayed
on the author's computer until this version.
