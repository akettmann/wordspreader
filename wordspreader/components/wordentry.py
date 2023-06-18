from typing import Literal

import flet as ft
from flet_core import (
    Column,
    Container,
    CrossAxisAlignment,
    FloatingActionButton,
    MainAxisAlignment,
    ResponsiveRow,
    Row,
    Text,
    TextField,
    TextThemeStyle,
    icons,
)

from wordspreader.components import Words

MODE_TYPE = Literal["edit", "new"]


# noinspection PyAttributeOutsideInit
class WordModal(ft.UserControl):
    def __init__(self, new_word: callable, edit_word: callable):
        super().__init__()
        self.new_word = new_word
        self.edit_word = edit_word
        self._mode: MODE_TYPE = "new"
        self.orig_key: str | None = None

    def _reset(self):
        self._title.value = ""
        self._words.value = ""
        self._tags.value = ""
        self.tags_set = set()
        self.update()

    def add_word(self):
        title = self._title.value.strip()
        words = self._words.value.strip()
        if title and words:
            self.new_word(title=title, words=words, tags=self.tags_set)
        self._reset()

    def add_tag(self, _):
        tag = self._tags.value.strip()
        if tag not in self.tags_set and tag:
            self._tag_display.controls.append(Text(tag))
            self._tag_display.update()
            self.tags_set.add(tag)
        self._tags.value = ""
        self._tags.focus()
        self._tags.update()

    def save(self, _):
        match self._mode:
            case "new":
                self.add_word()
            case "edit":
                self.save_edited_word()

    def build(self):
        self._header = Text("Add new Words to spread.", style=TextThemeStyle.HEADLINE_LARGE)
        self._title = TextField(label="Title")
        self._words = TextField(label="Content", multiline=True, min_lines=3)
        self._tags = TextField(
            label="Keywords",
            helper_text="Press Enter to submit a keyword to the list",
            on_submit=self.add_tag,
        )
        self.tags_set = set()
        self._tag_display = ResponsiveRow()
        self._fab = FloatingActionButton(icon=icons.ADD, on_click=self.save)
        self.column = Column(
            [
                self._header,
                self._title,
                self._words,
                self._tags,
                self._tag_display,
                Row(
                    [
                        self._fab,
                    ],
                    alignment=MainAxisAlignment.END,
                ),
            ],
            expand=True,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
        self.container = Container(self.column)

        return self.container

    def setup_edit_word(self, word: Words):
        self._title.value = self.orig_key = word.title
        self._words.value = word.words
        self._tag_display.controls = [Text(t) for t in word.tags]
        self.tags_set = set(word.tags)
        self.mode = "edit"
        self.update()

    def save_edited_word(self):
        # If the names are the same, it should send None
        new_name = None if self.orig_key == (n := self._title.value.strip()) else n
        self.edit_word(self.orig_key, self._words.value.strip(), self.tags_set, new_name)
        self._reset()

    @property
    def title(self):
        return self._title.value

    @title.setter
    def title(self, value):
        self._title.value = value

    @property
    def words(self):
        return self._words.value

    @words.setter
    def words(self, value):
        self._words.value = value

    @property
    def tags(self):
        return self._tags.value

    @tags.setter
    def tags(self, value):
        self._tags.value = value

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
                raise RuntimeError(
                    f"Invalid set value, received `{value}` expected one of {MODE_TYPE.__args__}"
                )
        self._mode = value
