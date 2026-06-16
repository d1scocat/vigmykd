from pathlib import Path
from typing import Any

import json


_LocValue = dict[str, 'str | _LocValue']


class Localization:
    def __init__(self, directory: Path, default: str):
        self._i18n: dict[str, dict[str, str]] = {}

        for loc_path in directory.glob("*.json"):
            data: dict[str, _LocValue] = json.loads(loc_path.read_text())

            loc_id = data.get("_id")
            if not isinstance(loc_id, str):
                raise ValueError("A i18n file must contain a _id string "
                                 f"value and {loc_path} doesn't")

            self._i18n[loc_id] = self._resolve_data(loc_id, {
                k: v for k, v in data.items() if k != "_id"
            })

        if default not in self._i18n:
            raise ValueError(f"Default locale '{default}' not found")
        self.default = default

    def t(self, loc: str, key: str, strict: bool = False, **kwargs) -> str:
        """
        Resolve a localized string by key for a given locale.

        Looks up the translation identified by `key` in the specified `loc`.
        If the key is not found:
        - raises a ValueError if `strict` is True
        - otherwise falls back to the default locale

        The resulting string is formatted using `str.format(**kwargs)`.

        Args:
            loc: Locale identifier (e.g. "en", "ru").
            key: Flattened translation key (e.g. "main-menu.login-button-label").
            strict: If True, do not fall back to the default locale.
            **kwargs: Values used to format the string.

        Returns:
            The formatted localized string.

        Raises:
            ValueError: If the key is missing in `loc` and `strict` is True,
                        or if required formatting placeholders are missing.
            KeyError: If the key is missing in both `loc` and the default locale.
        """
        if key in self._i18n.get(loc, {}):
            value = self._i18n[loc][key]
        else:
            if strict:
                raise ValueError(f"No key {key} in localization {loc}")

            try:
                value = self._i18n[self.default][key]
            except KeyError:
                raise KeyError(f"Missing key '{key}' in default locale ('{self.default}')")

        try:
            return value.format(**kwargs)
        except KeyError as ex:
            placeholder = ex.args[0]
            raise ValueError(f"Missing placeholder '{placeholder}' in key '{key}' ({loc})")

    def _resolve_data(
        self,
        holder_id: str,
        data: dict[str, Any],
        parent: str = ""
    ) -> dict[str, str]:
        result: dict[str, str] = {}

        for key, value in data.items():
            full_key = parent + key

            if isinstance(value, str):
                if full_key in result:
                    raise ValueError(f"Duplicate i18n key in {holder_id}: {full_key}")
                result[full_key] = value
            elif isinstance(value, dict):
                nested = self._resolve_data(holder_id, value, f"{full_key}.")
                for k, v in nested.items():
                    if k in result:
                        raise ValueError(f"Duplicate i18n key in {holder_id}: '{k}'")
                    result[k] = v
            else:
                raise TypeError(f"Invalid value type in {holder_id} at {full_key}: {type(value)}")

        return result
