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

MODE_TYPE = Literal["edit", "new"]


class WordModal(ft.UserControl):
    def __init__(self, new_word: callable, edit_word: callable):
        super().__init__()
        self.new_word = new_word
        self.edit_word = edit_word
        self._mode: MODE_TYPE = "new"
        self.orig_key: str | None = None

    # noinspection PyAttributeOutsideInit
    def build(self):
        def add_tag(_):
            tag = self._tags.value.strip()
            if tag not in self.tags_set and tag:
                self._tag_display.controls.append(Text(tag))
                self._tag_display.update()
                self.tags_set.add(tag)
            self._tags.value = ""
            self._tags.focus()
            self._tags.update()

        def reset():
            self._title.value = ""
            self._words.value = ""
            self._tags.value = ""
            self.tags_set = set()
            self.update()

        def add_word(_):
            title = self._title.value.strip()
            words = self._words.value.strip()
            if title and words:
                self.new_word(title=self._title.value, words=self._words.value, tags=self.tags_set)
            reset()

        self._header = Text("Add new Words to spread.", style=TextThemeStyle.HEADLINE_LARGE)
        self._title = TextField(label="Title")
        self._words = TextField(label="Content", multiline=True, min_lines=3)
        self._tags = TextField(
            label="Keywords",
            helper_text="Press Enter to submit a keyword to the list",
            on_submit=add_tag,
        )
        self.tags_set = set()
        self._tag_display = ResponsiveRow()
        self._fab = FloatingActionButton(icon=icons.ADD, on_click=add_word)
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
                raise RuntimeError(
                    f"Invalid set value, received `{value}` expected one of {MODE_TYPE.__args__}"
                )
        self._mode = value

    def submit(self):
        match self._mode:
            case "new":
                self.new_word(name=self.title, content=self.words, tags=self.tags)
