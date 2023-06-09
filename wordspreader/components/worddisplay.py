import logging

from flet_core import (
    Column,
    ControlEvent,
    Tab,
    Tabs,
    UserControl,
)

from wordspreader.components import Words
from wordspreader.ddl import Word
from wordspreader.persistence import DBPersistence


# noinspection PyAttributeOutsideInit
class WordDisplay(UserControl):
    log = logging.getLogger("WordDisplay")

    def __init__(self, db: DBPersistence, edit_word: callable, delete_word: callable):
        super().__init__()
        self.db = db
        self._edit_callback = edit_word
        self._delete_callback = delete_word

    def build(self):
        self.keywords = Tabs(on_change=self.filter_changed, tabs=self._build_keywords())
        self.words = Column(controls=self._build_all_words())

        return Column([self.keywords, self.words])

    def filter_changed(self, _: ControlEvent):
        self._set_visibility_for_filter()
        super().update()

    def _set_visibility_for_filter(self):
        match self.keywords.tabs[self.keywords.selected_index].text:
            case "all":
                for word in self.words.controls:
                    word.visible = True
            case str() as s:
                for word in self.words.controls:
                    word.visible = s in word.tags

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
                self._edit_callback,
                self._delete_callback,
            )
            for word in self.db.get_words_filtered()
        ]

    @staticmethod
    def _keyword_key(element: Tab):
        match element:
            case "all":
                return 0, Tab.text
            case _:
                return 1, Tab.text

    def _sort_keywords(self):
        self.keywords.tabs.sort(key=WordDisplay._keyword_key)

    def update(self):
        self._update_tags()
        self._update_words()
        super().update()

    def _update_tags(self) -> bool:
        ui_tags = {t.text for t in self.keywords.tabs}
        db_tags = set(self.db.get_all_tags())
        # If either side has something the other side doesn't
        if ui_tags.symmetric_difference(db_tags):
            self.log.debug("Found a difference in tags, updating.")
            old_key = self.keywords.tabs[self.keywords.selected_index].text
            self.keywords.tabs = self._build_keywords()
            self._sort_keywords()
            new_kws = {t.text for t in self.keywords.tabs}
            if old_key in new_kws:
                self.keywords.selected_index = list(new_kws).index(old_key)
            else:
                # If we don't have that keyword anymore, we are going to just go to All
                self.keywords.selected_index = 0
            self.keywords.update()
            return True
        return False

    def _update_words(self) -> bool:
        # Do we have all of the keywords and words that exist?
        ui_words = {w.title: w for w in self.words.controls}
        db_words = {w.name: w for w in self.db.get_words_filtered()}
        # If either side has something the other side doesn't
        if set(ui_words.keys()).symmetric_difference(db_words.keys()):
            self.log.debug("Found an obvious difference in words, updating.")
            self.words.controls = self._build_all_words()
            self.words.update()
            return True
        # Are our instances up to date?
        for word_control in self.words.controls:
            db_word: Word = db_words[word_control.title]
            wc: Words = word_control
            if wc.words != db_word.content:
                wc.words = db_word.content
            if set(wc.tags) != db_word.tags:
                wc.tags = db_word.tags

        return False
