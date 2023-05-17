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
    colors,
    icons,
)
from flet_core import ClipBehavior, Control, ControlEvent, OptionalNumber, Ref, Stack
from flet_core.types import AnimationValue, OffsetValue, ResponsiveNumber, RotateValue, ScaleValue

from wordspreader.persistence import DBPersistence


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class Tag(UserControl):
    def __init__(self, tag: str, delete_me: callable):
        super().__init__()
        self._tag = tag
        self._delete_me = delete_me

    def build(self):
        self._label = flet.Text(value=self._tag)
        self._icon_button = IconButton(
            icon=flet.icons.CANCEL_OUTLINED, on_click=self._delete_me, data={"tag": self._tag}
        )
        return Row([self._label, self._icon_button])


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class Words(UserControl):
    def __init__(self, title: str, words: str, tags: set[str], edit_me: callable, delete_me: callable):
        super().__init__()

        self._title = title
        self._words = words
        self._tags = {t: self._make_tag(t) for t in tags}
        self.delete_me = delete_me
        self.edit_me = edit_me

    @property
    def words(self):
        return self._words

    @words.setter
    def words(self, value):
        self.edit_me(content=value)
        self._words = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self.edit_me(new_name=value)
        self._title = value

        self.display_words.value = value
        self.display_words.update()

    def build(self):
        self.display_words = Text(self.title)
        # This is used for either title or content
        self.edit_stuff = TextField(expand=1)
        self._tag_row = Row(controls=[t for t in self._tags.values()])
        self.display_view = Row(
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
            controls=[
                self.display_words,
                Row(
                    spacing=0,
                    controls=[
                        self._tag_row,
                        IconButton(icon=icons.COPY, tooltip="Copy Words", on_click=self.set_clip),
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="Edit Words",
                            on_click=self.edit_words_clicked,
                        ),
                        IconButton(
                            icon=icons.TITLE,
                            tooltip="Edit Title",
                            on_click=self.edit_title_clicked,
                        ),
                        IconButton(
                            icons.DELETE_OUTLINE,
                            tooltip="Delete Words",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = Row(
            visible=False,
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_stuff,
                IconButton(
                    icon=icons.CANCEL_OUTLINED,
                    icon_color=colors.RED,
                    on_click=self.cancel_clicked,
                ),
                IconButton(
                    icon=icons.DONE_OUTLINE_OUTLINED,
                    icon_color=colors.GREEN,
                    on_click=self.save_clicked,
                ),
            ],
        )
        return Stack(controls=[self.display_view, self.edit_view])

    def edit_words_clicked(self, _):
        self.edit_stuff.value = self.words
        self.display_view.visible = False
        self.edit_view.visible = True
        self.edit_stuff.tooltip = "Update words"
        self.editing = "words"
        self.update()

    def edit_title_clicked(self, _):
        self.edit_stuff.value = self.title
        self.display_view.visible = False
        self.edit_view.visible = True
        self.edit_stuff.tooltip = "Update title"
        self.editing = "title"
        self.update()

    def save_clicked(self, _):
        new = self.edit_stuff.value
        if self.editing == "title":
            self.title = new
        elif self.editing == "words":
            self.words = new
        else:
            raise RuntimeError()
        self.cancel_clicked()

    def delete_clicked(self, _):
        self.delete_me(self)

    def cancel_clicked(self, _: ControlEvent = None):
        self.display_view.visible = True
        self.edit_view.visible = False
        self.editing = None
        self.update()

    def set_clip(self, _):
        self.page.set_clipboard(self.words)

    def _make_tag(self, t: str) -> Tag:
        def remove_tag(_):
            self.edit_me(self._words, self._tags_without_one(t))
            self._tag_row.controls.remove(self._tags.pop(t))
            self.update()

        return Tag(tag=t, delete_me=remove_tag)

    def _tags_without_one(self, t: str) -> set[str]:
        return set(filter(lambda x: x != t, self._tags.keys()))


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
