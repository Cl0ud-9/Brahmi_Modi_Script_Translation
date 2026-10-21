"""IAST (romanised Sanskrit and Prakrit) to English, word by word.

Each word is looked up first in a small lexicon of common words and inscription phrases, then in H. H. Wilson's
Sanskrit-English dictionary (1832), which scripts/download_dictionary.py fetches into data/wil.txt. Words found in
neither are returned as they are. This is a glossary, not a grammar-aware translation.
"""
import functools
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICTIONARY_PATH = os.environ.get('BRAHMI_MODI_DICTIONARY', os.path.join(ROOT, 'data', 'wil.txt'))

LEXICON = {
    "anirodham": "non-cessation",
    "anutpādam": "non-arising",
    "pratītyasamutpādaṃ": "dependent origination",
    "saṃsāra": "cycle of rebirth",
    "śivaḥ": "Shiva",
    "rāmāyaṇa": "Ramayana",
    "nirvāṇaṃ": "liberation",
    "anānārtham": "without purpose",
    "mama": "my",
    "nāma": "name",
    "asti": "is",
    "vidyā": "knowledge",
    "vinayaṃ": "humility",
    "dadāti": "gives",
    "aham": "I",
    "paśyāmi": "see",
    "śāntiṃ": "peace",
    "icchāmi": "desire",
    "mokṣaḥ": "liberation",
    "kṛṣṇaḥ": "Krishna",
    "kṣetraṃ": "field",
    "kṣetrajñaḥ": "knower of the field",
    "devo": "god",
    "maheśvaraḥ": "great lord",
    "paraga": "leader",
    "vimocati": "frees",
    "saṃsāraṃ": "cycle of rebirth",
    "yaḥ": "he who",
    "prapañcopaśamaṃ": "cessation of proliferation",
    "śivam": "auspicious, Shiva",
    "pūrve": "in the east",
    "udati": "rises",
    "sūryaḥ": "sun",
    "udeti": "rises",
    "lājinavīsativasābhisitena": "Blessed with twentyfold rice offerings",
    "devānaṃ": "of the gods",
    "piyena": "beloved",
    "piyadasina": "Piyadasi",
    "sakyamūniti": "Gautama Buddha",
    "sakyamuniti": "Gautama Buddha",
}

# IAST to SLP1, the ASCII transliteration the dictionary's headwords use. Longest sequences first.
IAST_TO_SLP1 = [
    ('kh', 'K'), ('gh', 'G'), ('ch', 'C'), ('jh', 'J'), ('ṭh', 'W'), ('ḍh', 'Q'), ('th', 'T'), ('dh', 'D'),
    ('ph', 'P'), ('bh', 'B'), ('ai', 'E'), ('au', 'O'),
    ('ā', 'A'), ('ī', 'I'), ('ū', 'U'), ('ṛ', 'f'), ('ṝ', 'F'), ('ḷ', 'x'), ('ḹ', 'X'),
    ('ṅ', 'N'), ('ñ', 'Y'), ('ṭ', 'w'), ('ḍ', 'q'), ('ṇ', 'R'), ('ś', 'S'), ('ṣ', 'z'),
    ('ṃ', 'M'), ('ṁ', 'M'), ('ḥ', 'H'),
]

ACTION_WORDS = {"is", "gives", "see", "desire", "frees"}
PERSON_WORDS = {"my", "he who", "I"}
NOUN_WORDS = {"name", "knowledge", "humility", "peace", "field", "liberation", "cycle of rebirth",
              "dependent origination", "cessation of proliferation", "sun"}


def iast_to_slp1(word):
    word = unicodedata.normalize('NFC', word.lower())
    for iast, slp1 in IAST_TO_SLP1:
        word = word.replace(iast, slp1)
    return word


def first_gloss(body):
    """The first English sense of a dictionary entry, e.g. 'A deity, a god'."""
    text = re.sub(r'\{#.*?#\}', '', body)
    text = re.sub(r'\{%(.*?)%\}', r'\1', text)
    text = re.sub(r'\([^)]*\)|<[^>]+>', '', text)
    text = re.sub(r'\br\.\s*\d+\w*(?:\s+and\s+\d+\w*)?\s+cls?\.', '', text)
    text = text.split('.E.')[0]
    if '.²1' in text:
        text = re.split(r'\.²\d+', text)[1]
    else:
        text = re.sub(r'^\s*(?:[a-z]{1,4}\.\s*)+', '', text)
    sentence = re.split(r'[.;:](?:\s|$)', text.strip())[0].strip(' ,')
    # Keep whole comma-separated senses while they fit in about 40 characters
    parts = sentence.split(', ')
    short = parts[0]
    for part in parts[1:]:
        if len(short) + 2 + len(part) > 40:
            break
        short += ', ' + part
    return short


ROOT_ENTRY = re.compile(r'\br\.\s*\d+(?:st|nd|rd|th)\b')


@functools.lru_cache(maxsize=1)
def load_dictionary(path=DICTIONARY_PATH):
    """Headword (SLP1) -> glosses, noun and adjective senses before verbal roots. Empty if the file is missing."""
    if not os.path.exists(path):
        return {}
    entries = {}
    with open(path, encoding='utf-8') as f:
        for block in f.read().split('<LEND>'):
            head = re.search(r'<k1>([^<]+)<k2>', block)
            if not head or '¦' not in block:
                continue
            body = ' '.join(block.split('¦', 1)[1].split())
            gloss = first_gloss(body)
            if not gloss:
                continue
            # A verbal root ("r. 1st cl.") is a worse answer than a noun or adjective with the same spelling
            is_root = ROOT_ENTRY.search(body[:120]) is not None
            entries.setdefault(head.group(1), []).append((is_root, gloss))
    return {word: [g for _, g in sorted(senses, key=lambda s: s[0])] for word, senses in entries.items()}


def candidates(word):
    """Spellings to try in the dictionary: the word, its stem without a case ending, and Wilson's 'rCC' spelling."""
    slp1 = iast_to_slp1(word)
    forms = [slp1]
    if len(slp1) > 2 and slp1[-1] in 'HM':
        forms.append(slp1[:-1])
    if len(slp1) > 3 and slp1.endswith('am'):
        forms.append(slp1[:-1])
    forms += [re.sub(r'r([kgcjwqtdpbmyvSzsnR])', r'r\1\1', f) for f in list(forms)]
    return list(dict.fromkeys(forms))


def lookup(word, dictionary=None):
    """English for one IAST word, or None."""
    if word in LEXICON:
        return LEXICON[word]
    dictionary = load_dictionary() if dictionary is None else dictionary
    for form in candidates(word):
        if form in dictionary:
            return dictionary[form][0]
    return None


def post_process(words):
    """Add 'the' before common nouns that do not follow a possessive."""
    result = []
    for i, word in enumerate(words):
        if word in NOUN_WORDS and not (i > 0 and words[i - 1] in PERSON_WORDS):
            result.append('the ' + word)
        else:
            result.append(word)
    return ' '.join(result).strip()


def iast_to_english(text):
    text = unicodedata.normalize('NFC', text.strip())
    if not text:
        raise ValueError('Please enter a valid IAST sentence.')
    if text in LEXICON:
        return LEXICON[text]
    words = re.findall(r"\w+|[^\w\s]", text)
    return post_process([lookup(word) or word for word in words])
