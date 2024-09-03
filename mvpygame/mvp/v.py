import pygame as pg

from mvpygame.sprite import Group
from mvpygame.subject import MutableSubject


class GameView:
    def __init__(self, surface: pg.Surface):
        self.surface = surface
        self.size_subject = MutableSubject[tuple[int, int]](surface.get_size())

    def draw(self, sprites: Group) -> None:
        """Draw the sprites, based on the coordinate origin"""
        for sprite in sorted(sprites, key=lambda s: s.layer):
            if hasattr(sprite, "draw"):
                sprite.draw(self.surface)

    def clear(self) -> None:
        """Clear the screen"""
        self.surface.fill(pg.Color("white"))

    def update(self, sprites: Group) -> None:
        """Update the display"""
        self.size_subject.value = self.surface.get_size()
        self.clear()
        self.draw(sprites)
        pg.display.flip()
