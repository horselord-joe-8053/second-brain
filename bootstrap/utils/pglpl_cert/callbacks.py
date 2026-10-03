"""Injectable callbacks for admin and CLI word-loop runners."""

from __future__ import annotations

from typing import Any, Callable, Protocol  # Any for db session typing in bind helpers

from utils.pglpl_cert.word_loop.core import TaggedSnapshot

GenerateTaggedFn = Callable[[str, list[int], int], list[TaggedSnapshot]]
DoorCOnTaggedFn = Callable[[list[TaggedSnapshot], int], dict[str, Any]]


class PersistDoorCStatusFn(Protocol):
    def __call__(self, tagged: list[TaggedSnapshot], door_c_result: dict[str, Any]) -> dict[str, int]: ...


def gender_persist_door_c_status(db: Any) -> PersistDoorCStatusFn:
    """Bind admin session persist for gender/glossary Door C results."""

    def _persist(tagged: list[TaggedSnapshot], door_c_result: dict[str, Any]) -> dict[str, int]:
        from app.services.paragraph_harness.door_c import persist_gender_door_c_tagged

        n_pass, n_fail = persist_gender_door_c_tagged(
            db, tagged, door_c_result, enqueue_aids=False
        )
        return {"door_c_pass": n_pass, "door_c_fail": n_fail}

    return _persist
