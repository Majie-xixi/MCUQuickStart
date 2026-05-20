"""Simple i18n: load JSON translation files, format with **kwargs."""
import json
from pathlib import Path


class I18n:
    def __init__(self, i18n_dir: Path):
        self._dir = i18n_dir
        self._strings: dict = {}
        self._lang = "en"

    def set_language(self, lang: str):
        self._lang = lang
        file = self._dir / f"{lang}.json"
        if file.exists():
            self._strings = json.loads(file.read_text(encoding="utf-8"))

    def get(self, key: str, **kwargs) -> str:
        text = self._strings.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text

    @property
    def language(self) -> str:
        return self._lang
