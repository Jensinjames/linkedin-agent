from apify import Actor
from .base import PlatformAdapter

class ApifyAdapter(PlatformAdapter):
    async def get_input(self):
        return await Actor.get_input()

    async def push_data(self, data):
        await Actor.push_data(data)

    def log_info(self, msg):
        """
        Logs an informational message to the Apify platform.
        """
        Actor.log.info(msg)

    async def fail(self, status_message, exception=None):
        """
        Signal a failure to the Apify platform with a status message and optional exception.
        
        Parameters:
            status_message (str): Description of the failure.
            exception (Exception, optional): Exception object providing additional error context.
        """
        await Actor.fail(status_message=status_message, exception=exception)
