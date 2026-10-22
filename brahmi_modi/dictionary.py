"""Fetching H. H. Wilson's Sanskrit-English dictionary (1832), which IAST to English looks words up in.

As digitised by the Cologne Digital Sanskrit Dictionaries (CC BY-SA 4.0). The file is pinned to one version and its
checksum verified, so every install looks words up the same way.
"""
import hashlib
import os
import urllib.request

from .translate import DICTIONARY_PATH

URL = ('https://raw.githubusercontent.com/sanskrit-lexicon/csl-orig/'
       '784cab8af458dab7a63511ed33d727351232034f/v02/wil/wil.txt')
SHA256 = '7db0cc57b1c0a69b9f25584a31028d39427210eedb785465a12871f75301530e'


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def is_installed(path=DICTIONARY_PATH):
    return os.path.exists(path) and sha256(path) == SHA256


def ensure(path=DICTIONARY_PATH, url=URL):
    """Download the dictionary unless the right file is already there. Returns True when it is in place.

    Raises OSError if it cannot be downloaded, or ValueError if the download is not the expected file (nothing is
    saved then).
    """
    if is_installed(path):
        return True
    os.makedirs(os.path.dirname(path), exist_ok=True)
    partial = path + '.part'
    urllib.request.urlretrieve(url, partial)
    if sha256(partial) != SHA256:
        os.remove(partial)
        raise ValueError('The downloaded dictionary does not match the expected file.')
    os.replace(partial, path)
    return True
