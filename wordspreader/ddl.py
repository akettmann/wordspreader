from __future__ import annotations

import uuid

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship


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
