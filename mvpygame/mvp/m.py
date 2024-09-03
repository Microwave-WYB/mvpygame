"""Model Class"""

from abc import ABC
from enum import Enum, auto
from typing import Iterable

import pygame as pg

from mvpygame.sprite import Group


class GameState(Enum):
    """Game State Enum"""

    RUNNING = auto()
    GAME_OVER = auto()


class GameModel(ABC):
    def __init__(self, size: tuple[int, int]):
        self.sprites = Group()
        self.state = GameState.RUNNING
        self.size: tuple[int, int] = size

    def on_resize(self, size: tuple[int, int]) -> None:
        """Handle a resize event"""
        self.size = size
        for sprite in self.sprites:
            sprite.on_resize(size)

    @property
    def width(self) -> int:
        """Width of the screen"""
        return self.size[0]

    @property
    def height(self) -> int:
        """Height of the screen"""
        return self.size[1]

    def update(self, dt: float) -> None:
        """Update the model"""
        self.sprites.update(dt)

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle an event"""

    def handle_key_presses(self, keys: Iterable[bool]) -> None:
        """Handle key presses"""
