from typing import TYPE_CHECKING

from pytest import fixture
from sqlalchemy import create_engine, Table

if TYPE_CHECKING:
    from wordspreader.main import WordSpreader
    from wordspreader.persistence import DBPersistence


@fixture(scope="function")
def db():
    from wordspreader.persistence import DBPersistence

    yield DBPersistence(create_engine("sqlite:///:memory:", echo=True))


@fixture(scope="session")
def db_factory():
    from wordspreader.persistence import DBPersistence, Base

    engine = create_engine("sqlite:///:memory:", echo=True)

    one_db_lol = DBPersistence(engine)

    def clean():
        # noinspection PyProtectedMember
        with one_db_lol._get_session() as session:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()

        # Base.metadata.drop_all(engine)
        # Base.metadata.create_all(engine)

    def factory() -> "DBPersistence":
        clean()
        return one_db_lol

    return factory


@fixture(scope="session")
def app_factory(db_factory):
    def factory() -> "WordSpreader":
        from wordspreader.main import WordSpreader

        return WordSpreader(db_factory())

    return factory
