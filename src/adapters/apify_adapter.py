from apify import Actor
from .base import PlatformAdapter

class ApifyAdapter(PlatformAdapter):
    async def get_input(self):
        return await Actor.get_input()

    async def push_data(self, data):
        await Actor.push_data(data)

    def log_info(self, msg):
        Actor.log.info(msg)

    async def fail(self, status_message, exception=None):
        await Actor.fail(status_message=status_message, exception=exception)