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


class Words(UserControl):
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False
        self.task_name = task_name
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def build(self):
        self.display_task = Checkbox(value=False, label=self.task_name, on_change=self.status_changed)
        self.edit_name = TextField(expand=1)

        self.display_view = Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.display_task,
                Row(
                    spacing=0,
                    controls=[
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
            alignment="spaceBetween",
            vertical_alignment="center",
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
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completed = self.display_task.value
        self.task_status_change(self)

    def delete_clicked(self, e):
        self.task_delete(self)


# noinspection PyAttributeOutsideInit
class WordSpreader(UserControl):
    def build(self):
        self.new_title = TextField(
            hint_text="Title the words.",
            expand=True,
        )
        self.new_words = TextField(
            hint_text="Provide the words.",
            expand=True,
            multiline=True,
        )
        self.tasks = Column()

        self.category = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all")],
        )

        # application's root control (i.e. "view") containing all other controls
        return Column(
            width=600,
            controls=[
                Row([Text(value="Words to Spread", style="headlineMedium")], alignment="center"),
                Row(
                    controls=[
                        self.new_title,
                    ]
                ),
                Row(
                    controls=[
                        self.new_words,
                    ]
                ),
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
            task = Words(self.new_title.value, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_title.value = ""
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
            if not task.completed:
                count += 1
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
