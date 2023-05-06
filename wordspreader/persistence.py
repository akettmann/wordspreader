from __future__ import annotations
from typing import List

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from sqlalchemy import String, ForeignKey, Column, Table, create_engine, select


class DuplicateKeyException(BaseException):
    pass


class Base(DeclarativeBase):
    pass


association_table = Table(
    "word_to_tag",
    Base.metadata,
    Column("word_name", ForeignKey("word.name")),
    Column("tag_id", ForeignKey("tag.id")),
)


class Word(Base):
    __tablename__ = 'word'
    name: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(String(2000), primary_key=True, unique=True)
    tags: Mapped[List[Tag]] = relationship(secondary=association_table)


class Tag(Base):
    __tablename__ = 'tag'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class DBPersistence:
    def __init__(self):
        self.engine = create_engine('sqlite:///dumb-example-db.sqlite3')

    async def new_word(self, name: str, content: str, tags: list[Tag] = None):
        word = Word(name=name, content=content, tags=tags or [])
        with await self._get_session() as session:
            session.add(word)
            session.commit()

    async def update_word(self, name: str, content: str = None, tags: list[Tag] = None, new_name: str = None):
        """Update the word with the content, tags, new name, or all three"""
        # This first, less likely to fail
        await self._update_word(name, content, tags)
        if new_name:
            # Might fail due to duplicate key
            await self._rename_word(name, new_name)

    async def _rename_word(self, old_name: str, new_name: str):
        """Changes the primary key"""
        with await self._get_session() as session:
            maybe_new_word = session.execute(select(Word).where(Word.name == new_name)).scalar_one_or_none()
            if maybe_new_word:
                raise DuplicateKeyException(f'New name: `{new_name}` is already taken, pick another name"')
            word = session.execute(select(Word).where(Word.name == old_name)).scalar_one()
            word.name = new_name
            session.add(word)
            session.commit()

    async def _update_word(self, name: str, content: str = None, tags: list[Tag] = None):
        """Doesn't change primary key, just content and/or tags"""
        with await self._get_session() as session:
            word = await self._get_word(name)
            word.content = content or word.content
            word.tags = tags or word.tags
            session.add(word)
            session.commit()

    async def _get_word(self, name: str) -> Word:
        with await self._get_session() as session:
            return session.execute(select(Word).where(Word.name == name)).scalar_one()

    async def _get_session(self) -> Session:
        return Session(self.engine)

    async def _create_dbs(self):
        Base.metadata.create_all(self.engine)
