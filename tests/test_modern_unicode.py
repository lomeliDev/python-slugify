"""Modern apostrophe-family contracts: U+2018/U+2019/U+02BC slug like ASCII "'" (#3)."""
import importlib
import unittest
from functools import partial
from unittest.mock import patch

from slugify import slugify as public_slugify

slugify = partial(public_slugify, algorithm='modern')
core = importlib.import_module('slugify.slugify')

# ASCII "'" is the reference member; every other member must slug exactly like it.
APOSTROPHE_FAMILY = ("'", '\u02bc', '\u2018', '\u2019')
BACKENDS = ('auto', 'text-unidecode', 'unidecode', 'anyascii')
# Quote-like characters deliberately left outside the family: unchanged, and equal to legacy.
OUTSIDE_FAMILY = ('don\u201bt', 'don\u2032t', 'don\uff07t', 'don\u02b9t', 'don\u05f3t')


def _backend_missing(backend):
    names = ('unidecode', 'text_unidecode') if backend == 'auto' else (backend.replace('-', '_'),)
    for name in names:
        try:
            importlib.import_module(name)
        except ModuleNotFoundError:
            continue
        return False
    return True


class ModernApostropheFamilyTests(unittest.TestCase):
    def test_typographic_apostrophe_matches_ascii(self):
        base = slugify("don't")
        self.assertEqual(base, 'don-t')
        for apostrophe in APOSTROPHE_FAMILY:
            for allow_unicode in (False, True):
                with self.subTest(apostrophe=apostrophe, allow_unicode=allow_unicode):
                    self.assertEqual(slugify(f'don{apostrophe}t', allow_unicode=allow_unicode), base)
        self.assertEqual(slugify('Baby\u2019s shoes'), slugify("Baby's shoes"))
        self.assertEqual(slugify('Baby\u2019s shoes'), 'baby-s-shoes')
        # Modern decodes entities first, so an encoded apostrophe is a family member too.
        self.assertEqual(slugify('a &rsquo; b'), slugify('a \u2019 b'))
        self.assertEqual(slugify('a &rsquo; b'), 'a-b')

    def test_apostrophe_family_matches_ascii_across_backends(self):
        for backend in BACKENDS:
            with self.subTest(backend=backend):
                if _backend_missing(backend):
                    self.skipTest(f'{backend} backend absent')
                base = slugify("don't", backend=backend)
                for apostrophe in APOSTROPHE_FAMILY:
                    self.assertEqual(slugify(f'don{apostrophe}t', backend=backend), base)

    def test_apostrophe_runs_collapse_to_a_single_separator(self):
        for run in ("''", '\u2019\u2019', "'\u2019", '\u2018\u02bc'):
            with self.subTest(run=run):
                self.assertEqual(slugify(f'don{run}t'), slugify("don''t"))
                self.assertEqual(slugify(f'don{run}t'), 'don-t')
        self.assertEqual(slugify('\u2019\u2018'), '')

    def test_apostrophe_family_follows_ascii_through_options(self):
        option_sets = (
            dict(separator='_'),
            dict(max_length=5, word_boundary=True),
            dict(max_length=5, word_boundary=True, save_order=True),
            dict(stopwords=['t']),
            dict(lowercase=False),
            dict(regex_pattern=r'[^-a-z0-9_]+'),
            dict(allow_unicode=True),
            dict(replacements=[('stop', 'wait')], replacement_stage='pre'),
        )
        for options in option_sets:
            with self.subTest(options=options):
                expected = slugify("don't stop", **options)
                for apostrophe in APOSTROPHE_FAMILY:
                    self.assertEqual(slugify(f'don{apostrophe}t stop', **options), expected)

    def test_apostrophe_family_is_resolved_before_transliteration(self):
        # The family becomes a separator up front, so no backend table is consulted for it.
        with patch.object(core, 'import_module', side_effect=AssertionError('must not import')):
            for apostrophe in APOSTROPHE_FAMILY:
                with self.subTest(apostrophe=apostrophe):
                    self.assertEqual(slugify(f'don{apostrophe}t'), 'don-t')
        # Text that stays non-ASCII still reaches the backend; nothing is silently skipped.
        self.assertEqual(slugify('caf\u00e9', backend='text-unidecode'), 'cafe')

    def test_backend_generated_quotes_are_still_removed(self):
        # Upstream #17/#23: a quote the backend generates is deleted, never made a separator.
        # U+044C transliterates to an ASCII apostrophe; text-unidecode is the base dependency.
        for text, expected in (('\u0406\u0432\u0430\u043d\u044c\u043a\u043e', 'ivanko'),
                               ('\u041a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440', 'kompiuter')):
            with self.subTest(text=text):
                self.assertEqual(slugify(text, backend='text-unidecode'), expected)
                self.assertEqual(slugify(text), public_slugify(text))
                self.assertNotIn('-', slugify(text))

    def test_legacy_apostrophe_output_is_frozen(self):
        self.assertEqual(public_slugify("don't"), 'don-t')
        for apostrophe in APOSTROPHE_FAMILY[1:]:
            with self.subTest(apostrophe=apostrophe):
                self.assertEqual(public_slugify(f'don{apostrophe}t'), 'dont')
                self.assertEqual(public_slugify(f'don{apostrophe}t', algorithm='legacy'), 'dont')

    def test_quote_like_characters_outside_the_family_are_unchanged(self):
        for text in OUTSIDE_FAMILY:
            with self.subTest(text=text):
                self.assertEqual(slugify(text), public_slugify(text))


if __name__ == '__main__':
    unittest.main()
