import logging
from collections.abc import Iterable
from typing import Literal

import flet as ft
from flet_core import (
    Column,
    Container,
    ControlEvent,
    CrossAxisAlignment,
    FloatingActionButton,
    MainAxisAlignment,
    ResponsiveRow,
    Text,
    TextButton,
    TextField,
    TextThemeStyle,
    icons,
)

from wordspreader.components import Words

log = logging.getLogger(__name__)
MODE_TYPE = Literal["edit", "new"]


# noinspection PyAttributeOutsideInit
class WordModal(ft.BottomSheet):
    def __init__(self, new_word: callable, edit_word: callable):
        super().__init__()
        self.new_word = new_word
        self.edit_word = edit_word
        self._mode: MODE_TYPE = "new"
        self._editing: Words | None
        self.orig_key: str | None = None
        self._header = Text("Add new Words to spread.", style=TextThemeStyle.HEADLINE_LARGE)
        self._title = TextField(label="Title")
        self._words = TextField(label="Content", multiline=True, min_lines=3)
        self._tags = TextField(
            label="Keywords",
            helper_text="Press Enter to submit a keyword to the list",
            on_submit=self.add_tag,
        )
        self._tags_set = set()
        self._tag_display = ResponsiveRow(
            alignment=MainAxisAlignment.START, vertical_alignment=CrossAxisAlignment.START
        )
        self._fab = FloatingActionButton(
            icon=icons.ADD, on_click=self.save, tooltip="Add the word."
        )
        self.column = Column(
            [self._header, self._title, self._words, self._tags, self._tag_display, self._fab],
            expand=True,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            tight=True,
        )
        self.container = Container(self.column)
        super().__init__(content=self.container)

    def _reset(self):
        del self.words

    def add_word(self):
        """Creates the word and resets the form"""
        title = self._title.value.strip()
        words = self._words.value.strip()
        if title and words:
            self.new_word(title=title, words=words, tags=self._tags_set)
        self._reset()

    def add_tag(self, _):
        """Handles the submit on the tag field, clears the field and adds the tag to the list of tags"""
        tag = self._tags.value.strip()
        logging.debug(f"Got tag named `{tag}`")
        if tag not in self._tags_set and tag:
            logging.debug(f"tag `{tag}` is new and not empty")
            self._tag_display.controls.append(self._make_tag_obj(tag))
            self._tags_set.add(tag)
        self._tags.value = ""
        self._tags.focus()
        self.update()

    def delete_tag(self, e: ControlEvent):
        new_tags = self.tags
        new_tags.remove(e.control.text.strip())
        self.tags = new_tags

    def _make_tag_obj(self, name: str):
        logging.debug(f"Creating textbutton for {self.title}")
        return TextButton(
            name, icon=icons.DELETE, icon_color="red", expand=False, on_click=self.delete_tag
        )

    def save(self, _):
        match self._mode:
            case "new":
                self.add_word()
            case "edit":
                self.save_edited_word()

    def build(self):
        return self

    def setup_edit_word(self, word: Words):
        self._editing = word
        self.title = word.title
        self.words = word.words
        self.tags = word.tags
        self.mode = "edit"
        self.update()

    def save_edited_word(self):
        # If the names are the same, it should send None
        log.debug("Saving changes to word `%s`", self._editing.title)
        self.edit_word(self._editing.title, self.words, self.tags, self.title)
        self._editing.title = self.title
        self._editing.words = self.words
        self._editing.tags = self.tags
        self._reset()

    @property
    def title(self):
        return self._title.value

    @title.setter
    def title(self, value):
        if self._title.value != value:
            log.debug("Updating words from `%s` to `%s`", self._title.value, value)
            self._title.value = value
            self.container.update()
        else:
            log.debug("Skipping updating title as the new value evaluated equal")

    @title.deleter
    def title(self):
        self.title = ""

    @property
    def words(self):
        return self._words.value

    @words.setter
    def words(self, value: str):
        if self._words.value != value:
            log.debug("Updating words from `%s` to `%s`", self._words.value, value)
            self._words.value = value
            self.container.update()
        else:
            log.debug("Skipping updating words as the new value evaluated equal")

    @words.deleter
    def words(self):
        self.words = ""

    @property
    def tags(self) -> set[str]:
        return self._tags_set

    @tags.setter
    def tags(self, value: Iterable[str]):
        new_tags = value if isinstance(value, set) else set(value)
        if new_tags != self._tags_set:
            log.debug("Updating words from `%s` to `%s`", self._tags_set, new_tags)
            self._tags_set = new_tags
            self._tag_display.controls = [self._make_tag_obj(t) for t in sorted(self.tags)]
            self.container.update()
        else:
            log.debug(
                "Skipping updating tags as the new value `%s` evaluated equal to `%s`",
                new_tags,
                self._tags_set,
            )

    @tags.deleter
    def tags(self):
        self.tags = set()

    @property
    def mode(self) -> MODE_TYPE:
        return self._mode

    @mode.setter
    def mode(self, value):
        match value:
            case "new":
                pass
            case "edit":
                pass
            case _:
                # Pycharm doing weird stuff, acting like MODE_TYPE is the type it is describing.
                # noinspection PyUnresolvedReferences
                msg = f"Invalid set value, received `{value}` expected one of {MODE_TYPE.__args__}"
                raise RuntimeError(msg)
        self._mode = value
