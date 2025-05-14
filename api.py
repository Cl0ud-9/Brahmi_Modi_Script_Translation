from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
try:
    from indicnlp.transliterate.unicode_transliterate import ItransTransliterator
    from indicnlp.tokenize import indic_tokenize
except ImportError:
    ItransTransliterator = None
    indic_tokenize = None

app = FastAPI()

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str

# === IAST-to-English Setup ===
def check_dependencies():
    """Verify indicnlp is installed."""
    if ItransTransliterator is None or indic_tokenize is None:
        return False
    return True

def load_fallback_lexicon():
    """Fallback lexicon for common terms."""
    return {
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
    }

def load_monier_williams_dictionary():
    """Load Monier-Williams dictionary from wil.txt."""
    dictionary_file = "wil.txt"
    if not os.path.exists(dictionary_file):
        return {}
    dictionary = {}
    try:
        k1_pattern = re.compile(r'<k1>([^<]+)<k2>')
        meaning_pattern = re.compile(r'¦\s*([^<]+)')
        split_pattern = re.compile(r'\.\d+')
        with open(dictionary_file, 'r', encoding='utf-8') as f:
            current_entry_lines = []
            for line in f:
                line = line.strip()
                if line.startswith('<L>'):
                    current_entry_lines = [line]
                elif line == '<LEND>':
                    entry_text = ' '.join(current_entry_lines)
                    k1_match = k1_pattern.search(entry_text)
                    if k1_match:
                        word = k1_match.group(1).lower()
                        meaning_match = meaning_pattern.search(' '.join(current_entry_lines[1:]))
                        if meaning_match:
                            meaning = meaning_match.group(1).strip()
                            meaning_parts = split_pattern.split(meaning)
                            if meaning_parts:
                                meaning = meaning_parts[0].strip()
                                if meaning.startswith('.'):
                                    meaning = meaning[1:].strip()
                                if word and meaning:
                                    dictionary[word] = meaning
                    current_entry_lines = []
                else:
                    current_entry_lines.append(line)
        return dictionary
    except Exception as e:
        return {}

def iast_to_english_translit(text):
    """Transliterate IAST to English phonetics using IndicNLP."""
    if not check_dependencies():
        return text
    try:
        transliterated = ItransTransliterator.to_itrans(text, 'sa')
        transliterated = (transliterated.replace('shh', 'sh')
                                        .replace('Sh', 'Sh')
                                        .replace('R^i', 'Ri')
                                        .replace('~n', 'n')
                                        .replace('~m', 'm')
                                        .replace('.n', 'n')
                                        .replace('.m', 'm'))
        return transliterated
    except Exception:
        return text

def lookup_monier_williams(word, dictionary):
    """Lookup word in Monier-Williams dictionary."""
    word = word.lower().replace('ṃ', 'ṁ').replace('ḥ', '')
    return dictionary.get(word, word)

def post_process_translation(translated_words):
    """Post-process translated words for fluency."""
    result = []
    for i, word in enumerate(translated_words):
        if word.strip() == "":
            result.append(word)
            continue
        if word in ["is", "gives", "see", "desire", "frees"]:
            result.append(word)
        elif word in ["my", "he who", "I"]:
            result.append(word)
        elif word in ["name", "knowledge", "humility", "peace", "field", "liberation", "cycle of rebirth", "dependent origination", "cessation of proliferation", "sun"]:
            if i > 0 and translated_words[i-1] in ["my", "I", "he who"]:
                result.append(word)
            else:
                result.append(f"the {word}")
        else:
            result.append(word)
    return " ".join(result).strip()

# Load dictionary once at startup
MONIER_WILLIAMS_DICT = load_monier_williams_dictionary()

def iast_to_english(text):
    """Convert IAST to English translation."""
    if not text.strip():
        return "Please enter a valid IAST sentence."
    if not check_dependencies():
        raise ValueError("indicnlp library is not installed. Install it using: pip install indicnlp")
    
    fallback_lexicon = load_fallback_lexicon()
    if text in fallback_lexicon:
        return fallback_lexicon[text]

    words = indic_tokenize.trivial_tokenize(text, lang='sa')
    translated_words = []

    for word in words:
        if word.strip() == "":
            translated_words.append(word)
            continue
        if word in fallback_lexicon:
            translated_words.append(fallback_lexicon[word])
            continue
        if MONIER_WILLIAMS_DICT:
            dict_meaning = lookup_monier_williams(word, MONIER_WILLIAMS_DICT)
            if dict_meaning != word:
                translated_words.append(dict_meaning)
                continue
        translated_words.append(iast_to_english_translit(word))

    return post_process_translation(translated_words)

# === Modi-to-IAST Setup ===
independent_vowels = {
    '\U00011600': 'a', '\U00011601': 'ā', '\U00011602': 'i', '\U00011603': 'ī',
    '\U00011604': 'u', '\U00011605': 'ū', '\U00011606': 'ṛ', '\U00011607': 'ṟ',
    '\U00011608': 'ḷ', '\U00011609': 'e', '\U0001160A': 'ai', '\U0001160B': 'o',
    '\U0001160C': 'au'
}

consonants = {
    '\U0001160E': 'ka', '\U0001160F': 'kha', '\U00011610': 'ga', '\U00011611': 'gha', '\U00011612': 'ṅa',
    '\U00011613': 'ca', '\U00011614': 'cha', '\U00011615': 'ja', '\U00011616': 'jha', '\U00011617': 'ña',
    '\U00011618': 'ṭa', '\U00011619': 'ṭha', '\U0001161A': 'ḍa', '\U0001161B': 'ḍha', '\U0001161C': 'ṇa',
    '\U0001161D': 'ta', '\U0001161E': 'tha', '\U0001161F': 'da', '\U00011620': 'dha', '\U00011621': 'na',
    '\U00011622': 'pa', '\U00011623': 'pha', '\U00011624': 'ba', '\U00011625': 'bha', '\U00011626': 'ma',
    '\U00011627': 'ya', '\U00011628': 'ra', '\U00011629': 'la', '\U0001162A': 'va', '\U0001162B': 'śa',
    '\U0001162C': 'ṣa', '\U0001162D': 'sa', '\U0001162E': 'ha', '\U0001162F': 'ḻa', '\U00011630': 'kṣa',
    '\U00011631': 'jña'
}

dependent_vowels = {
    '\U00011632': 'ā', '\U00011633': 'i', '\U00011634': 'ī', '\U00011635': 'u',
    '\U00011636': 'ū', '\U00011637': 'ṛ', '\U00011638': 'ṟ', '\U00011639': 'ḷ',
    '\U0001163A': 'e', '\U0001163B': 'ai', '\U0001163C': 'o', '\U0001163D': 'au'
}

diacritics = {
    '\U0001163E': 'ṃ', '\U0001163F': 'ḥ', '\U00011640': '',  # virāma
    '\U00011641': '’', '\U00011642': '.', '\U00011643': '..',
    '\U00011644': ',', '\U00011645': ';', '\U00011681': '.'  # end-of-sentence
}

digits = {chr(cp): str(i) for i, cp in enumerate(range(0x11650, 0x1165A))}

modi_dictionary = {**independent_vowels, **consonants, **dependent_vowels, **diacritics, **digits}
modi_dictionary['\U00011680'] = '' 

def modi_to_iast(text):
    """Convert Modi script to IAST Latin transliteration."""
    if not text:
        return ""
    try:
        result = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == ' ':
                result.append(' ')
                i += 1
            elif ch in consonants:
                cluster = [consonants[ch][:-1]]  # Base consonant without inherent 'a'
                i += 1
                while i < len(text) and text[i] == '\U00011640' and i + 1 < len(text) and text[i + 1] in consonants:
                    cluster.append(consonants[text[i + 1]][:-1])
                    i += 2
                vowels = []
                diacritics_list = []
                has_virama = False
                while i < len(text) and (text[i] in dependent_vowels or text[i] in diacritics):
                    nxt = text[i]
                    if nxt in dependent_vowels:
                        vowels.append(dependent_vowels[nxt])
                    elif nxt == '\U00011640':
                        has_virama = True
                    elif nxt in diacritics:
                        diacritics_list.append(diacritics[nxt])
                    i += 1
                if has_virama:
                    vowel = ''
                elif vowels:
                    vowel = ''.join(vowels)
                else:
                    vowel = 'a'
                if len(cluster) > 1:
                    result.append(''.join(cluster[:-1]) + cluster[-1] + vowel + ''.join(diacritics_list))
                else:
                    result.append(cluster[0] + vowel + ''.join(diacritics_list))
            elif ch in independent_vowels or ch in digits or ch in diacritics:
                result.append(modi_dictionary.get(ch, ch))
                i += 1
            else:
                if ch not in dependent_vowels:
                    result.append(ch)
                i += 1
        return ''.join(result)
    except Exception as e:
        raise ValueError(f"Error transliterating Modi text: {str(e)}")

def brahmi_to_iast(text):
    """Convert Brahmi script to IAST Latin transliteration."""
    if not text:
        return ""

    # Character mappings for Brahmi to IAST
    vowels = {
        '\U00011005': 'a', '\U00011006': 'ā', '\U00011007': 'i', '\U00011008': 'ī',
        '\U00011009': 'u', '\U0001100A': 'ū', '\U0001100B': 'ṛ', '\U0001100C': 'ṝ',
        '\U0001100D': 'ḷ', '\U0001100E': 'e', '\U0001100F': 'ai', '\U00011010': 'o',
        '\U00011011': 'au'
    }
    consonants = {
        '\U00011013': 'k', '\U00011014': 'kh', '\U00011015': 'g', '\U00011016': 'gh',
        '\U00011017': 'ṅ', '\U00011018': 'c', '\U00011019': 'ch', '\U0001101A': 'j',
        '\U0001101B': 'jh', '\U0001101C': 'ñ', '\U0001101D': 'ṭ', '\U0001101E': 'ṭh',
        '\U0001101F': 'ḍ', '\U00011020': 'ḍh', '\U00011021': 'ṇ', '\U00011022': 't',
        '\U00011023': 'th', '\U00011024': 'd', '\U00011025': 'dh', '\U00011026': 'n',
        '\U00011027': 'p', '\U00011028': 'ph', '\U00011029': 'b', '\U0001102A': 'bh',
        '\U0001102B': 'm', '\U0001102C': 'y', '\U0001102D': 'r', '\U0001102E': 'l',
        '\U0001102F': 'v', '\U00011030': 'ś', '\U00011031': 'ṣ', '\U00011032': 's',
        '\U00011033': 'h'
    }
    vowel_signs = {
        '\U00011038': 'ā', '\U00011039': 'i', '\U0001103A': 'i', '\U0001103B': 'ī',
        '\U0001103C': 'ū', '\U0001103D': 'ū', '\U0001103E': 'ṛ', '\U0001103F': 'ṝ',
        '\U00011040': 'ḷ', '\U00011041': 'e', '\U00011042': 'e', '\U00011043': 'o',
        '\U00011044': 'au'
    }
    diacritics = {
        '\U00011000': 'ṃ', '\U00011001': 'ṃ', '\U00011002': 'ḥ', '\U00011046': ''
    }
    punctuation = {
        '\U0001104B': '॥', '\U0001104C': '।', '\U00011047': '.', '\U00011048': '..'
    }
    numerals = {
        '\U00011066': '0', '\U00011067': '1', '\U00011068': '2', '\U00011069': '3',
        '\U0001106A': '4', '\U0001106B': '5', '\U0001106C': '6', '\U0001106D': '7',
        '\U0001106E': '8', '\U0001106F': '9'
    }
    conjuncts = {
        '\U00011027\U00011046\U0001102D': 'pra',
        '\U00011022\U00011046\U0001102C': 'tya',
        '\U00011022\U00011046\U00011027': 'tp',
        '\U00011018\U00011046\U00011019': 'cch'
    }
    orthographic_corrections = {
        '\U00011044': ('au', 'o'),
        '\U0001103F\U00011046': ('ṝ', 'ṛ'),
        '\U0001100B\U00011046': ('ṛ', 'r')
    }

    all_chars = {**vowels, **consonants, **vowel_signs, **diacritics, **punctuation, **numerals}

    try:
        words = text.split()
        result = []

        for word in words:
            translated_word = ""
            i = 0
            has_final_virama = len(word) >= 2 and word[-1] == '\U00011046'
            word_to_process = word[:-1] if has_final_virama else word

            while i < len(word_to_process):
                if (i + 2 < len(word_to_process) and word_to_process[i:i+3] in conjuncts):
                    translated_word += conjuncts[word_to_process[i:i+3]]
                    i += 3
                    if (i < len(word_to_process) and word_to_process[i] in vowel_signs):
                        vowel = vowel_signs[word_to_process[i]]
                        if word_to_process[i] in orthographic_corrections:
                            incorrect, correct = orthographic_corrections[word_to_process[i]]
                            if vowel == incorrect:
                                vowel = correct
                        translated_word += vowel
                        i += 1
                    continue

                char = word_to_process[i]

                if char in numerals:
                    translated_word += numerals[char]
                    i += 1
                    continue

                if char in punctuation:
                    translated_word += punctuation[char]
                    i += 1
                    continue

                if char in vowels:
                    translated_word += vowels[char]
                    i += 1
                    continue

                if char in ['\U00011000', '\U00011001', '\U00011002']:
                    translated_word += diacritics[char]
                    i += 1
                    continue

                if char in consonants:
                    curr_cons = consonants[char]
                    i += 1
                    if (i < len(word_to_process) and word_to_process[i] == '\U00011046'):
                        i += 1
                        if (i < len(word_to_process) and word_to_process[i] in consonants):
                            next_cons = consonants[word_to_process[i]]
                            if curr_cons == 'c' and next_cons == 'c':
                                translated_word += 'cc'
                            else:
                                translated_word += curr_cons + next_cons
                            i += 1
                            if (i < len(word_to_process) and word_to_process[i] in vowel_signs):
                                vowel = vowel_signs[word_to_process[i]]
                                if word_to_process[i] in orthographic_corrections:
                                    incorrect, correct = orthographic_corrections[word_to_process[i]]
                                    if vowel == incorrect:
                                        vowel = correct
                                translated_word += vowel
                                i += 1
                            elif (i >= len(word_to_process) or word_to_process[i] != '\U00011046'):
                                translated_word += 'a'
                        else:
                            translated_word += curr_cons
                    else:
                        if (i < len(word_to_process) and word_to_process[i] in vowel_signs):
                            vowel = vowel_signs[word_to_process[i]]
                            if word_to_process[i] in orthographic_corrections:
                                incorrect, correct = orthographic_corrections[word_to_process[i]]
                                if vowel == incorrect:
                                    vowel = correct
                            translated_word += curr_cons + vowel
                            i += 1
                        else:
                            translated_word += curr_cons + 'a'
                    continue

                if char in vowel_signs:
                    vowel = vowel_signs[char]
                    if char in orthographic_corrections:
                        incorrect, correct = orthographic_corrections[char]
                        if vowel == incorrect:
                            vowel = correct
                    translated_word += vowel
                    i += 1
                    continue

                if char == '\U00011640':
                    i += 1
                    continue

                if '\U00011000' <= char <= '\U0001107F' and char not in all_chars:
                    raise ValueError(f"Unrecognized Brahmi character: {char} (Unicode: {hex(ord(char))})")

                translated_word += char
                i += 1

            if has_final_virama and translated_word.endswith('a'):
                translated_word = translated_word[:-1]

            result.append(translated_word)

        return ' '.join(result)

    except Exception as e:
        raise ValueError(f"Error transliterating Brahmi text: {str(e)}")

@app.post("/brahmi-to-iast")
async def convert_brahmi(input: TextInput):
    try:
        result = brahmi_to_iast(input.text)
        return {"output": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/iast-to-english")
async def convert_iast(input: TextInput):
    try:
        result = iast_to_english(input.text)
        return {"output": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/modi-to-iast")
async def convert_modi(input: TextInput):
    try:
        result = modi_to_iast(input.text)
        return {"output": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)