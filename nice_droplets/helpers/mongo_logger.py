import logging
from typing import Optional, Dict, Any
import pymongo
from pymongo import MongoClient
import motor.motor_asyncio
import datetime

class MongoLogger:
    """
    MongoLogger provides both synchronous and asynchronous logging to a MongoDB collection.

    This logger supports standard logging methods (debug, info, warning, error, critical) and their async equivalents.
    It can log to both a standard Python logger and directly to MongoDB, using pymongo for sync and motor for async operations.
    
    It also allows you to specify extra filter keys for each log entry and to define MongoDB indexes for efficient querying.

    :param mongo_url: MongoDB connection string.
    :param db_name: Name of the MongoDB database.
    :param collection_name: Name of the MongoDB collection for logs.
    :param logger: Optional standard Python logger to also log to.
    :param index_keys: Optional list of keys (field names or pymongo index specs) to create an index on for filtering.
    :param default_keys: Optional dictionary of keys/values to add to every log entry (can be overridden per log call).
    :param ttl_seconds: Optional TTL in seconds for automatic log expiration (sets up a TTL index on 'timestamp').


    **Example usage:**

    .. code-block:: python

        from mongo_logger import MongoLogger
        logger = MongoLogger(
            mongo_url="mongodb://localhost:27017",
            db_name="mydb",
            collection_name="logs",
            index_keys=["email", "session_id"]
        )
        logger.info("User logged in", keys={"email": "user@example.com"})
        # Async logging
        await logger.info_async("Async event", keys={"email": "user@example.com"})

    **Features:**
        - Synchronous and asynchronous logging to MongoDB
        - Optional logging to a standard Python logger
        - Custom filter keys for each log message
        - Automatic index creation for efficient querying
        - Robust index creation logic for sync/async contexts
    """
    def __init__(self, 
                 mongo_url: str, 
                 db_name: str, 
                 collection_name: str, 
                 logger: Optional[logging.Logger] = None,
                 index_keys: Optional[list] = None,
                 default_keys: Optional[dict] = None,
                 ttl_seconds: Optional[int] = 30*24*60*60):
        self.logger = logger
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.collection_name = collection_name
        # Sync client (pymongo)
        self._sync_client = MongoClient(mongo_url)
        self._sync_collection = self._sync_client[db_name][collection_name]
        # Async client (motor)
        self._async_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        self._async_collection = self._async_client[db_name][collection_name]
        self.default_keys = default_keys or {}
        # If TTL is specified, create TTL index on 'timestamp'
        if ttl_seconds:
            self._sync_collection.create_index(
                "timestamp",
                expireAfterSeconds=ttl_seconds
            )
        else:
            self._sync_collection.create_index("timestamp")
        # Create index if specified
        if index_keys:
            # Accepts either a list of field names or pymongo index spec tuples
            if all(isinstance(k, str) for k in index_keys):
                pymongo_index = [(k, 1) for k in index_keys]
            else:
                pymongo_index = index_keys
            # Try async index creation if in an async context; otherwise fall back to sync
            async_index_created = False
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Try to create index asynchronously
                    task = loop.create_task(self._async_collection.create_index(pymongo_index))
                    # Optionally, wait for completion if in startup
                    loop.run_until_complete(asyncio.wait([task]))
                    async_index_created = True
            except Exception:
                async_index_created = False
            if not async_index_created:
                try:
                    self._sync_collection.create_index(pymongo_index)
                except Exception:
                    pass

    def _make_doc(self, level: str, msg: str, keys: Optional[Dict[str, Any]], **kwargs) -> dict:
        doc = {
            "level": level,
            "message": msg,
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
        }
        # Merge default_keys with keys, with keys taking precedence
        merged_keys = {**self.default_keys, **(keys or {})}
        if merged_keys:
            doc.update(merged_keys)
        if kwargs:
            doc["extra"] = kwargs
        return doc

    # --- Synchronous logging ---
    def debug(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Log a debug-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        self._log("DEBUG", msg, keys, **kwargs)

    def info(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Log an info-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        self._log("INFO", msg, keys, **kwargs)

    def warning(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Log a warning-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        self._log("WARNING", msg, keys, **kwargs)

    def error(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Log an error-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        self._log("ERROR", msg, keys, **kwargs)

    def critical(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Log a critical-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        self._log("CRITICAL", msg, keys, **kwargs)

    def _log(self, level, msg, keys, **kwargs):
        if self.logger:
            log_func = getattr(self.logger, level.lower(), self.logger.info)
            log_func(msg, extra={"keys": keys, **kwargs})
        doc = self._make_doc(level, msg, keys, **kwargs)
        self._sync_collection.insert_one(doc)

    # --- Asynchronous logging ---
    async def debug_async(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Asynchronously log a debug-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        await self._log_async("DEBUG", msg, keys, **kwargs)

    async def info_async(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Asynchronously log an info-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        await self._log_async("INFO", msg, keys, **kwargs)

    async def warning_async(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Asynchronously log a warning-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        await self._log_async("WARNING", msg, keys, **kwargs)

    async def error_async(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Asynchronously log an error-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        await self._log_async("ERROR", msg, keys, **kwargs)

    async def critical_async(self, msg, keys: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Asynchronously log a critical-level message to MongoDB (and standard logger if set).

        :param msg: The log message.
        :param keys: Optional dictionary of keys/values to attach to this log entry.
        :param kwargs: Additional data to include as 'extra'.
        """
        await self._log_async("CRITICAL", msg, keys, **kwargs)

    async def _log_async(self, level, msg, keys, **kwargs):
        if self.logger:
            log_func = getattr(self.logger, level.lower(), self.logger.info)
            log_func(msg, extra={"keys": keys, **kwargs})
        doc = self._make_doc(level, msg, keys, **kwargs)
        await self._async_collection.insert_one(doc)        

    def get_collection(self) -> pymongo.collection.Collection:
        return self._sync_collection

    def get_async_collection(self) -> motor.motor_asyncio.AsyncIOMotorCollection:
        return self._async_collection

    def fetch_recent_messages(self, *, timespan_seconds: int | None = None, filters: Optional[dict] = None, limit: int = 50, fields: Optional[list] = None,
        add_filter: Optional[dict] = None):
        """
        Fetch recent log messages synchronously within the given timespan (in seconds), with optional additional filters.
        Results are sorted by timestamp descending.

        :param timespan_seconds: Number of seconds to look back from now (UTC). 30 days by default.
        :param filters: Optional additional MongoDB filter dictionary.
        :param limit: Maximum number of results to return.
        :param fields: List of fields to return (default: ["timestamp", "message"]).
        :param add_filter: Optional additional MongoDB filter dictionary.
        :return: List of log documents.
        """
        if timespan_seconds is None:  # 365 days
            timespan_seconds = 365*24*60*60
        from datetime import datetime, timezone, timedelta
        query = filters.copy() if filters else {}
        now = datetime.now(timezone.utc)
        earliest = now - timedelta(seconds=timespan_seconds)
        query["timestamp"] = {"$gte": earliest}
        projection = {field: 1 for field in (fields or ["timestamp", "message"])}
        projection["_id"] = 0
        if add_filter:
            query.update(add_filter)
        cursor = self._sync_collection.find(query, projection).sort("timestamp", -1).limit(limit)
        return list(cursor)

    async def fetch_recent_messages_async(self, *, timespan_seconds: int | None = None, filters: Optional[dict] = None, limit: int = 50, fields: Optional[list] = None,
        add_filter: Optional[dict] = None):
        """
        Fetch recent log messages asynchronously within the given timespan (in seconds), with optional additional filters.
        Results are sorted by timestamp descending.

        :param timespan_seconds: Number of seconds to look back from now (UTC).
        :param filters: Optional additional MongoDB filter dictionary.
        :param limit: Maximum number of results to return.
        :param fields: List of fields to return (default: ["timestamp", "message"]).
        :param add_filter: Optional additional MongoDB filter dictionary.
        :return: List of log documents.
        """
        if timespan_seconds is None:  # 365 days
            timespan_seconds = 365*24*60*60
        from datetime import datetime, timezone, timedelta
        query = filters.copy() if filters else {}
        now = datetime.now(timezone.utc)
        earliest = now - timedelta(seconds=timespan_seconds)
        query["timestamp"] = {"$gte": earliest}
        projection = {field: 1 for field in (fields or ["timestamp", "message"])}
        projection["_id"] = 0
        if add_filter:
            query.update(add_filter)
        cursor = self._async_collection.find(query, projection).sort("timestamp", -1).limit(limit)
        return [doc async for doc in cursor]