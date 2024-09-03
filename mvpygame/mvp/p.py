import pygame as pg

from mvpygame.mvp.m import GameModel
from mvpygame.mvp.v import GameView


class GamePresenter:
    def __init__(
        self, view: GameView, model: GameModel, screen: pg.Surface, clock: pg.time.Clock, fps: int
    ):
        self.view = view
        self.model = model
        self.screen = screen
        self.clock = clock
        self.fps = fps
        self.running = True

    def update(self):
        dt = self.clock.tick(self.fps) / 1000.0
        self.model.update(dt)
        self.view.update(self.model.sprites)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            self.model.handle_event(event)
        keys = pg.key.get_pressed()
        self.model.handle_key_presses(keys)

    def run(self):
        while self.running:
            self.update()
