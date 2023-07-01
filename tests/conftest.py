import os
from typing import TYPE_CHECKING

from pytest import fixture
from sqlalchemy import create_engine

if TYPE_CHECKING:
    from wordspreader.main import WordSpreader
    from wordspreader.persistence import DBPersistence

ENGINE_ECHO = True if not os.environ.get("ECHO_OFF", False) else False


@fixture(scope="session")
def db_factory():
    from wordspreader.ddl import Base
    from wordspreader.persistence import DBPersistence

    engine = create_engine("sqlite:///:memory:", echo=ENGINE_ECHO)

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
