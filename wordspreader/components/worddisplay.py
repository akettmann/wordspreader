from functools import partial
from typing import Any

from flet_core import (
    ClipBehavior,
    Column,
    Control,
    ControlEvent,
    OptionalNumber,
    Ref,
    Tab,
    Tabs,
    UserControl,
)
from flet_core.types import AnimationValue, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue

from wordspreader.components import Words
from wordspreader.persistence import DBPersistence, Word


# noinspection PyAttributeOutsideInit
class WordDisplay(UserControl):
    def __init__(
        self,
        db: DBPersistence,
        controls: list[Control] | None = None,
        ref: Ref | None = None,
        key: str | None = None,
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
            key,
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

    def build(self):
        self.keywords = Tabs(
            on_change=self.filter_changed,
            tabs=self._build_keywords(),
        )
        self.words = Column(controls=self._build_all_words())

        return Column([self.keywords, self.words])

    def delete_words(self, words: Words):
        self.db.delete_word(words.title)
        self.words.controls.remove(words)
        self.update()

    def filter_changed(self, _: ControlEvent):
        status = self.keywords.tabs[self.keywords.selected_index].text
        if status == "all":
            # Skipping the first object, it is the tabs object
            for word in self.words.controls[1:]:
                word.visible = True
        else:
            # Skipping the first object, it is the tabs object
            for word in self.words.controls[1:]:
                word: Words
                word.visible = status in word.tags
        self.update()

    def _build_keywords(self) -> list[Tab]:
        tabs = [Tab(text="all")]
        tabs.extend([Tab(text=t) for t in sorted(self.db.get_all_tags())])
        return tabs

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

    @staticmethod
    def _keyword_key(element: Tab):
        match element:
            case "all":
                return (0, Tab.text)
            case _:
                return (1, Tab.text)

    def _sort_keywords(self):
        self.keywords.tabs.sort(key=WordDisplay._keyword_key)
        self.keywords.update()

    def update(self):
        current_tags = {t.text for t in self.keywords.tabs}
        all_tags_from_db = set(self.db.get_all_tags())
        if missing_tags := all_tags_from_db - current_tags:
            self.keywords.tabs = self._build_keywords()
            self.keywords.update()
        all_word_names_from_db = {w.name for w in self.db.get_words_filtered()}
        current_word_names = {w.title for w in self.words.controls[1:]}
        if missing_words := all_word_names_from_db - current_word_names:
            self.words.controls = self._build_all_words()
            self.words.update()
        self._sort_keywords()
        super().update()
