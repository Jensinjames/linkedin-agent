from typing import Any, Dict

class PlatformAdapter:
    async def get_input(self) -> Dict[str, Any]:
        raise NotImplementedError

    async def push_data(self, data: Any) -> None:
        raise NotImplementedError

    def log_info(self, msg: str) -> None:
        """
        Logs an informational message to the platform's logging system.
        
        Parameters:
            msg (str): The message to be logged.
        """
        raise NotImplementedError

    async def fail(self, status_message: str, exception: Exception = None) -> None:
        """
        Handle failure scenarios by reporting a status message and optionally an exception.
        
        Parameters:
            status_message (str): Description of the failure.
            exception (Exception, optional): The exception associated with the failure, if any.
        """
        raise NotImplementedError
