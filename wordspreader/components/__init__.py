import flet
from flet_core import (
    ControlEvent,
    IconButton,
    ListTile,
    PopupMenuButton,
    PopupMenuItem,
    Row,
    Stack,
    Text,
    TextField,
    UserControl,
    colors,
    icons,
)


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
        # Old
        self.display_words.value = value
        self.display_words.update()
        # New
        self.display_view2.title = value
        self.display_view2.update()

    @property
    def tags(self) -> set[str]:
        return set(self._tags.keys())

    def build(self):
        self.display_words = Text(self.title)
        # This is used for either title or content
        self.edit_stuff = TextField(expand=1)
        self._tag_row = Row(controls=list(self._tags.values()))
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
        self.title_widget = Text(self._title)
        self.tags_widgets = [
            IconButton(
                icon=icons.DELETE,
            )
        ]
        self.display_view2 = ListTile(
            leading=IconButton(icon=icons.COPY, tooltip="Copy Words", on_click=self.set_clip),
            title=Row(
                [
                    self.title_widget,
                ]
            ),
            trailing=PopupMenuButton(
                icon=icons.MORE_VERT,
                items=[
                    PopupMenuItem(text="Edit Words", on_click=self.edit_words_clicked),
                    PopupMenuItem(text="Edit Title", on_click=self.edit_title_clicked),
                    PopupMenuItem(text="Delete Words", on_click=self.delete_clicked),
                ],
            ),
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
        return Stack(controls=[self.display_view2, self.edit_view])

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
