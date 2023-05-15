from typing import TYPE_CHECKING

from hypothesis import given
from hypothesis import strategies as st
from pytest import mark
from pytest import raises

from wordspreader.persistence import Tag, Word

if TYPE_CHECKING:
    from wordspreader.persistence import DBPersistence

st_name = st.text(max_size=100, min_size=2)
st_content = st.text(max_size=300)
st_tag = st.text(max_size=20, min_size=2)
st_tags = st.sets(st_tag, max_size=10)
st_name_list = st.lists(st_name, min_size=2, max_size=2, unique=True)
st_content_list = st.lists(st_content, min_size=2, max_size=2, unique=True)
st_built_tag = st.builds(Tag, name=st_tag)
st_build_tags = st.sets(st_built_tag, max_size=10)
st_word = st.builds(Word, name=st_name, content=st_content, tags=st_build_tags)


def check_word(name: str, content: str, tags: set[str], word: "Word"):
    assert word.name == name
    assert word.content == content
    assert isinstance(tags, set)
    assert all(isinstance(i, str) for i in tags)
    assert tags == word.tags


# noinspection PyProtectedMember
def make_get_check(name: str, content: str, tags: set[str], db: "DBPersistence") -> Word:
    db.new_word(name, content, tags)
    word = db.get_word(name)
    check_word(name, content, tags, word)
    return word


@given(name=st_name, content=st_content, tags=st_tags)
def test_get_word(name: str, content: str, tags: set[str], db_factory: callable):
    from wordspreader.persistence import Word

    db: "DBPersistence" = db_factory()
    with db._get_session() as session:
        word = Word(name=name, content=content, tags=tags)
        session.add(word)
        session.commit()
    check_word(name, content, tags, db.get_word(name))


@given(name=st_name, content=st_content, tags=st_tags)
def test_new_word(name: str, content: str, tags: set[str], db_factory: callable):
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)


@given(name=st_name, content=st_content, tags=st_tags)
def test_delete_word(name: str, content: str, tags: set[str], db_factory: callable):
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)
    db.delete_word(name)

    assert db.get_word(name) is None


@given(names=st_name_list, content=st_content, tags=st_tags)
def test__rename_word(names: list[str, str], content: str, tags: set[str], db_factory: callable):
    from wordspreader.persistence import DuplicateKeyException

    name, new_name = names
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)
    with raises(DuplicateKeyException):
        # Make sure we still raise a duplicate key if we try and rename to an already used name
        db._rename_word(name, name)
    db._rename_word(name, new_name)
    check_word(new_name, content, tags, db.get_word(new_name))
    assert db.get_word(name) is None


@given(name=st_name, contents=st_content_list, tags=st_tags)
def test__update_word(name: str, contents: list[str], tags: set[str], db_factory):
    content, new_content = contents
    db: "DBPersistence" = db_factory()
    make_get_check(name, content, tags, db)
    db._update_word(name=name, content=new_content)
    check_word(name, new_content, tags, db.get_word(name))


@given(
    names=st_name_list,
    contents=st_content_list,
    tags=st.lists(st.sets(st_tag, min_size=4, max_size=5), min_size=2, max_size=2),
)
def test__get_words_filtered(names: list[str], contents: list[str], tags: list[set[str]], db_factory):
    db: "DBPersistence" = db_factory()

    # Split up input
    name1, name2 = names
    content1, content2 = contents
    tag1, tag2 = tags
    # Word 1
    word1 = make_get_check(name1, content1, tag1, db)
    word1_list = list(db.get_words_filtered(tag1))
    assert len(word1_list) == 1
    word1_by_tag = word1_list[0]
    assert word1 == word1_by_tag
    # Word 2
    word2 = make_get_check(name2, content2, tag2, db)
    word2_list = list(db.get_words_filtered(tag2))
    assert len(word2_list) == 1
    word2_by_tag = word2_list[0]
    assert word2 == word2_by_tag
