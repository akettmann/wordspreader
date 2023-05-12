from typing import TYPE_CHECKING

from pytest import fixture
from sqlalchemy import create_engine

if TYPE_CHECKING:
    from wordspreader.persistence import DBPersistence
    from wordspreader.main import WordSpreader


@fixture(scope='function')
def db():
    from wordspreader.persistence import DBPersistence

    yield DBPersistence(create_engine('sqlite:///:memory:'))


@fixture(scope='session')
def db_factory():
    def factory() -> "DBPersistence":
        from wordspreader.persistence import DBPersistence

        return DBPersistence(create_engine('sqlite:///:memory:'))

    return factory


@fixture(scope='session')
def app_factory(db_factory):
    def factory() -> "WordSpreader":
        from wordspreader.main import WordSpreader

        return WordSpreader(db_factory())

    return factory
