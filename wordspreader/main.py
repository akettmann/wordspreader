import logging
from functools import partial
from pathlib import Path
from typing import Any

import appdirs
import flet
from flet import (
    Column,
    Page,
    Row,
    Tab,
    Tabs,
    Text,
    UserControl,
)
from flet_core import ClipBehavior, Control, ControlEvent, OptionalNumber, Ref
from flet_core.types import AnimationValue, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue

from wordspreader.components import Words
from wordspreader.components.wordentry import WordEntry
from wordspreader.persistence import DBPersistence, Word


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

    def build(self):
        self.word_entry = WordEntry(self.new_word)

        self.tasks = Column(controls=self._build_all_words())
        self.keywords = Tabs(
            selected_index=0,
            on_change=self.filter_changed,
            tabs=self._build_keywords(),
        )

        # application's root control (i.e. "view") containing all other controls
        return Column(
            controls=[
                Row(
                    [Text(value="Words to Spread", style=flet.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=flet.MainAxisAlignment.CENTER,
                ),
                Column(
                    spacing=25,
                    controls=[
                        self.word_entry,
                        self.keywords,
                        self.tasks,
                    ],
                ),
            ],
        )

    def _build_all_words(self) -> list[Words]:
        return [
            Words(
                word.name,
                word.content,
                word.tags,
                partial(self.db.update_word, word.name),
                self.delete_words,
            )
            for word in self.db.get_words_filtered()
        ]

    def _build_keywords(self, current_tags: list[Tab] = None) -> list[Tab]:
        set(self.db.get_all_tags())
        # This will be empty if the current_tags is not provided, so we make all of them
        {t.text for t in current_tags or []}
        tabs = [Tab(text="all")]
        tabs.extend([Tab(text=t) for t in self.db.get_all_tags()])
        return tabs

    def delete_words(self, words: Words):
        self.db.delete_word(words.title)
        self.tasks.controls.remove(words)
        self.update()

    def filter_changed(self, _: ControlEvent):
        status = self.keywords.tabs[self.keywords.selected_index].text
        if status == "all":
            for task in self.tasks.controls:
                task.visible = True
        else:
            for task in self.tasks.controls:
                task.visible = status in task.tags
        self.update()

    def update(self):
        super().update()

    def db_word_to_flet_word(self, db_word: Word) -> Words:
        return Words(
            db_word.name,
            db_word.content,
            db_word.tags,
            partial(self.db.update_word, db_word.name),
            partial(self.db.delete_word, db_word.name),
        )

    def new_word(self, title: str, words: str, tags: set[str] = None) -> Words:
        db_word = self.db.new_word(title, words, tags)
        self.update()
        return self.db_word_to_flet_word(db_word)


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
