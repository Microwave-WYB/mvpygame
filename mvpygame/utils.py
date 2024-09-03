from typing import Callable, Optional


def unwrap[T](value: Optional[T], message: Optional[str] = None) -> T:
    if value is None:
        raise ValueError(message or f"Expected a value of type {T} but got None")
    return value


def unwrap_or_else[T](value: Optional[T], default_factory: Callable[[], T]) -> T:
    return value or default_factory()
