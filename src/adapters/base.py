from typing import Any, Dict

class PlatformAdapter:
    async def get_input(self) -> Dict[str, Any]:
        raise NotImplementedError

    async def push_data(self, data: Any) -> None:
        raise NotImplementedError

    def log_info(self, msg: str) -> None:
        raise NotImplementedError

    async def fail(self, status_message: str, exception: Exception = None) -> None:
        raise NotImplementedError
