from pytest import fixture
from sqlalchemy import create_engine


@fixture(scope='function')
def db():
    from wordspreader.persistence import DBPersistence

    yield DBPersistence(create_engine('sqlite:///:memory:'))


@fixture(scope='session')
def db_factory():
    def factory():
        from wordspreader.persistence import DBPersistence

        return DBPersistence(create_engine('sqlite:///:memory:'))

    return factory


@fixture(scope='session')
def app_factory(db_factory):
    def factory():
        from wordspreader.main import WordSpreader

        return WordSpreader(db_factory())

    return factory
