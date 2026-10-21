"""Brahmi and Modi script transliteration, IAST to English glossing, and Brahmi text recognition."""
from .translate import iast_to_english
from .transliterate import brahmi_to_iast, modi_to_iast

__all__ = ['brahmi_to_iast', 'modi_to_iast', 'iast_to_english']
__version__ = '1.1.1'
