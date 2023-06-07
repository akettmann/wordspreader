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
from wordspreader.persistence import DBPersistence


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
        self.words.controls.insert(0, self.keywords)

        return [self.keywords, self.words]

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
