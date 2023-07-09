import logging
from collections.abc import Iterable

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

log = logging.getLogger(f"{__name__}.Words")


class Words(UserControl):
    """
    One instance is for one Words entry, its title, content and tags
    """

    def __init__(
        self, title: str, words: str, tags: Iterable[str], edit_me: callable, delete_me: callable
    ):
        super().__init__()
        self._tags = tags if isinstance(tags, set) else set(tags)
        self.edit_me = edit_me
        self.delete_me = delete_me
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
        self.words_text = Text(value=words, max_lines=1)
        self.title_text = Text(value=title)
        self.tag_text = Text(
            style=TextThemeStyle.BODY_MEDIUM,
            italic=True,
            weight=FontWeight.BOLD,
        )
        self.popup_menu = PopupMenuButton(
            items=[
                PopupMenuItem(text="Edit", on_click=lambda _: self.edit_me(self)),
                PopupMenuItem(text="Delete", on_click=lambda _: self.delete_me(self)),
            ],
        )
        self.list_tile = ListTile(
            leading=self.copy_icon,
            title=Row([self.title_text, self.tag_text]),
            subtitle=self.words_text,
            trailing=self.popup_menu,
        )
        self._render_tags()

    @property
    def words(self):
        """The Long form content, not the title."""
        return self.words_text.value

    @words.setter
    def words(self, value: str):
        log.debug("Updating the words from `%s` to `%s`", self.words_text.value, value)
        self.words_text.value = value
        self.words_text.update()

    @property
    def title(self):
        """The Title, not the long form content or words"""
        return self.title_text.value

    @title.setter
    def title(self, value: str):
        log.debug("Updating the title from `%s` to `%s`", self.title_text.value, value)
        self.title_text.value = value
        self.title_text.update()

    @property
    def tags(self) -> set[str]:
        """Tag words or topics"""
        return self._tags

    @tags.setter
    def tags(self, value: Iterable[str]):
        value = value if isinstance(value, set) else set(value)
        log.debug("Updating the tags from `%s` to `%s`", self._tags, value)
        self._tags = value
        self._render_tags()
        self.tag_text.update()

    def _render_tags(self):
        self.tag_text.value = ", ".join(sorted(t.title() for t in self.tags))

    def build(self):
        return self.list_tile

    def delete_clicked(self, _):
        self.delete_me(self)

    def set_clip(self, _):
        self.page.set_clipboard(self.words)
