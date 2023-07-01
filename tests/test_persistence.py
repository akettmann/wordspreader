from typing import TYPE_CHECKING

from hypothesis import given
from hypothesis import strategies as st
from pytest import mark, raises

from wordspreader.ddl import Tag, Word

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
def test_make_get_new_word(name: str, content: str, tags: set[str], db_factory: callable):
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
    from wordspreader.ddl import DuplicateKeyException

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
    tags=st.lists(st_tag, min_size=4, max_size=10, unique=True),
)
def test__get_words_filtered(names: list[str], contents: list[str], tags: list[str], db_factory):
    db: "DBPersistence" = db_factory()

    def get_by_tag_and_check(my_tag: str, word: Word):
        word_list = list(db.get_words_filtered(my_tag))
        assert len(word_list) == 1
        fetched_word = word_list[0]
        assert word == fetched_word

    # Split up input
    name1, name2 = names
    content1, content2 = contents
    tags1 = set(tags[:4])
    tags2 = set(tags[4:])
    # Word 1
    word1 = make_get_check(name1, content1, tags1, db)
    for tag in word1.tags:
        assert tag in tags1
        assert tag not in tags2
        get_by_tag_and_check(tag, word1)
    # Word 2
    word2 = make_get_check(name2, content2, tags2, db)
    for tag in word2.tags:
        assert tag in tags2
        assert tag not in tags1
        get_by_tag_and_check(tag, word2)


def test__add_two_words_with_the_same_tag(db_factory):
    db: "DBPersistence" = db_factory()
    make_get_check("word1", "", {"thing", "stuff"}, db)
    make_get_check("word2", "", {"thing", "stuff"}, db)


@mark.skip("This is why we need to use the `wordspreader.persistence.DBPersistence.resolve_tags`")
def test__add_two_words_with_the_same_tag_2(db_factory):
    from wordspreader.ddl import Word

    db: "DBPersistence" = db_factory()
    words = Word(name="potato", content="", tags={})
    words.tags.add("test")
    words.tags.add("test2")
    words2 = Word(name="potato2", content="", tags={})
    words2.tags.add("test3")
    words2.tags.add("test2")
    with db._get_session() as session:
        session.add_all([words, words2])
        session.commit()


def test__orphans_are_cleaned_up(db_factory):
    db: "DBPersistence" = db_factory()
    word1 = make_get_check("word1", "", {"thing", "stuff"}, db)
    assert len(list(db.get_all_tags())) == 2, "Tags should exist still"
    db.update_word(word1.name, tags=set())
    assert len(list(db.get_all_tags())) == 0, "Tags should be cleaned up now"


def test__orphans_are_cleaned_up_when_word_deleted(db_factory):
    db: "DBPersistence" = db_factory()
    word1 = make_get_check("word1", "", {"thing", "stuff"}, db)
    assert len(list(db.get_all_tags())) == 2, "Tags should exist still"
    db.delete_word(word1.name)
    assert len(list(db.get_all_tags())) == 0, "Tags should be cleaned up now"
