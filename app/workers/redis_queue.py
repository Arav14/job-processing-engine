import redis
import json


class RedisJobQueue:
    def __int__(self):
        self.redis = redis.Redis(
            host="localhost", port=6379, decode_responses=True)
        self.queue_name = "job_queue"

    def add_job(self, job_id: str):
        self.redis.rpush(self.queue_name, job_id)

    def get_job(self):
        job = self.redis.lpop(self.queue_name)
        return job

    def is_empty(self):
        return self.redis.llen(self.queue_name) == 0
