from typing import Any, Callable


class Subject[T]:
    def __init__(self, init: T) -> None:
        self._value = init
        self._observers: list[Callable[[T], Any]] = []

    @property
    def value(self) -> T:
        return self._value

    def attach(self, observer: Callable[[T], Any]) -> None:
        self._observers.append(observer)
        observer(self.value)  # Notify the observer of the current value

    def detach(self, observer: Callable[[T], Any]) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer(self._value)


class MutableSubject[T](Subject):
    @Subject.value.setter
    def value(self, new_value: T) -> None:
        if new_value == self._value:
            return
        self._value = new_value
        self.notify()
