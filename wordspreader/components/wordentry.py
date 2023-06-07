import logging
from typing import Any

from flet_core import (
    ClipBehavior,
    Control,
    ControlEvent,
    IconButton,
    OptionalNumber,
    Ref,
    ResponsiveRow,
    Row,
    Text,
    TextField,
    UserControl,
    colors,
    icons,
)
from flet_core.types import AnimationValue, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue


class WordEntry(UserControl):
    def __init__(
        self,
        new_word: callable,
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
        self.new_word = new_word
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
        self.add_new_words = IconButton(
            icons.ADD, on_click=self.add_clicked, icon_color=colors.GREEN
        )

    def build(self):
        return ResponsiveRow(
            controls=[
                self.new_title,
                self.new_words,
                self.new_tags_entry,
                self.new_tags_entered,
                self.add_new_words,
            ],
            expand=True,
        )

    def add_new_tag(self, e: ControlEvent):
        new_tag_name = e.control.value
        e.control.value = ""
        self.new_tags_entry.focus()
        for tag in self.new_tags_entered.controls:
            if tag.value == new_tag_name:
                # We already have this tag in the list
                word_name = "UNTITLED" if not (tv := self.new_title.value) else tv
                logging.info(
                    f"Skipping adding duplicate tag `{new_tag_name}` to word `{word_name}`"
                )
                return
        self.new_tags_entered.controls.append(Text(new_tag_name))
        self.new_tags_entered.update()
        self.new_tags_entry.update()

    def reset(self):
        self.new_title.value = ""
        self.new_words.value = ""
        self.new_tags_entered.controls.clear()
        self.new_title.focus()
        self.update()

    def add_clicked(self, _: ControlEvent):
        if self.new_title.value:
            tags = {t.value for t in self.new_tags_entered.controls}

            self.new_word(self.new_title.value, self.new_words.value, tags)
            self.reset()
