# See prior message for full code (simple Redis queue abstraction)
# Place in src/queue/redis_queue.py
import redis
import json
import os
from typing import Dict, Any, Optional

class RedisQueue:
    def __init__(self, redis_url: Optional[str] = None, queue_name: str = "job_queue"):
        self.redis_url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        self.queue_name = queue_name
        self.redis = redis.Redis.from_url(self.redis_url)

    def enqueue(self, job: Dict[str, Any]) -> str:
        job_json = json.dumps(job)
        self.redis.rpush(self.queue_name, job_json)
        return job.get("job_id") or "unknown"

    def dequeue(self) -> Optional[Dict[str, Any]]:
        job_json = self.redis.blpop(self.queue_name, timeout=10)
        if job_json:
            _, job_str = job_json
            return json.loads(job_str)
        return None

    def queue_length(self) -> int:
        return self.redis.llen(self.queue_name)