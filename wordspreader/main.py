from typing import Optional, List, Union, Any

import flet
from flet import (
    Checkbox,
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
from flet_core import ControlEvent, Control, Ref, OptionalNumber, ClipBehavior
from flet_core.types import ResponsiveNumber, RotateValue, ScaleValue, OffsetValue, AnimationValue

from wordspreader.persistence import DBPersistence


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class Words(UserControl):
    def __init__(self, title: str, words: str):
        super().__init__()

        self.title = title
        self.words = words

    def build(self):
        self.display_words = Checkbox(value=False, label=self.title, on_change=self.status_changed)
        self.edit_name = TextField(expand=1)

        self.display_view = Row(
            alignment=flet.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=flet.CrossAxisAlignment.CENTER,
            controls=[
                self.display_words,
                Row(
                    spacing=0,
                    controls=[
                        IconButton(icon=icons.COPY, tooltip="Copy Words", on_click=self.set_clip),
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="Edit Words",
                            on_click=self.edit_clicked,
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
                self.edit_name,
                IconButton(
                    icon=icons.DONE_OUTLINE_OUTLINED,
                    icon_color=colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_words.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_words.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_words.value
        self.task_status_change(self)

    def delete_clicked(self, e):
        self.task_delete(self)

    def set_clip(self, e: ControlEvent):
        self.page.set_clipboard(self.words)


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class WordSpreader(UserControl):
    def __init__(
        self,
        controls: Optional[List[Control]] = None,
        ref: Optional[Ref] = None,
        width: OptionalNumber = None,
        height: OptionalNumber = None,
        left: OptionalNumber = None,
        top: OptionalNumber = None,
        right: OptionalNumber = None,
        bottom: OptionalNumber = None,
        expand: Union[None, bool, int] = None,
        col: Optional[ResponsiveNumber] = None,
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
        visible: Optional[bool] = None,
        disabled: Optional[bool] = None,
        data: Any = None,
        clip_behavior: Optional[ClipBehavior] = None,
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
        self.dirs = appdirs.AppDirs('WordSpreader', 'mriswithe')
        self.db_file = Path(self.dirs.user_data_dir) / 'wordspreader.sqlite3'
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.db = DBPersistence(self.db_file)

    def build(self):
        def on_clicked(e: ControlEvent):
            print(e)

        self.new_title = TextField(
            label="Title the words.",
            expand=True,
        )
        self.new_words = TextField(label="Provide the words.", expand=True, multiline=True, on_submit=on_clicked)
        self.add_new_words = IconButton(icons.ADD, on_click=self.add_clicked)

        self.tasks = Column(controls=[Words(word.name, word.content) for word in self.db.get_words_filtered()])

        self.category = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all")],
        )

        # application's root control (i.e. "view") containing all other controls
        return Column(
            width=600,
            controls=[
                Row(
                    [Text(value="Words to Spread", style=flet.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=flet.MainAxisAlignment.CENTER,
                ),
                Row(
                    controls=[
                        self.new_title,
                    ]
                ),
                Row(controls=[self.new_words, self.add_new_words]),
                Column(
                    spacing=25,
                    controls=[
                        self.category,
                        self.tasks,
                    ],
                ),
            ],
        )

    def add_clicked(self, e):
        if self.new_title.value:
            words = Words(self.new_title.value, self.new_words.value)
            self.tasks.controls.append(words)
            self.new_title.value = ""
            self.new_words.value = ""
            self.new_title.focus()
            self.update()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completed:
                self.task_delete(task)

    def update(self):
        status = self.category.tabs[self.category.selected_index].text
        count = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.completed is False)
                or (status == "completed" and task.completed)
            )

        super().update()


def main(page: Page):
    page.title = "ToDo App"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    page.update()

    # create application instance
    app = WordSpreader()

    # add application's root control to the page
    page.add(app)


flet.app(target=main)
