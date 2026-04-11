import json
from datetime import UTC, datetime
from functools import wraps
from math import ceil
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, msg: str, func: CallableWithMeta[P, R_co], block_time: datetime):
        super().__init__(msg)
        self.func_name: str = f"{func.__module__}.{func.__name__}"
        self.block_time: datetime = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        errors = []
        if critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        if len(errors) > 0:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)
        self.critical_count: int = critical_count
        self.time_to_recover: int = time_to_recover
        self.triggers_on: type[Exception] = triggers_on
        self.triggers_count: int = 0
        self.block_time: None | datetime = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.block_time_check(func)
            try:
                res = func(*args, **kwargs)
            except self.triggers_on as exp:
                self.triggers_count += 1
                if self.triggers_count == self.critical_count:
                    self.block_time = datetime.now(UTC)
                    error = BreakerError(TOO_MUCH, func, self.block_time)
                    raise error from exp
                raise
            self.triggers_count = 0
            return res

        return wrapper

    def block_time_check(self, func: CallableWithMeta[P, R_co]) -> None:
        if (self.block_time is not None) and (
            ceil((datetime.now(UTC) - self.block_time).total_seconds()) < self.time_to_recover
        ):
            raise BreakerError(TOO_MUCH, func, self.block_time)
        if self.block_time is not None:
            self.triggers_count = 0
            self.block_time = None


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
