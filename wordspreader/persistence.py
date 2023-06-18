from __future__ import annotations

import uuid
from collections.abc import Iterator
from itertools import chain
from pathlib import Path

from sqlalchemy import Column, ForeignKey, String, Table, create_engine, delete, select
from sqlalchemy.engine import Engine
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
    relationship,
)


class DuplicateKeyException(BaseException):
    pass


class Base(MappedAsDataclass, DeclarativeBase, eq=True, repr=True):
    pass


association_table = Table(
    "word_to_tag",
    Base.metadata,
    Column("word_id", ForeignKey("word.word_id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.name"), primary_key=True),
)


class Word(Base):
    __tablename__ = "word"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    content: Mapped[str] = mapped_column(String(2000))
    tgs_: Mapped[set[Tag]] = relationship(
        secondary=association_table, lazy="joined", init=False, repr=False
    )
    tags: AssociationProxy[set[str]] = association_proxy("tgs_", "name")
    word_id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, init=False, repr=False
    )


class Tag(Base, unsafe_hash=True):
    __tablename__ = "tag"
    name: Mapped[str] = mapped_column(String(100), primary_key=True, unique=True)


class DBPersistence:
    def __init__(self, engine: Engine):
        self.engine = engine
        Base.metadata.create_all(self.engine)

    @classmethod
    def from_file(cls, db_file: Path):
        return cls(create_engine(f"sqlite:///{db_file.resolve().absolute()}"))

    def new_word(self, name: str, content: str, tags: set[str] = None) -> Word:
        with self._get_session() as session:
            db_tags = self.resolve_tags(tags, session)
            word = Word(name=name, content=content, tags={})
            word.tgs_ = db_tags
            session.add(word)
            session.commit()
            word = session.scalar(select(Word).where(Word.name == name))
        return word

    @staticmethod
    def resolve_tags(tags: set[str], session: Session) -> set[Tag]:
        tags_from_db = list(
            session.execute(select(Tag).where(Tag.name.in_(tags))).unique().scalars()
        )
        found_tag_names = {tag.name for tag in tags_from_db}
        created_tags = [Tag(name=t) for t in tags - found_tag_names]
        session.add_all(created_tags)
        session.commit()
        return set(chain(created_tags, tags_from_db))

    def update_word(
        self, name: str, content: str = None, tags: set[str] = None, new_name: str = None
    ):
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
            query = query.where(Word.tags == category)

        with self._get_session() as session:
            yield from session.scalars(query).unique()

    def get_word(self, name: str) -> Word:
        with self._get_session() as session:
            return self._get_word(session, name)

    def get_words_like(self, name: str) -> Iterator[Word]:
        with self._get_session() as session:
            yield from session.execute(select(Word).where(Word.name.like(name))).unique().scalars()

    def get_all_tags(self) -> Iterator[str]:
        with self._get_session() as session:
            yield from session.execute(select(Tag.name)).scalars()

    def _rename_word(self, old_name: str, new_name: str):
        """Changes the primary key"""
        with self._get_session() as session:
            maybe_new_word = self._get_word(session, new_name)
            if maybe_new_word:
                msg = f'New name: `{new_name}` is already taken, pick another name"'
                raise DuplicateKeyException(msg)
            word = self._get_word(session, old_name)
            word.name = new_name
            session.add(word)
            session.commit()

    def _update_word(self, name: str, content: str = None, tags: set[str] = None):
        """Doesn't change primary key, just content and/or tags"""
        with self._get_session() as session:
            word = self._get_word(session, name, True)
            if content is not None:
                # If it is a str, even empty, we need to assign it, though an empty list evals as falsey
                word.content = content
            if tags is not None:
                # If it is a list, even empty, we need to assign it, though an empty list evals as falsey
                word.tags = tags
            session.add(word)
            session.commit()

    @staticmethod
    def _get_word(session: Session, name: str, for_update: bool = False) -> Word | None:
        query = select(Word).where(Word.name == name)
        if for_update:
            query.with_for_update()

        return session.execute(query).unique().scalar_one_or_none()

    def _get_session(self) -> Session:
        return Session(self.engine)
