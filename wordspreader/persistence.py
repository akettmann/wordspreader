from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import Column, ForeignKey, String, Table, create_engine, delete, select, Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class DuplicateKeyException(BaseException):
    pass


class Base(DeclarativeBase):
    pass


association_table = Table(
    "word_to_tag",
    Base.metadata,
    Column("word_name", ForeignKey("word.name")),
    Column("tag_name", ForeignKey("tag.name")),
)


class Word(Base):
    __tablename__ = "word"
    name: Mapped[str] = mapped_column(String(100), primary_key=True, unique=True)
    content: Mapped[str] = mapped_column(String(2000))
    tags: Mapped[list[Tag]] = relationship(secondary=association_table)


class Tag(Base):
    __tablename__ = "tag"
    name: Mapped[str] = mapped_column(String(100), primary_key=True)


class DBPersistence:
    def __init__(self, engine: Engine):
        self.engine = engine
        Base.metadata.create_all(self.engine)

    @classmethod
    def from_file(cls, db_file: Path):
        return cls(create_engine(f"sqlite:///{db_file.resolve().absolute()}"))

    def new_word(self, name: str, content: str, tags: list[Tag] = None):
        word = Word(name=name, content=content, tags=tags or [])
        with self._get_session() as session:
            session.add(word)
            session.commit()

    def update_word(self, name: str, content: str = None, tags: list[Tag] = None, new_name: str = None):
        """Update the word with the content, tags, new name, or all three"""
        # This first, less likely to fail
        # specifically tags is not None, because setting the list of tags to `[]` is legal
        # and a change (remove all tags from object)
        # Also content is not allowed to be null
        if content is not None or tags is not None:
            self._update_word(name, content, tags)
        if new_name:
            # Might fail due to duplicate key
            self._rename_word(name, new_name)

    def delete_word(self, name: str):
        with self._get_session() as session:
            session.execute(delete(Word).where(Word.name == name))
            session.commit()

    def get_words_filtered(self, category: str = None) -> Iterator[Word]:
        query = select(Word)
        if category is not None:
            query.where(Word.tags.contains(category))

        with self._get_session() as session:
            yield from session.scalars(query)

    def _rename_word(self, old_name: str, new_name: str):
        """Changes the primary key"""
        with self._get_session() as session:
            maybe_new_word = session.execute(select(Word).where(Word.name == new_name)).scalar_one_or_none()
            if maybe_new_word:
                msg = f'New name: `{new_name}` is already taken, pick another name"'
                raise DuplicateKeyException(msg)
            word = session.execute(select(Word).where(Word.name == old_name)).scalar_one()
            word.name = new_name
            session.add(word)
            session.commit()

    def _update_word(self, name: str, content: str = None, tags: list[Tag] = None):
        """Doesn't change primary key, just content and/or tags"""
        with self._get_session() as session:
            word = self._get_word(name)
            if isinstance(content, str):
                # If it is a str, even empty, we need to assign it, though an empty list evals as falsey
                word.content = content
            if isinstance(tags, list):
                # If it is a list, even empty, we need to assign it, though an empty list evals as falsey
                word.tags = tags
            session.add(word)
            session.commit()

    def _get_word(self, name: str) -> Word:
        with self._get_session() as session:
            return session.execute(select(Word).where(Word.name == name)).scalar_one()

    def _get_session(self) -> Session:
        return Session(self.engine)

    def _create_dbs(self):
        Base.metadata.create_all(self.engine)
