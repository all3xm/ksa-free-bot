from __future__ import annotations

import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any


class JsonStorage:
    """Small local JSON store for birthdays and polls."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.RLock()
        self._data: dict[str, Any] = {"birthdays": {}, "polls": {}}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Could not read {self.path.name}. Fix or remove the damaged file.") from error
        if not isinstance(loaded, dict):
            raise RuntimeError(f"{self.path.name} does not contain valid bot data.")
        self._data["birthdays"] = loaded.get("birthdays", {})
        self._data["polls"] = loaded.get("polls", {})

    def _save(self) -> None:
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary.replace(self.path)

    @staticmethod
    def _birthday_key(guild_id: int, user_id: int) -> str:
        return f"{guild_id}:{user_id}"

    def set_birthday(self, guild_id: int, user_id: int, month: int, day: int) -> None:
        with self._lock:
            self._data["birthdays"][self._birthday_key(guild_id, user_id)] = {
                "month": month,
                "day": day,
            }
            self._save()

    def get_birthday(self, guild_id: int, user_id: int) -> dict[str, int] | None:
        with self._lock:
            value = self._data["birthdays"].get(self._birthday_key(guild_id, user_id))
            return deepcopy(value) if value else None

    def create_poll(
        self,
        message_id: int,
        guild_id: int,
        channel_id: int,
        creator_id: int,
        question: str,
        options: list[str],
    ) -> None:
        with self._lock:
            self._data["polls"][str(message_id)] = {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "creator_id": creator_id,
                "question": question,
                "options": options,
                "votes": {},
                "ended": False,
            }
            self._save()

    def get_poll(self, message_id: int) -> dict[str, Any] | None:
        with self._lock:
            poll = self._data["polls"].get(str(message_id))
            return deepcopy(poll) if poll else None

    def active_polls(self) -> list[tuple[int, dict[str, Any]]]:
        with self._lock:
            return [
                (int(message_id), deepcopy(poll))
                for message_id, poll in self._data["polls"].items()
                if not poll.get("ended", False)
            ]

    def vote(self, message_id: int, user_id: int, option_index: int) -> dict[str, Any] | None:
        with self._lock:
            poll = self._data["polls"].get(str(message_id))
            if not poll or poll.get("ended", False):
                return None
            if not 0 <= option_index < len(poll["options"]):
                return None
            poll["votes"][str(user_id)] = option_index
            self._save()
            return deepcopy(poll)

    def end_poll(self, message_id: int) -> dict[str, Any] | None:
        with self._lock:
            poll = self._data["polls"].get(str(message_id))
            if not poll or poll.get("ended", False):
                return None
            poll["ended"] = True
            self._save()
            return deepcopy(poll)
