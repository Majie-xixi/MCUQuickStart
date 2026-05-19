"""Chip database: load chip definitions from JSON files."""
import json
from pathlib import Path


class ChipDatabase:
    def __init__(self, chips_dir: Path):
        self._chips_dir = chips_dir
        self._families: dict = {}

    def load(self):
        """Load all chip JSON files from chips directory."""
        for json_file in self._chips_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for family_name, family_data in data.items():
                self._families[family_name] = family_data

    def get_families(self) -> list[str]:
        """Return list of chip family names."""
        return list(self._families.keys())

    def get_family(self, family_name: str) -> dict:
        """Return full family definition."""
        return self._families.get(family_name, {})

    def get_chip(self, family_name: str, chip_name: str) -> dict | None:
        """Return chip config merged with family defaults."""
        family = self._families.get(family_name)
        if not family:
            return None
        chip = family.get("chips", {}).get(chip_name)
        if not chip:
            return None
        result = {k: v for k, v in family.items() if k not in ("chips",)}
        result.update(chip)
        result["name"] = chip_name
        return result

    def get_chips_for_family(self, family_name: str) -> list[str]:
        """Return list of chip names for a family."""
        family = self._families.get(family_name, {})
        return list(family.get("chips", {}).keys())
