"""Brahmi and Modi script to IAST (Latin) transliteration.

Both scripts are abugidas: a consonant carries an inherent "a" unless a vowel sign or the virama follows
it. The letter tables are built from the Unicode character names, so every code point maps to the sound
its name gives and nothing has to be typed by hand.
"""
import unicodedata

VOWELS = {
    'A': 'a', 'AA': 'ā', 'I': 'i', 'II': 'ī', 'U': 'u', 'UU': 'ū',
    'VOCALIC R': 'ṛ', 'VOCALIC RR': 'ṝ', 'VOCALIC L': 'ḷ', 'VOCALIC LL': 'ḹ',
    'E': 'e', 'AI': 'ai', 'O': 'o', 'AU': 'au',
    'BHATTIPROLU AA': 'ā', 'OLD TAMIL SHORT E': 'e', 'OLD TAMIL SHORT O': 'o',
}

CONSONANTS = {
    'KA': 'k', 'KHA': 'kh', 'GA': 'g', 'GHA': 'gh', 'NGA': 'ṅ',
    'CA': 'c', 'CHA': 'ch', 'JA': 'j', 'JHA': 'jh', 'NYA': 'ñ',
    'TTA': 'ṭ', 'TTHA': 'ṭh', 'DDA': 'ḍ', 'DDHA': 'ḍh', 'NNA': 'ṇ',
    'TA': 't', 'THA': 'th', 'DA': 'd', 'DHA': 'dh', 'NA': 'n',
    'PA': 'p', 'PHA': 'ph', 'BA': 'b', 'BHA': 'bh', 'MA': 'm',
    'YA': 'y', 'RA': 'r', 'LA': 'l', 'VA': 'v',
    'SHA': 'ś', 'SSA': 'ṣ', 'SA': 's', 'HA': 'h', 'LLA': 'ḷ',
    'OLD TAMIL LLA': 'ḷ', 'OLD TAMIL LLLA': 'ḻ', 'OLD TAMIL RRA': 'ṟ', 'OLD TAMIL NNNA': 'ṉ',
}

SIGNS = {'CANDRABINDU': 'm̐', 'ANUSVARA': 'ṃ', 'VISARGA': 'ḥ', 'JIHVAMULIYA': 'ẖ', 'UPADHMANIYA': 'ḫ'}

# Brahmi names its virama 'BRAHMI VIRAMA', Modi 'MODI SIGN VIRAMA'
VIRAMAS = {'VIRAMA', 'SIGN VIRAMA', 'SIGN OLD TAMIL VIRAMA'}

PUNCTUATION = {
    'DANDA': '|', 'DOUBLE DANDA': '||',
    'PUNCTUATION DOT': '.', 'PUNCTUATION DOUBLE DOT': ':', 'PUNCTUATION LINE': '|',
}

DIGITS = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE']

# Brahmi also has signs for tens, a hundred and a thousand, written additively; each becomes its value
NUMBERS = {name: str(value) for value, name in enumerate(DIGITS) if value}
NUMBERS.update({'TEN': '10', 'TWENTY': '20', 'THIRTY': '30', 'FORTY': '40', 'FIFTY': '50', 'SIXTY': '60',
                'SEVENTY': '70', 'EIGHTY': '80', 'NINETY': '90', 'ONE HUNDRED': '100', 'ONE THOUSAND': '1000'})


def build_table(script, first, last):
    """Map each character of a Unicode block to (kind, IAST), using its character name."""
    table = {}
    for code in range(first, last + 1):
        name = unicodedata.name(chr(code), '')
        if not name.startswith(script + ' '):
            continue
        part = name[len(script) + 1:]
        if part.startswith('LETTER ') and part[7:] in VOWELS:
            entry = ('vowel', VOWELS[part[7:]])
        elif part.startswith('LETTER ') and part[7:] in CONSONANTS:
            entry = ('consonant', CONSONANTS[part[7:]])
        elif part.startswith('VOWEL SIGN ') and part[11:] in VOWELS:
            entry = ('vowel sign', VOWELS[part[11:]])
        elif part in VIRAMAS:
            entry = ('virama', '')
        elif part.startswith('SIGN ') and part[5:] in SIGNS:
            entry = ('mark', SIGNS[part[5:]])
        elif part in PUNCTUATION:
            entry = ('mark', PUNCTUATION[part])
        elif part.startswith('DIGIT ') and part[6:] in DIGITS:
            entry = ('mark', str(DIGITS.index(part[6:])))
        elif part.startswith('NUMBER ') and part[7:] in NUMBERS:
            entry = ('mark', '[{}]'.format(NUMBERS[part[7:]]))
        elif part == 'NUMBER JOINER':
            entry = ('mark', '')
        else:
            continue
        table[chr(code)] = entry
    return table


BRAHMI = build_table('BRAHMI', 0x11000, 0x1107F)
MODI = build_table('MODI', 0x11600, 0x1165F)


def transliterate(text, table):
    """Transliterate text with one script's table. Characters the table does not know pass through."""
    out = []
    i = 0
    while i < len(text):
        kind, value = table.get(text[i], (None, text[i]))
        if kind == 'consonant':
            following = table.get(text[i + 1], (None, ''))[0] if i + 1 < len(text) else None
            if following == 'vowel sign':
                out.append(value + table[text[i + 1]][1])
                i += 2
                continue
            if following == 'virama':
                out.append(value)
                i += 2
                continue
            out.append(value + 'a')
        elif kind != 'virama':
            out.append(value)
        i += 1
    return ''.join(out)


def brahmi_to_iast(text):
    """Brahmi script to IAST, e.g. '𑀫𑀫 𑀦𑀸𑀫' -> 'mama nāma'."""
    return transliterate(text, BRAHMI)


def modi_to_iast(text):
    """Modi script to IAST, e.g. '𑘦𑘨𑘰𑘙𑘲' -> 'marāṭhī'."""
    return transliterate(text, MODI)
