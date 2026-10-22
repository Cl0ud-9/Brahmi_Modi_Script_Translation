"""Download the Sanskrit-English dictionary used by IAST to English into data/wil.txt (about 9 MB).

The app does this by itself on its first run; this script is for the API, or to fetch it ahead of time.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brahmi_modi.dictionary import ensure, is_installed  # noqa: E402
from brahmi_modi.translate import DICTIONARY_PATH  # noqa: E402


def main():
    if is_installed():
        print('Dictionary already in place:', DICTIONARY_PATH)
        return 0
    print('Downloading the dictionary (about 9 MB)...')
    try:
        ensure()
    except (OSError, ValueError) as e:
        print(f'Could not download the dictionary: {e}', file=sys.stderr)
        return 1
    print('Saved', DICTIONARY_PATH)
    return 0


if __name__ == '__main__':
    sys.exit(main())
