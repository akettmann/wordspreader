from functools import partial

from flet_core import (
    Column,
    ControlEvent,
    Tab,
    Tabs,
    UserControl,
)

from wordspreader.components import Words
from wordspreader.persistence import DBPersistence


# noinspection PyAttributeOutsideInit
class WordDisplay(UserControl):
    def __init__(self, db: DBPersistence, edit_word: callable):
        super().__init__()
        self.db = db
        self.edit_word = edit_word

    def build(self):
        self.keywords = Tabs(on_change=self.filter_changed, tabs=self._build_keywords())
        self.words = Column(controls=self._build_all_words())

        return Column([self.keywords, self.words])

    def delete_words(self, words: Words):
        self.db.delete_word(words.title)
        self.words.controls.remove(words)
        self.update()

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
                self.edit_word,
                self.delete_words,
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
        self.keywords.update()

    def update(self):
        current_tags = {t.text for t in self.keywords.tabs}
        all_tags_from_db = set(self.db.get_all_tags())
        if _ := all_tags_from_db - current_tags:
            self.keywords.tabs = self._build_keywords()
            self.keywords.update()
        all_word_names_from_db = {w.name for w in self.db.get_words_filtered()}
        current_word_names = {w.title for w in self.words.controls[1:]}
        if _ := all_word_names_from_db - current_word_names:
            self.words.controls = self._build_all_words()
            self.words.update()
        self._sort_keywords()
        super().update()
