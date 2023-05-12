from typing import TYPE_CHECKING

import sqlalchemy.exc
from hypothesis import strategies as st, given
from pytest import raises, mark

if TYPE_CHECKING:
    from wordspreader.persistence import DBPersistence, Word


def check_word(name: str, content: str, word: "Word"):
    assert word.name == name
    assert word.content == content


# noinspection PyProtectedMember
def make_get_check(name: str, content: str, db: "DBPersistence"):
    db.new_word(name, content)
    word = db.get_word(name)
    check_word(name, content, word)


@given(name=st.text(max_size=100), content=st.text(max_size=300))
def test_new_word_and_get_word(name: str, content: str, db_factory: callable):
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, db)


@given(name=st.text(max_size=100), content=st.text(max_size=300))
def test_delete_word(name: str, content: str, db_factory: callable):
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, db)
    db.delete_word(name)
    with raises(sqlalchemy.exc.NoResultFound):
        db.get_word(name)


@mark.skip(reason='Not using tags yet')
def test_get_words_filtered():
    raise AssertionError()


@given(
    names=st.lists(st.text(min_size=1, max_size=100), unique=True, min_size=2, max_size=2),
    content=st.text(max_size=300),
)
def test__rename_word(names: list[str, str], content: str, db_factory: callable):
    name, new_name = names
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, db)
    db._rename_word(name, new_name)
    check_word(new_name, content, db.get_word(new_name))
    with raises(sqlalchemy.exc.NoResultFound):
        check_word(name, content, db.get_word(name))


@given(
    name=st.text(max_size=100, min_size=1),
    contents=st.lists(st.text(min_size=1, max_size=300), unique=True, min_size=2, max_size=2),
)
def test__update_word(name, contents, db_factory):
    content, new_content = contents
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, db)
    db._update_word(name=name, content=new_content)
    check_word(name, new_content, db.get_word(name))
