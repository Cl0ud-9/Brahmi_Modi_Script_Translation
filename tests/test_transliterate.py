import unicodedata

import pytest

from brahmi_modi.transliterate import BRAHMI, MODI, brahmi_to_iast, modi_to_iast


@pytest.mark.parametrize('brahmi, iast', [
    ('𑀫𑀫 𑀦𑀸𑀫', 'mama nāma'),
    ('𑀤𑁂𑀯𑀸𑀦𑀁𑀧𑀺𑀬𑁂𑀦 𑀧𑀺𑀬𑀤𑀲𑀺𑀦', 'devānaṃpiyena piyadasina'),
    ('𑀮𑀸𑀚𑀺𑀦𑀯𑀻𑀲𑀢𑀺𑀯𑀲𑀸𑀪𑀺𑀲𑀺𑀢𑁂𑀦', 'lājinavīsativasābhisitena'),
    ('𑀲𑀓𑁆𑀬𑀫𑀼𑀦𑀺𑀢𑀺', 'sakyamuniti'),
    ('𑀧𑁆𑀭𑀢𑀻𑀢𑁆𑀬', 'pratītya'),
    ('𑀥𑀫𑁆𑀫', 'dhamma'),
    ('𑀅𑀳𑀁', 'ahaṃ'),
    ('𑁧𑁨𑁩', '123'),
    ('𑀏𑀐𑀑𑀒', 'eaioau'),
    ('𑀓𑁂 𑀓𑁃 𑀓𑁄 𑀓𑁅', 'ke kai ko kau'),
    ('𑀥𑀁𑀫𑀮𑀺𑀧𑀻𑁇', 'dhaṃmalipī|'),
    ('𑁗', '[6]'),
])
def test_brahmi(brahmi, iast):
    assert brahmi_to_iast(brahmi) == iast


@pytest.mark.parametrize('modi, iast', [
    ('𑘦𑘻𑘟𑘲', 'modī'),
    ('𑘦𑘨𑘰𑘙𑘲', 'marāṭhī'),
    ('𑘨𑘽𑘦𑘲', 'raṃmī'),
    ('𑘎𑘿𑘬', 'kṣa'),
    ('𑘁𑘝𑘿𑘦𑘨𑘳𑘢', 'ātmarupa'),
    ('𑙑𑙒', '12'),
    ('𑘊𑘋𑘌𑘍', 'eaioau'),
])
def test_modi(modi, iast):
    assert modi_to_iast(modi) == iast


@pytest.mark.parametrize('table, script', [(BRAHMI, 'BRAHMI'), (MODI, 'MODI')])
def test_every_letter_and_sign_is_mapped(table, script):
    first = 0x11000 if script == 'BRAHMI' else 0x11600
    for code in range(first, first + 0x80):
        name = unicodedata.name(chr(code), '')
        if ' LETTER ' in name or ' VOWEL SIGN ' in name or ' DIGIT ' in name:
            assert chr(code) in table, name


@pytest.mark.parametrize('table, script', [(BRAHMI, 'BRAHMI'), (MODI, 'MODI')])
def test_table_follows_the_unicode_names(table, script):
    # The sign names end in the sound: 'MODI VOWEL SIGN II' is ī, 'BRAHMI LETTER KHA' is kh
    spot_checks = {'LETTER KA': 'k', 'LETTER KHA': 'kh', 'LETTER SHA': 'ś', 'LETTER SSA': 'ṣ', 'LETTER NYA': 'ñ',
                   'VOWEL SIGN AA': 'ā', 'VOWEL SIGN II': 'ī', 'VOWEL SIGN U': 'u', 'VOWEL SIGN O': 'o',
                   'LETTER AU': 'au', 'SIGN ANUSVARA': 'ṃ', 'SIGN VISARGA': 'ḥ'}
    for suffix, iast in spot_checks.items():
        assert table[unicodedata.lookup(f'{script} {suffix}')][1] == iast


def test_virama_removes_the_inherent_vowel_and_unknown_text_passes_through():
    assert brahmi_to_iast('𑀓𑁆') == 'k'
    assert brahmi_to_iast('abc 𑀓') == 'abc ka'
    assert modi_to_iast('') == ''
