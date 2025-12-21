from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

# ═══════════════════════════════════  generic helpers ══════════════════════════


def _dig(doc: Optional[Dict[str, Any]],
         path: Iterable[str],
         default: Any) -> Any:
    """
    Traverse a nested dictionary along *path*.
    Return *default* if the path cannot be resolved.
    """
    if doc is None:
        return default
    cur: Any = doc
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def _selector_cache_key(selector: Dict[str, Any]) -> str:
    """
    Turn an arbitrary selector dict into a stable, deterministic string.
    Used by RedisConfig to build a flat key.
    """
    # Sort keys for determinism
    return ",".join(f"{k}={selector[k]}" for k in sorted(selector))


# ═══════════════════════════════════  key tokenizer ════════════════════════════
class _Tokens:
    """
    Split a config key into its logical parts.

      <collection>:<doc_id>[:nested:field]      → generic/global key
      $<placeholder>[:nested:field]             → user-scoped key
    """

    def __init__(self, raw: str) -> None:
        parts = raw.split(":")
        if not parts:
            raise ValueError("empty key")
        self.is_user = parts[0].startswith("$")

        if self.is_user:
            self.placeholder: str = parts[0][1:]
            self.path: List[str] = parts[1:]
        else:
            if len(parts) < 2:
                raise ValueError("generic key needs <collection>:<doc_id>")
            self.collection: str = parts[0]
            self.doc_id: str = parts[1]
            self.path: List[str] = parts[2:]


# ═══════════════════════════════════  shared base ══════════════════════════════
@dataclass
class _UserPlaceholder:
    collection: str               # e.g. "lechler_ai.users"
    identifier: Dict[str, Any]    # e.g. {"email": "..."}  – selector dict


from abc import ABC, abstractmethod
import asyncio

class ConfigInterface(ABC):
    """
    Shared parent that exposes:

        • add_user_key()
        • set()
        • get()

    Subclasses **only** implement the two primitive DB operations
    `_set_value()` and `_get_value()`.
    """

    # ---------------------------------------------------------------- init
    def __init__(self) -> None:
        self._users: Dict[str, _UserPlaceholder] = {}

    # ---------------------------------------------------- register user token
    def add_user_key(self,
                     placeholder: str,
                     *,
                     collection: str,
                     identifier: Dict[str, Any]) -> None:
        """
        Register a `$placeholder` that maps to a single user document.

        Parameters
        ----------
        placeholder : "foo"  → used in keys as "$foo"
        collection  : "<db.collection>" where that user document lives
        identifier  : selector dict that matches (only) that user document
        """
        self._users[placeholder.lstrip("$")] = _UserPlaceholder(
            collection, identifier
        )

    # ---------------------------------------------------------------- public
    def set(self, key: str, value: Any) -> None:
        """Create or overwrite *value*."""
        t = _Tokens(key)

        if t.is_user:                                      # user-scoped
            up = self._users.get(t.placeholder)
            if up is None:
                raise KeyError(f"Unknown user placeholder ${t.placeholder}")
            self._set_value(up.collection, up.identifier, t.path, value)
        else:                                              # generic/global
            self._set_value(t.collection, {"_id": t.doc_id}, t.path, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Read a value, or *default* if not present."""
        t = _Tokens(key)

        if t.is_user:
            up = self._users.get(t.placeholder)
            if up is None:
                raise KeyError(f"Unknown user placeholder ${t.placeholder}")
            return self._get_value(up.collection, up.identifier, t.path, default)
        else:
            return self._get_value(t.collection, {"_id": t.doc_id}, t.path, default)

    # ------------------------------------------------------------- primitives
    @abstractmethod
    def _set_value(self,
                   collection: str,
                   selector: Dict[str, Any],
                   path: Iterable[str],
                   value: Any) -> None:
        ...

    @abstractmethod
    def _get_value(self,
                   collection: str,
                   selector: Dict[str, Any],
                   path: Iterable[str],
                   default: Any = None) -> Any:
        ...

    # ------------------------------------------------------------- async primitives
    async def async_set(self, key: str, value: Any) -> None:
        t = _Tokens(key)
        if t.is_user:
            up = self._users.get(t.placeholder)
            if up is None:
                raise KeyError(f"Unknown user placeholder ${t.placeholder}")
            await self._set_value_async(up.collection, up.identifier, t.path, value)
        else:
            await self._set_value_async(t.collection, {"_id": t.doc_id}, t.path, value)

    async def async_get(self, key: str, default: Any = None) -> Any:
        t = _Tokens(key)
        if t.is_user:
            up = self._users.get(t.placeholder)
            if up is None:
                raise KeyError(f"Unknown user placeholder ${t.placeholder}")
            return await self._get_value_async(up.collection, up.identifier, t.path, default)
        else:
            return await self._get_value_async(t.collection, {"_id": t.doc_id}, t.path, default)

    @abstractmethod
    async def _set_value_async(self,
                              collection: str,
                              selector: Dict[str, Any],
                              path: Iterable[str],
                              value: Any) -> None:
        raise NotImplementedError("Async set not implemented for this backend.")

    @abstractmethod
    async def _get_value_async(self,
                              collection: str,
                              selector: Dict[str, Any],
                              path: Iterable[str],
                              default: Any = None) -> Any:
        raise NotImplementedError("Async get not implemented for this backend.")



# ═══════════════════════════════════  Mongo implementation ════════════════════
from pymongo import MongoClient


# For async Mongo support
try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    AsyncIOMotorClient = None

class MongoConfig(ConfigInterface):
    """
    MongoDB backend: one database, many collections.

    • *collection*   → collection inside the chosen DB
    • *selector*     → dict used directly in find_one()/update_one()
    • *path*         → list of nested field tokens
    """

    def __init__(self,
                 mongo_uri: str,
                 mongo_db: str) -> None:
        super().__init__()
        self._db = MongoClient(mongo_uri)[mongo_db]
        if AsyncIOMotorClient is not None:
            self._db_async = AsyncIOMotorClient(mongo_uri)[mongo_db]
        else:
            self._db_async = None

    # ───────────────────────── helper
    def _coll(self, name: str) -> str:
        """
        Normalize collection name: drop '<db>.' prefix if the caller supplied it.
        """
        return name.split(".", 1)[-1]

    # ───────────────────────── primitives
    def _set_value(self,
                   collection: str,
                   selector: Dict[str, Any],
                   path: Iterable[str],
                   value: Any) -> None:
        coll = self._db[self._coll(collection)]
        path = list(path)
        update = {"$set": {".".join(path): value}} if path else {"$set": value}
        coll.update_one(selector, update, upsert=True)

    def _get_value(self,
                   collection: str,
                   selector: Dict[str, Any],
                   path: Iterable[str],
                   default: Any = None) -> Any:
        coll = self._db[self._coll(collection)]
        doc = coll.find_one(selector, projection={"_id": 0})
        return _dig(doc, path, default)

    async def _set_value_async(self,
                              collection: str,
                              selector: Dict[str, Any],
                              path: Iterable[str],
                              value: Any) -> None:
        if self._db_async is None:
            raise NotImplementedError("Async Mongo support is not enabled (motor not installed).")
        coll = self._db_async[self._coll(collection)]
        path = list(path)
        update = {"$set": {".".join(path): value}} if path else {"$set": value}
        await coll.update_one(selector, update, upsert=True)

    async def _get_value_async(self,
                              collection: str,
                              selector: Dict[str, Any],
                              path: Iterable[str],
                              default: Any = None) -> Any:
        if self._db_async is None:
            raise NotImplementedError("Async Mongo support is not enabled (motor not installed).")
        coll = self._db_async[self._coll(collection)]
        doc = await coll.find_one(selector, projection={"_id": 0})
        return _dig(doc, path, default)



# ═══════════════════════════════════  Redis implementation ════════════════════
try:
    import redis  # type: ignore
except ImportError:  # pragma: no cover – Redis is optional
    redis = None


# For async Redis support
try:
    import aioredis
except ImportError:
    aioredis = None

class RedisConfig(ConfigInterface):
    """
    Redis backend: every *leaf* value is stored as one flat key.

    Key format:
        <prefix>:<collection>:<selector-string>[:a][:b][:c]
    """

    def __init__(self,
                 redis_uri: str,
                 prefix: str = "cfg") -> None:
        if redis is None:
            raise ImportError("pip install redis")
        super().__init__()
        self._r = redis.from_url(redis_uri, decode_responses=True)
        self._prefix = prefix.rstrip(":")
        if aioredis is not None:
            # Use the same connection string as for sync
            self._r_async = aioredis.from_url(redis_uri, decode_responses=True)
        else:
            self._r_async = None

    # -------------------------------------------- helper
    def _build_key(self,
                   collection: str,
                   selector: Dict[str, Any],
                   path: Iterable[str]) -> str:
        sel_part = _selector_cache_key(selector)
        return ":".join([self._prefix, collection, sel_part, *path])

    # -------------------------------------------- required primitives
    def _set_value(self,
                   collection: str,
                   selector: Dict[str, Any],
                   path: Iterable[str],
                   value: Any) -> None:
        key = self._build_key(collection, selector, path)
        self._r.set(key, json.dumps(value))

    def _get_value(self,
                   collection: str,
                   selector: Dict[str, Any],
                   path: Iterable[str],
                   default: Any = None) -> Any:
        key = self._build_key(collection, selector, path)
        raw = self._r.get(key)
        return default if raw is None else json.loads(raw)

    async def _set_value_async(self,
                              collection: str,
                              selector: Dict[str, Any],
                              path: Iterable[str],
                              value: Any) -> None:
        if self._r_async is None:
            raise NotImplementedError("Async Redis support is not enabled (aioredis not installed).");
        key = self._build_key(collection, selector, path)
        await self._r_async.set(key, json.dumps(value))

    async def _get_value_async(self,
                              collection: str,
                              selector: Dict[str, Any],
                              path: Iterable[str],
                              default: Any = None) -> Any:
        if self._r_async is None:
            raise NotImplementedError("Async Redis support is not enabled (aioredis not installed).");
        key = self._build_key(collection, selector, path)
        raw = await self._r_async.get(key)
        return default if raw is None else json.loads(raw)

# ═══════════════════════════════════  demonstration ═══════════════════════════
if __name__ == "__main__":
    import asyncio
    # Mongo demo – requires a local MongoDB
    mongo_cfg = MongoConfig("mongodb://localhost:27017", "demo_db")
    mongo_cfg_async = MongoConfig("mongodb://localhost:27017", "demo_db")

    mongo_cfg.set("global_config:ui:default_language", "English")
    print("Mongo generic:",
          mongo_cfg.get("global_config:ui:default_language"))

    mongo_cfg.add_user_key(
        "demo_user",
        collection="demo.users",
        identifier={"email": "alice.smith@example.com"}
    )
    mongo_cfg.set("$demo_user:licenses:demoAssistant", 18)
    mongo_cfg.set("$demo_user:plugins:orderAssistant:enabled", True)
    print("Mongo user:",
          mongo_cfg.get("$demo_user:licenses:demoAssistant", 19))
    print("Mongo user:",
          mongo_cfg.get("$demo_user:plugins:orderAssistant:enabled", False))

    # ASYNC TESTS
    async def async_tests():
        # Global key (different from sync)
        await mongo_cfg_async.async_set("global_config:ui:async_language", "German")
        val = await mongo_cfg_async.async_get("global_config:ui:async_language")
        print("Mongo async generic:", val)

        # User key (different from sync)
        mongo_cfg_async.add_user_key(
            "async_user",
            collection="demo.users",
            identifier={"email": "bob.async@example.com"}
        )
        await mongo_cfg_async.async_set("$async_user:licenses:asyncAssistant", 23)
        val2 = await mongo_cfg_async.async_get("$async_user:licenses:asyncAssistant", 25)
        print("Mongo async user:", val2)

    asyncio.run(async_tests())

    # Redis demo – uncomment if you have Redis
    # redis_cfg = RedisConfig("redis://localhost:6379/0")
    # redis_cfg.set("branding:main:bg_color", "#004B83")
    # print("Redis generic:",
    #       redis_cfg.get("branding:main:bg_color"))
