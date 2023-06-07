from flet_core import (
    ButtonStyle,
    FontWeight,
    IconButton,
    ListTile,
    MaterialState,
    PopupMenuButton,
    PopupMenuItem,
    Row,
    Text,
    TextThemeStyle,
    UserControl,
    colors,
    icons,
)


class Words(UserControl):
    def __init__(
        self, title: str, words: str, tags: set[str], edit_me: callable, delete_me: callable
    ):
        super().__init__()

        self._title = title
        self._words = words
        self._tags = sorted(tags)
        self.delete_me = delete_me
        self.edit_me = edit_me

    @property
    def words(self):
        return self._words

    @property
    def title(self):
        return self._title

    @property
    def tags(self) -> list[str]:
        return sorted(self._tags)

    # noinspection PyAttributeOutsideInit
    def build(self):
        self.copy_icon = IconButton(
            icon=icons.COPY_SHARP,
            icon_size=35,
            on_click=self.set_clip,
            tooltip="Copy the text.",
            style=ButtonStyle(
                color={
                    MaterialState.PRESSED: colors.RED,
                    MaterialState.DEFAULT: colors.WHITE,
                }
            ),
        )
        self.words_text = Text(value=self._words, max_lines=1)
        self.title_text = Text(value=self._title)
        self.tag_text = Text(
            value=", ".join(self.tags),
            style=TextThemeStyle.BODY_MEDIUM,
            italic=True,
            weight=FontWeight.BOLD,
        )
        self.popup_menu = PopupMenuButton(
            items=[
                PopupMenuItem(text="Edit", on_click=self.edit_me),
                PopupMenuItem(text="Delete", on_click=self.delete_me),
            ],
        )
        self.list_tile = ListTile(
            leading=self.copy_icon,
            title=Row([self.title_text, self.tag_text]),
            subtitle=self.words_text,
            trailing=self.popup_menu,
        )
        return self.list_tile

    def delete_clicked(self, _):
        self.delete_me(self)

    def set_clip(self, _):
        self.page.set_clipboard(self.words)
