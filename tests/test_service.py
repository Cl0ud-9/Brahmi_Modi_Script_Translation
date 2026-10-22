import io

import pytest
from PIL import Image

from brahmi_modi import service


def test_convert_each_script():
    assert service.convert('brahmi', '𑀫𑀫 𑀦𑀸𑀫') == 'mama nāma'
    assert service.convert('iast', 'mama nāma') == 'my name'


@pytest.mark.parametrize('script, text, status', [('iast', ' ', 400), ('brahmi', 'x' * 5001, 422), ('greek', 'a', 400)])
def test_bad_input_says_why(script, text, status):
    with pytest.raises(service.InputError) as caught:
        service.convert(script, text)
    assert caught.value.status == status
    assert str(caught.value)


def test_reading_something_that_is_not_an_image():
    with pytest.raises(service.InputError, match='not an image'):
        service.read_brahmi(b'hello')


def test_a_blank_image_reads_as_nothing():
    blank = io.BytesIO()
    Image.new('L', (256, 64), 255).save(blank, 'PNG')
    assert service.read_brahmi(blank.getvalue()) == {'brahmi': '', 'iast': ''}
