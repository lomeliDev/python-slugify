from slugify import slugify


def test_combining_mark_does_not_split_word() -> None:
    output = slugify('İstanbul', allow_unicode=True, algorithm='modern')

    assert '-' not in output
    assert output.endswith('stanbul')
