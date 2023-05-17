import logging
from functools import partial
from pathlib import Path
from typing import Any

import appdirs
import flet
from flet import (
    Column,
    IconButton,
    Page,
    Row,
    Tab,
    Tabs,
    Text,
    TextField,
    UserControl,
    icons,
)
from flet_core import ClipBehavior, Control, ControlEvent, OptionalNumber, Ref
from flet_core.types import AnimationValue, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue

from wordspreader.components import Words
from wordspreader.persistence import DBPersistence


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class WordSpreader(UserControl):
    def __init__(
        self,
        db: DBPersistence,
        controls: list[Control] | None = None,
        ref: Ref | None = None,
        width: OptionalNumber = None,
        height: OptionalNumber = None,
        left: OptionalNumber = None,
        top: OptionalNumber = None,
        right: OptionalNumber = None,
        bottom: OptionalNumber = None,
        expand: None | bool | int = None,
        col: ResponsiveNumber | None = None,
        opacity: OptionalNumber = None,
        rotate: RotateValue = None,
        scale: ScaleValue = None,
        offset: OffsetValue = None,
        aspect_ratio: OptionalNumber = None,
        animate_opacity: AnimationValue = None,
        animate_size: AnimationValue = None,
        animate_position: AnimationValue = None,
        animate_rotation: AnimationValue = None,
        animate_scale: AnimationValue = None,
        animate_offset: AnimationValue = None,
        on_animation_end=None,
        visible: bool | None = None,
        disabled: bool | None = None,
        data: Any = None,
        clip_behavior: ClipBehavior | None = None,
    ):
        super().__init__(
            controls,
            ref,
            width,
            height,
            left,
            top,
            right,
            bottom,
            expand,
            col,
            opacity,
            rotate,
            scale,
            offset,
            aspect_ratio,
            animate_opacity,
            animate_size,
            animate_position,
            animate_rotation,
            animate_scale,
            animate_offset,
            on_animation_end,
            visible,
            disabled,
            data,
            clip_behavior,
        )

        self.db = db

    @classmethod
    def default_app_dir_db(cls):
        """Creates an instance using the default"""
        dirs = appdirs.AppDirs("WordSpreader", "mriswithe")
        db_file = Path(dirs.user_data_dir) / "wordspreader.sqlite3"
        db_file.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Using file path `{db_file}` for the database")
        return cls(DBPersistence.from_file(db_file))

    def add_new_tag(self, e: ControlEvent):
        new_tag_name = e.control.value
        e.control.value = ""
        self.new_tags_entry.focus()
        for tag in self.new_tags_entered.controls:
            if tag.value == new_tag_name:
                # We already have this tag in the list
                word_name = "UNTITLED" if not (tv := self.new_title.value) else tv
                logging.info(f"Skipping adding duplicate tag `{new_tag_name}` to word `{word_name}`")
                return
        self.new_tags_entered.controls.append(Text(new_tag_name))
        self.update()

    def build(self):
        self.new_title = TextField(
            label="Title the words.",
            expand=True,
        )
        self.new_words = TextField(label="Provide the words.", expand=True, multiline=True)
        self.new_tags_entry = TextField(
            label="Provide the tags (Optional)",
            expand=True,
            on_submit=self.add_new_tag,
            counter_text="Press enter to submit a tag",
        )
        self.new_tags_entered = Row()
        self.add_new_words = IconButton(icons.ADD, on_click=self.add_clicked)

        self.tasks = Column(
            controls=[
                Words(
                    word.name,
                    word.content,
                    word.tags,
                    partial(self.db.update_word, word.name),
                    self.delete_words,
                )
                for word in self.db.get_words_filtered()
            ]
        )

        self.category = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all")],
        )

        # application's root control (i.e. "view") containing all other controls
        return Column(
            controls=[
                Row(
                    [Text(value="Words to Spread", style=flet.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=flet.MainAxisAlignment.CENTER,
                ),
                Row(controls=[self.new_title]),
                Row(controls=[self.new_words]),
                Row(controls=[self.new_tags_entry]),
                Row(controls=[self.new_tags_entered]),
                self.add_new_words,
                Column(
                    spacing=25,
                    controls=[
                        self.category,
                        self.tasks,
                    ],
                ),
            ],
        )

    def add_clicked(self, _):
        if self.new_title.value:
            tags = {t.value for t in self.new_tags_entered.controls}
            words = Words(
                self.new_title.value,
                self.new_words.value,
                tags,
                partial(self.db.update_word, self.new_title.value),
                self.delete_words,
            )
            self.db.new_word(self.new_title.value, self.new_words.value, tags)
            self.tasks.controls.append(words)
            self.new_title.value = ""
            self.new_words.value = ""
            self.new_tags_entered.controls.clear()
            self.new_title.focus()
            self.update()

    def delete_words(self, words: Words):
        self.db.delete_word(words.title)
        self.tasks.controls.remove(words)
        self.update()

    def tabs_changed(self, _):
        self.update()

    def update(self):
        status = self.category.tabs[self.category.selected_index].text
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.completed is False)
                or (status == "completed" and task.completed)
            )

        super().update()


def main(page: Page):
    page.title = "Word Spreader"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    # create application instance
    app = WordSpreader.default_app_dir_db()
    # add application's root control to the page
    page.add(app)


logging.basicConfig(level=logging.INFO)
flet.app(target=main)
