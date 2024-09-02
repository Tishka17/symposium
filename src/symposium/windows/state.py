import inspect
from typing import ClassVar, TypeGuard


class State:
    _instances: ClassVar[int] = 0

    def __init__(self):
        self.number = self._instances + 1
        State._instances += 1
        self.name: str | None = None
        self.owner: type[StatesGroup] | None = None

    def __get__(self, instance, owner):
        return self

    def __set_name__(self, owner: "StatesGroup", name):
        self.name = name
        self.owner = owner

    def __str__(self):
        return f"{self.owner.name}.{self.name}"


def is_state(attribute: object) -> TypeGuard[State]:
    return isinstance(attribute, State)


class StatesGroup:
    def __init_subclass__(cls, name: str | None = None):
        cls.name = name or cls.__name__

    @classmethod
    def states(cls) -> list[State]:
        states = [state for name, state in inspect.getmembers(cls, is_state)]
        states.sort(key=lambda x: x.number)
        return states
