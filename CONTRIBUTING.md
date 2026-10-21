# Contributing to LipiYatra

Thanks for wanting to help. Bug reports, ideas and pull requests are all welcome. Please keep to the
[code of conduct](CODE_OF_CONDUCT.md).

The project is source-available, not open source: see [LICENSE](LICENSE). You may fork this repository to prepare
contributions, but not to publish or share your own copies. By opening a pull request you agree to clause 8 of the
license: you have the right to submit the change, and it becomes part of the project under the author's terms.

## Before you start

- **Found a wrong transliteration or translation?** Open an issue with the input, what came out and what it should
  be.
- **Have an idea?** Open an issue before writing code, so we can agree on the approach. Large changes that were not
  discussed may be closed.
- **Found a security problem?** Do not open a public issue. Report it privately: see [SECURITY.md](SECURITY.md).

## Setup

Requirements: Python 3.11, 3.12, 3.13 or 3.14.

```bash
git clone https://github.com/<your-account>/LipiYatra.git
cd LipiYatra
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/download_dictionary.py
ruff check .
pytest
```

## What a pull request needs

- `ruff check .` and `pytest` pass.
- A new behaviour comes with a test that fails without it.
- Transliteration changes are checked against the Unicode character names, which the tables are built from.
- A retrained or re-exported model comes with its character error rate on the held-out lines, measured the way the
  README describes, and the README's results are updated. Model checkpoints go to the Kaggle dataset, not git.
- The OCR samples in `samples/` stay real held-out lines, not ones picked because the model reads them.

## Style

Match the surrounding code. Comments are short and explain why, not what. Plain wording in docs and in the app, with
no marketing language.
