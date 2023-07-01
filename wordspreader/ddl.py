from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship
from sqlalchemy_utils import auto_delete_orphans


class DuplicateKeyException(BaseException):
    pass


class Base(MappedAsDataclass, DeclarativeBase, eq=True, repr=True, unsafe_hash=True):
    pass


tagging = Table(
    "tagging",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
    Column("entry_id", Integer, ForeignKey("words.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, init=True)


class Word(Base):
    __tablename__ = "words"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(unique=True, init=True)
    content: Mapped[str]
    tag_objs: Mapped[set[Tag]] = relationship(
        "Tag",
        secondary=tagging,
        backref="words",
        init=False,
        lazy="joined",
        collection_class=set,
    )
    tags: AssociationProxy[set[str]] = association_proxy("tag_objs", "name")


auto_delete_orphans(Word.tag_objs)
