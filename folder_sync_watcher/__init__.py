from .config import SyncConfig
from .hashing import FileHasher
from .paths import FilePathManager
from .subst import SubstManager

__all__ = [
    "SyncConfig",
    "FileHasher",
    "FilePathManager",
    "SubstManager",
    "FolderSyncWatcher",
    "SyncHandler",
]


def __getattr__(name: str):
    if name in {"FolderSyncWatcher", "SyncHandler"}:
        from .watcher import FolderSyncWatcher, SyncHandler

        return {"FolderSyncWatcher": FolderSyncWatcher, "SyncHandler": SyncHandler}[name]
    raise AttributeError(name)
