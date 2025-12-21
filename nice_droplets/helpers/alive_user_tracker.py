from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List, Optional

class AliveUserTracker:
    """
    Helper for tracking 'alive' users in Redis with time-bucketed keys.
    The time source is always the Redis server.
    """
    def __init__(self, redis_client, base_key_name: str|list, min_alive_interval: float = 30.0):
        self._redis_client = redis_client
        if isinstance(base_key_name, str):
            self._base_key_names = [base_key_name]
        elif isinstance(base_key_name, list):
            self._base_key_names = base_key_name
        else:
            raise ValueError("base_key_name must be a string or a list of strings")
        self._min_alive_interval = min_alive_interval

    @property
    def base_key_name_for_write(self):
        return self._base_key_names[0]

    @property
    def base_key_names_for_read(self):
        return self._base_key_names

    async def mark_alive(self, user_id: str, add_info: str|None = None):
        """
        Mark a user as alive. Uses Redis server time to bucket by minute.
        Only writes to the first base_key_name.
        """
        redis_server_time = (await self._redis_client.time())[0]
        utc_time = datetime.fromtimestamp(redis_server_time, tz=ZoneInfo("UTC"))
        redis_server_time_str = utc_time.strftime("%Y_%m_%d_%H_%M")
        redis_server_time_str_seconds = utc_time.strftime("%Y_%m_%d_%H_%M_%S")
        base_key = self._base_key_names[0]
        key = f"{base_key}:alive:{user_id}"
        all_alive_key = f"{base_key}:alive_all_{redis_server_time_str}"
        pipe = self._redis_client.pipeline()
        pipe.setex(key, int(self._min_alive_interval*2), redis_server_time_str_seconds)
        if add_info:
            pipe.setex(f"{key}:info", int(self._min_alive_interval*2), add_info)
        pipe.sadd(all_alive_key, user_id)
        pipe.expire(all_alive_key, 60)
        await pipe.execute()

    async def is_alive(self, user_id: str) -> bool:
        """
        Check if a user is alive (has a non-expired key) in any of the base_key_names.
        """
        for base_key in self.base_key_names_for_read:
            key = f"{base_key}:alive:{user_id}"
            if await self._redis_client.exists(key) > 0:
                return True
        return False

    async def get_alive_users(self) -> List[str]:
        """
        Get all users alive in the last 60 seconds (current and previous minute) from all base_key_names.
        """
        redis_server_time = (await self._redis_client.time())[0]
        utc_time = datetime.fromtimestamp(redis_server_time, tz=ZoneInfo("UTC"))
        cur_minute_str = utc_time.strftime("%Y_%m_%d_%H_%M")
        prev_minute = utc_time.replace(second=0) - timedelta(minutes=1)
        prev_minute_str = prev_minute.strftime("%Y_%m_%d_%H_%M")
        users = set()
        for base_key in self.base_key_names_for_read:
            cur_key = f"{base_key}:alive_all_{cur_minute_str}"
            prev_key = f"{base_key}:alive_all_{prev_minute_str}"
            cur_key_members = await self._redis_client.smembers(cur_key) or []
            users.update([str(user, 'utf-8') for user in cur_key_members])
            prev_key_members = await self._redis_client.smembers(prev_key) or []
            users.update([str(user, 'utf-8') for user in prev_key_members])
        return list(users)

    async def get_add_info(self, user_id: str):
        """
        Fetches the add_info JSON for a user from all base_key_names, returning the first non-null value.
        Returns the parsed JSON object or None if not found.
        """
        import json
        for base_key in getattr(self, '_base_key_names', [getattr(self, '_base_key_name', None)]):
            if base_key:
                key = f"{base_key}:alive:{user_id}:info"
                add_info_val = await self._redis_client.get(key)
                if add_info_val:
                    try:
                        return json.loads(add_info_val.decode('utf-8') if isinstance(add_info_val, bytes) else str(add_info_val))
                    except Exception:
                        continue
        return None

    async def get_last_seen_times(self) -> dict:
        """
        Get a mapping of user_id -> last seen timestamp (from alive key value) for all alive users from all base_key_names.
        """
        user_ids = await self.get_alive_users()
        if not user_ids:
            return {}
        pipe = self._redis_client.pipeline()
        key_map = {}
        for user_id in user_ids:
            # Try all base keys for each user, prefer first that returns a value
            for base_key in self.base_key_names_for_read:
                key = f"{base_key}:alive:{user_id}"
                key_map[(user_id, base_key)] = pipe.get(key)
        results = await pipe.execute()
        # Map user_id -> last non-None value found
        user_last_seen = {user_id: None for user_id in user_ids}
        for ((user_id, base_key), val) in zip(key_map.keys(), results):
            if val and user_last_seen[user_id] is None:
                user_last_seen[user_id] = val.decode('utf-8') if isinstance(val, bytes) else str(val)
        return user_last_seen
