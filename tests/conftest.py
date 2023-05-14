from typing import TYPE_CHECKING

from pytest import fixture
from sqlalchemy import create_engine

if TYPE_CHECKING:
    from wordspreader.main import WordSpreader
    from wordspreader.persistence import DBPersistence


@fixture(scope="function")
def db():
    from wordspreader.persistence import DBPersistence

    yield DBPersistence(create_engine("sqlite:///:memory:", echo=True))


@fixture(scope="session")
def db_factory():
    def factory() -> "DBPersistence":
        from wordspreader.persistence import DBPersistence

        return DBPersistence(create_engine("sqlite:///:memory:", echo=True))

    return factory


@fixture(scope="session")
def app_factory(db_factory):
    def factory() -> "WordSpreader":
        from wordspreader.main import WordSpreader

        return WordSpreader(db_factory())

    return factory
