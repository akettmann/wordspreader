import logging
from pathlib import Path

import appdirs
import flet
from flet import (
    Column,
    Page,
    Row,
    Text,
    UserControl,
)
from flet.utils import open_in_browser
from flet_core import (
    AlertDialog,
    BottomSheet,
    FloatingActionButton,
    PopupMenuButton,
    PopupMenuItem,
    TextButton,
    TextThemeStyle,
    colors,
    icons,
)
from flet_core.types import (
    MainAxisAlignment,
)

from wordspreader.components import Words
from wordspreader.components.worddisplay import WordDisplay
from wordspreader.components.wordentry import WordModal
from wordspreader.persistence import DBPersistence


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class WordSpreader(UserControl):
    def setup_edit_word(self, word: Words):
        self.word_modal.setup_edit_word(word)
        self.open_bs()

    def setup_delete_word(self, word: Words):
        self._to_delete = word
        self.alert_dialog.open = True
        self.alert_dialog.content = Column(
            [
                Text(value=word.title),
                Text(value=word.words),
                word.make_tag_text(),
            ],
            tight=True,
        )
        self.alert_dialog.update()
        self.page.update()

    def delete_word_and_cleanup(self, _=None):
        try:
            self.db.delete_word(self._to_delete.title)
        finally:
            self._to_delete = None
        self.word_display.update()
        self.close_alert_dialog()

    def word_entry_edit_word(self, *args, **kwargs):
        self.db.update_word(*args, **kwargs)
        self.word_display.update()
        self.close_bs()

    def __init__(self, db: DBPersistence):
        super().__init__()

        self.db = db
        self.word_display = WordDisplay(self.db, self.setup_edit_word, self.setup_delete_word)
        self.word_modal = WordModal(self.new_word, self.word_entry_edit_word)
        self.bs = BottomSheet(self.word_modal)
        self.fab = FloatingActionButton(icon=icons.ADD, bgcolor=colors.BLUE, on_click=self.open_bs)
        self.popup = PopupMenuButton(
            items=[
                PopupMenuItem(
                    text="Show Database file in explorer",
                    on_click=self.show_db_file_in_file_browser,
                ),
                PopupMenuItem(text="Load Examples", on_click=self.load_examples),
                PopupMenuItem(text="Wipe DB", on_click=self.wipe_db),
            ],
            tooltip="Show options",
        )
        self.alert_dialog = AlertDialog(
            title=Text("Are you sure you wish to delete this?"),
            actions=[
                TextButton("Yes", on_click=self.delete_word_and_cleanup),
                TextButton("No", on_click=self.close_alert_dialog),
            ],
        )
        self._to_delete: Words | None = None

    def open_bs(self, _=None):
        self.bs.open = True
        self.bs.update()

    def close_bs(self, _=None):
        self.bs.open = False
        self.bs.update()

    def open_alert_dialog(self):
        self.alert_dialog.open = True
        self.alert_dialog.update()

    def close_alert_dialog(self, _=None):
        self.alert_dialog.open = False
        self.alert_dialog.update()

    @classmethod
    def default_app_dir_db(cls):
        """Creates an instance using the default"""
        # noinspection PyUnresolvedReferences
        cls.default_db_path.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Using file path `{cls.default_db_path}` for the database")
        # noinspection PyTypeChecker
        return DBPersistence.from_file(cls.default_db_path)

    def did_mount(self):
        self.page.floating_action_button = self.fab
        self.page.overlay.append(self.bs)
        self.page.dialog = self.alert_dialog
        self.page.add(self.fab, self.alert_dialog)

    # noinspection PyPropertyDefinition
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
                        self.popup,
                    ],
                    alignment=MainAxisAlignment.CENTER,
                ),
                self.word_display,
            ],
        )

    def update(self):
        self.word_display.update()
        super().update()

    def new_word(self, title: str, words: str, tags: set[str] = None):
        self.db.new_word(title, words, tags)
        self.close_bs()
        self.update()

    def show_db_file_in_file_browser(self, _):
        open_in_browser(f"file:///{self.default_db_path.parent}")

    def load_examples(self, _):
        import yaml

        example_file = Path(__file__).resolve(strict=True).parent / "examples.yaml"
        data = yaml.safe_load(example_file.read_text())
        for word in data.get("words"):
            match word:
                case {"title": title, "words": words, "tags": tags}:
                    # Using a bare except because we should only be eating SQLalchemy unique errors
                    # noinspection PyPep8
                    self.db.new_word(title, words, set(tags))
        self.update()

    def wipe_db(self, _):
        from wordspreader.ddl import Base

        Base.metadata.drop_all(self.db.engine)
        Base.metadata.create_all(self.db.engine)
        self.update()


_db = WordSpreader.default_app_dir_db()


def main(page: Page):
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(name)s [%(levelname)s]:%(message)s"
    )
    page.title = "Word Spreader"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    # create application instance
    app = WordSpreader(_db)
    # add application's root control to the page
    page.add(app)


flet.app(target=main)
