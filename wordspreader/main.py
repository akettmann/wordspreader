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
    Text,
    UserControl,
)
from flet_core import (
    BottomSheet,
    ClipBehavior,
    Control,
    ControlEvent,
    FloatingActionButton,
    IconButton,
    OptionalNumber,
    Ref,
    TextThemeStyle,
    colors,
    icons,
)
from flet_core.types import (
    AnimationValue,
    MainAxisAlignment,
    OffsetValue,
    ResponsiveNumber,
    RotateValue,
    ScaleValue,
)

from wordspreader.components import Words
from wordspreader.components.worddisplay import WordDisplay
from wordspreader.components.wordentry import WordModal
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

        def open_bs(_):
            self.bs.open = True
            self.bs.update()

        def close_bs(_):
            self.bs.open = False
            self.bs.update()

        self.db = db
        self.word_display = WordDisplay(self.db)
        self.word_modal = WordModal(self.new_word, self.db.update_word)
        self.bs = BottomSheet(self.word_modal)
        self.fab = FloatingActionButton(icon=icons.ADD, bgcolor=colors.BLUE, on_click=open_bs)

    @classmethod
    def default_app_dir_db(cls):
        """Creates an instance using the default"""
        cls.default_db_path.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Using file path `{cls.default_db_path}` for the database")
        return cls(DBPersistence.from_file(cls.default_db_path))

    def did_mount(self):
        self.page.floating_action_button = self.fab
        self.page.overlay.append(self.bs)
        self.page.add(self.fab)

    @classmethod
    @property
    def default_db_path(cls) -> Path:
        dirs = appdirs.AppDirs("WordSpreader", "mriswithe")
        return Path(dirs.user_data_dir) / "wordspreader.sqlite3"

    def build(self):
        # application's root control (i.e. "view") containing all other controls
        return Column(
            controls=[
                Row(
                    [
                        Text(value="Words to Spread", style=TextThemeStyle.HEADLINE_MEDIUM),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                ),
                self.word_display,
            ],
        )

    def update(self):
        self.word_display.update()
        super().update()

    def db_word_to_flet_word(self, db_word: Word) -> Words:
        return Words(
            db_word.name,
            db_word.content,
            db_word.tags,
            partial(self.db.update_word, db_word.name),
            partial(self.db.delete_word, db_word.name),
        )

    def new_word(self, title: str, words: str, tags: set[str] = None):
        self.db.new_word(title, words, tags)
        self.bs.open = False
        self.bs.update()
        self.update()


def main(page: Page):
    page.title = "Word Spreader"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    # create application instance
    app = WordSpreader.default_app_dir_db()
    # add application's root control to the page
    page.add(app)


flet.app(target=main)
