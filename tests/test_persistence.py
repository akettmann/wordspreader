from typing import TYPE_CHECKING

from hypothesis import given
from hypothesis import strategies as st
from pytest import mark, raises

if TYPE_CHECKING:
    from wordspreader.persistence import DBPersistence, Word

st_name = st.text(max_size=100, min_size=2)
st_content = st.text(max_size=300)
st_tag = st.text(max_size=20, min_size=2)
st_tags = st.lists(st_tag, max_size=10, unique=True)
st_name_list = st.lists(st_name, min_size=2, max_size=2, unique=True)
st_content_list = st.lists(st_content, min_size=2, max_size=2, unique=True)


def check_word(name: str, content: str, tags: list[str], word: "Word"):
    assert word.name == name
    assert word.content == content
    assert set(t for t in tags) == set(t.name for t in word.tags)


# noinspection PyProtectedMember
def make_get_check(name: str, content: str, tags: list[str], db: "DBPersistence"):
    db.new_word(name, content, tags)
    word = db.get_word(name)
    check_word(name, content, tags, word)


@given(name=st_name, content=st_content, tags=st_tags)
def test_new_word_and_get_word(name: str, content: str, tags: list[str], db_factory: callable):
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)


@given(name=st_name, content=st_content, tags=st_tags)
def test_delete_word(name: str, content: str, tags: list[str], db_factory: callable):
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)
    db.delete_word(name)

    assert db.get_word(name) is None


@mark.skip(reason="Not using tags yet")
def test_get_words_filtered():
    raise AssertionError()


@given(names=st_name_list, content=st_content, tags=st_tags)
def test__rename_word(names: list[str, str], content: str, tags: list[str], db_factory: callable):
    name, new_name = names
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)
    db._rename_word(name, new_name)
    check_word(new_name, content, tags, db.get_word(new_name))
    assert db.get_word(name) is None


@given(name=st_name, content=st_content, tags=st_tags)
def test__rename_word_already_exists(name: str, content: str, tags: list[str], db_factory: callable):
    from wordspreader.persistence import DuplicateKeyException

    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)
    with raises(DuplicateKeyException):
        db._rename_word(name, name)


@given(name=st_name, contents=st_content_list, tags=st_tags)
def test__update_word(name: str, contents: list[str], tags: list[str], db_factory):
    content, new_content = contents
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)
    db._update_word(name=name, content=new_content)
    check_word(name, new_content, tags, db.get_word(name))
