import pytest
import asyncio
from nice_droplets.helpers.mongo_logger import MongoLogger
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_mongo_logger"
COLLECTION_NAME = "logs"


def mongo_available():
    """Check if MongoDB is available."""
    try:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=1000)
        client.admin.command('ping')
        return True
    except ServerSelectionTimeoutError:
        return False


pytestmark = pytest.mark.skipif(
    not mongo_available(),
    reason="MongoDB not available at localhost:27017"
)


@pytest.fixture(autouse=True)
def cleanup():
    # Cleanup before each test
    client = MongoClient(MONGO_URL)
    client[DB_NAME][COLLECTION_NAME].delete_many({})
    yield
    # Drop the collection after each test
    client[DB_NAME].drop_collection(COLLECTION_NAME)


def test_sync_logging():
    logger = MongoLogger(MONGO_URL, DB_NAME, COLLECTION_NAME, index_keys=["email"])
    logger.info("sync test", keys={"email": "user@domain.com"})
    client = MongoClient(MONGO_URL)
    doc = client[DB_NAME][COLLECTION_NAME].find_one({"email": "user@domain.com"})
    assert doc is not None
    assert doc["message"] == "sync test"
    assert doc["level"] == "INFO"

@pytest.mark.asyncio
def test_async_logging():
    logger = MongoLogger(MONGO_URL, DB_NAME, COLLECTION_NAME, index_keys=["email"])
    async def run():
        await logger.info_async("async test", keys={"email": "async@domain.com"})
    asyncio.get_event_loop().run_until_complete(run())
    client = MongoClient(MONGO_URL)
    doc = client[DB_NAME][COLLECTION_NAME].find_one({"email": "async@domain.com"})
    assert doc is not None
    assert doc["message"] == "async test"
    assert doc["level"] == "INFO"


def test_fetch_recent_messages():
    logger = MongoLogger(MONGO_URL, DB_NAME, COLLECTION_NAME)
    logger.info("recent 1", keys={"tag": "a"})
    logger.info("recent 2", keys={"tag": "b"})
    # Should fetch both, most recent first
    results = logger.fetch_recent_messages(timespan_seconds=60, limit=2)
    assert len(results) == 2
    assert results[0]["message"].startswith("recent")
    # Test filter
    filtered = logger.fetch_recent_messages(timespan_seconds=60, filters={"tag": "a"}, limit=2)
    assert any(doc["message"] == "recent 1" for doc in filtered)
    # Test fields
    fields = logger.fetch_recent_messages(timespan_seconds=60, fields=["message"], limit=1)
    assert "message" in fields[0]
    assert "timestamp" not in fields[0]


@pytest.mark.asyncio
async def test_fetch_recent_messages_async():
    logger = MongoLogger(MONGO_URL, DB_NAME, COLLECTION_NAME)
    await logger.info_async("async recent 1", keys={"tag": "async-a"})
    await logger.info_async("async recent 2", keys={"tag": "async-b"})
    # Should fetch both, most recent first
    results = await logger.fetch_recent_messages_async(timespan_seconds=60, limit=2)
    assert len(results) == 2
    assert results[0]["message"].startswith("async recent")
    # Test filter
    filtered = await logger.fetch_recent_messages_async(timespan_seconds=60, filters={"tag": "async-a"}, limit=2)
    assert any(doc["message"] == "async recent 1" for doc in filtered)
    # Test fields
    fields = await logger.fetch_recent_messages_async(timespan_seconds=60, fields=["message"], limit=1)
    assert "message" in fields[0]
    assert "timestamp" not in fields[0]
