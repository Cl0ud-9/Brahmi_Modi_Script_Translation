"""Download the Sanskrit-English dictionary used by IAST to English into data/wil.txt.

H. H. Wilson, A Dictionary in Sanscrit and English (1832), as digitised by the Cologne Digital Sanskrit Dictionaries
(CC BY-SA 4.0). The file is pinned to one version and checked, so every install looks words up the same way.
"""
import hashlib
import os
import sys
import urllib.request

URL = ('https://raw.githubusercontent.com/sanskrit-lexicon/csl-orig/'
       '784cab8af458dab7a63511ed33d727351232034f/v02/wil/wil.txt')
SHA256 = '7db0cc57b1c0a69b9f25584a31028d39427210eedb785465a12871f75301530e'
TARGET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'wil.txt')


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    if os.path.exists(TARGET) and sha256(TARGET) == SHA256:
        print('Dictionary already in place:', TARGET)
        return 0
    os.makedirs(os.path.dirname(TARGET), exist_ok=True)
    print('Downloading the dictionary (about 9 MB)...')
    partial = TARGET + '.part'
    urllib.request.urlretrieve(URL, partial)
    if sha256(partial) != SHA256:
        os.remove(partial)
        print('The download does not match the expected file. Nothing was saved.', file=sys.stderr)
        return 1
    os.replace(partial, TARGET)
    print('Saved', TARGET)
    return 0


if __name__ == '__main__':
    sys.exit(main())
