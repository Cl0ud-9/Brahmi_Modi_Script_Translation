import os

import pytest

from brahmi_modi.translate import DICTIONARY_PATH, candidates, first_gloss, iast_to_english, load_dictionary, lookup

SAMPLE = """<L>1<pc>421<k1>deva<k2>deva
{#deva#}¦ ({#f#}) {#dezwa#} r. 1st cl. ({#devate#}) To sport or play.
<LEND>
<L>2<pc>421<k1>deva<k2>deva
{#deva#}¦ m. ({#-vaH#})
.²1 A deity, a god.
.²2 A king, in poetical language.
<LEND>
<L>3<pc>006<k1>agni<k2>agni
{#agni#}¦ m. ({#-gniH#})
.²1 Fire, always associated with the idea of the deity presiding over it.
<LEND>
<L>4<pc>001<k1>sUryya<k2>sUryya
{#sUryya#}¦ m. ({#-ryyaH#}) The sun.
<LEND>
"""


@pytest.fixture
def dictionary(tmp_path):
    path = tmp_path / 'wil.txt'
    path.write_text(SAMPLE, encoding='utf-8')
    return load_dictionary.__wrapped__(str(path))


def test_noun_senses_come_before_verbal_roots(dictionary):
    assert dictionary['deva'] == ['A deity, a god', 'To sport or play']


def test_long_glosses_keep_whole_senses():
    assert first_gloss('m. .²1 Fire, always associated with the idea of the deity presiding over it.') == 'Fire'


def test_inflected_words_and_wilson_spellings_are_found(dictionary):
    # sūryaḥ: nominative ending dropped, and Wilson doubles a consonant after r (sUryya)
    assert lookup('sūryaḥ', {}) == 'sun'
    assert lookup('sūrya', dictionary) == 'The sun'
    assert 'sUryya' in candidates('sūrya')


def test_lexicon_words_and_sentences():
    assert iast_to_english('mama nāma') == 'my name'
    assert iast_to_english('aham paśyāmi sūryaḥ') == 'I see the sun'
    assert iast_to_english('kṣetrajñaḥ') == 'knower of the field'


def test_empty_input_is_an_error():
    with pytest.raises(ValueError):
        iast_to_english('   ')


@pytest.mark.skipif(not os.path.exists(DICTIONARY_PATH), reason='run scripts/download_dictionary.py first')
def test_real_dictionary():
    assert len(load_dictionary()) > 40000
    assert lookup('deva') == 'A deity, a god'
    assert lookup('dharma') == 'Virtue, moral and religious merit'
    assert iast_to_english('agni jala') == 'Fire Water'
