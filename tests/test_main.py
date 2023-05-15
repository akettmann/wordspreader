from typing import TYPE_CHECKING

from hypothesis import given
from hypothesis import strategies as st
from pytest import fixture, skip


if TYPE_CHECKING:
    from wordspreader.main import WordSpreader
    from wordspreader.persistence import Word
skip("Can't handle the flet yet", allow_module_level=True)


@fixture(scope="session", autouse=True)
def hide_flet_for_unittests():
    pass


def check_word(name: str, content: str, word: "Word"):
    assert word.name == name
    assert word.content == content


def make_get_check(name: str, content: str, app: "WordSpreader"):
    app.new_title.value = name
    app.new_words.value = content
    app.add_clicked(None)
    word = app.db.get_word(name)
    check_word(name, content, word)


@given(name=st.text(max_size=100), content=st.text(max_size=300))
def test_add_and_get(name, content, app_factory):
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from wordspreader.main import WordSpreader
    app = app_factory()
    app: "WordSpreader"
    make_get_check(name, content, app)
