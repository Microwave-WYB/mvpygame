from abc import ABC
from enum import Enum, auto
from typing import Optional

import pygame as pg


class CoordSystem(Enum):
    """Coordinate Origin Enum"""

    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()


class AnchorPoint(Enum):
    """Anchor Point Enum"""

    TOP_LEFT = auto()
    TOP_CENTER = auto()
    TOP_RIGHT = auto()
    CENTER_LEFT = auto()
    CENTER = auto()
    CENTER_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_CENTER = auto()
    BOTTOM_RIGHT = auto()


class Sprite(pg.sprite.Sprite, ABC):
    """Custom Sprite Class"""

    def __init__(
        self,
        image: Optional[pg.Surface],
        pos: tuple[int, int],
        view_size: tuple[int, int],
        layer: int = 0,
        coord_system: CoordSystem = CoordSystem.BOTTOM_LEFT,
        anchor_point: AnchorPoint = AnchorPoint.BOTTOM_LEFT,
    ):
        super().__init__()
        self.view_size: tuple[int, int] = (0, 0)
        self.image = image
        self.virtual_pos = pos
        self.view_size = view_size
        self._layer = layer
        self.coord_system = coord_system
        self.anchor_point = anchor_point
        self.children: list[Sprite] = []

    def add_child(self, child: "Sprite") -> None:
        """Add a child sprite"""
        self.children.append(child)

    def on_resize(self, size: tuple[int, int]) -> None:
        """Handle a resize event"""
        for child in self.children:
            child.on_resize(size)

    @property
    def view_width(self) -> int:
        """View Width"""
        return self.view_size[0]

    @property
    def view_height(self) -> int:
        """View Height"""
        return self.view_size[1]

    @property
    def pos(self) -> tuple[int, int]:
        """Position"""
        match self.coord_system:
            case CoordSystem.TOP_LEFT:
                return self.virtual_pos
            case CoordSystem.BOTTOM_LEFT:
                return self.virtual_x, self.view_height - self.virtual_y

    @property
    def virtual_x(self) -> int:
        """Virtual X"""
        return self.virtual_pos[0]

    @virtual_x.setter
    def virtual_x(self, value: int) -> None:
        """Set Virtual X"""
        self.virtual_pos = value, self.virtual_pos[1]

    @property
    def virtual_y(self) -> int:
        """Virtual Y"""
        return self.virtual_pos[1]

    @virtual_y.setter
    def virtual_y(self, value: int) -> None:
        """Set Virtual Y"""
        self.virtual_pos = self.virtual_pos[0], value

    @property
    def x(self) -> int:
        """X"""
        return self.pos[0]

    @property
    def y(self) -> int:
        """Y"""
        return self.pos[1]

    @property
    def rect(self) -> Optional[pg.Rect]:
        """Rect"""
        if not self.image:
            return None
        rect: pg.Rect = self.image.get_rect()
        match self.anchor_point:
            case AnchorPoint.TOP_LEFT:
                rect.topleft = self.pos
            case AnchorPoint.TOP_CENTER:
                rect.midtop = self.pos
            case AnchorPoint.TOP_RIGHT:
                rect.topright = self.pos
            case AnchorPoint.CENTER_LEFT:
                rect.midleft = self.pos
            case AnchorPoint.CENTER:
                rect.center = self.pos
            case AnchorPoint.CENTER_RIGHT:
                rect.midright = self.pos
            case AnchorPoint.BOTTOM_LEFT:
                rect.bottomleft = self.pos
            case AnchorPoint.BOTTOM_CENTER:
                rect.midbottom = self.pos
            case AnchorPoint.BOTTOM_RIGHT:
                rect.bottomright = self.pos

        return rect

    def update(self, dt: float) -> None:
        """Update the sprite"""
        for child in self.children:
            child.update(dt)

    def draw(self, surface: pg.Surface) -> None:
        """Draw the sprite"""
        if self.image and self.rect:
            surface.blit(self.image, self.rect)

        for child in self.children:
            child.draw(surface)


class Group(pg.sprite.Group):
    """Custom Group Class"""

    def __init__(self, *sprites: Sprite):
        super().__init__(*sprites)

    def update(self, dt: float) -> None:
        """Update all sprites in the group"""
        for sprite in self.sprites():
            if isinstance(sprite, Sprite):
                sprite.update(dt)
