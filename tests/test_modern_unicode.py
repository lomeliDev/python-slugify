"""Modern algorithm up-front argument type validation.

The modern algorithm validates caller-supplied arguments at the top of
``_modern_slugify`` so a misuse fails with a clear, argument-specific message
instead of a cryptic error raised deep in the pipeline. These tests cover the
``regex_pattern`` argument alongside the existing ``max_length``/``separator``
guards.
"""
import re

import pytest

from slugify import slugify


def test_regex_pattern_type_is_validated_up_front():
    with pytest.raises(TypeError, match='regex_pattern'):
        slugify('abc', algorithm='modern', regex_pattern=123)


def test_regex_pattern_accepts_str_and_compiled_pattern():
    assert slugify('a b', algorithm='modern', regex_pattern=r'[^-a-z]+') == 'a-b'
    assert slugify('a b', algorithm='modern', regex_pattern=re.compile(r'[^-a-z]+')) == 'a-b'
