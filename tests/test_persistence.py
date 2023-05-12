import sqlalchemy.exc
from pytest import raises
from hypothesis import strategies as st, given


def check_word(name, content, word):
    assert word.name == name
    assert word.content == content


@given(name=st.text(max_size=100), content=st.text(max_size=300))
def test_new_word(name, content, db_factory):
    db = db_factory()
    db.new_word(name, content)
    word = db._get_word(name)
    check_word(name, content, word)


def test_delete_word():
    raise AssertionError()


def test_get_words_filtered():
    raise AssertionError()


@given(
    names=st.lists(st.text(min_size=1, max_size=100), unique=True, min_size=2, max_size=2),
    content=st.text(max_size=300),
)
def test__rename_word(names, content, db_factory):
    name, new_name = names
    db = db_factory()
    db.new_word(name, content)
    check_word(name, content, db._get_word(name))
    db._rename_word(name, new_name)
    check_word(new_name, content, db._get_word(new_name))
    with raises(sqlalchemy.exc.NoResultFound):
        check_word(name, content, db._get_word(name))


def test__update_word():
    raise AssertionError()


def test__get_word():
    raise AssertionError()


def test__get_session():
    raise AssertionError()


def test__create_dbs():
    raise AssertionError()
