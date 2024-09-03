from random import randint
from typing import override

import pygame as pg

from mvpygame.mvp.m import GameModel, GameState
from mvpygame.mvp.p import GamePresenter
from mvpygame.mvp.v import GameView
from mvpygame.sprite import AnchorPoint, CoordSystem, Group, Sprite
from mvpygame.utils import unwrap

pg.init()
pg.font.init()
pg.display.set_caption("Flappy Bird")


def between[T: int | float](value: T, min_value: T, max_value: T) -> T:
    return min(max(value, min_value), max_value)


class SimplePhysics:
    @staticmethod
    def update(*args: float, dt: float = 1) -> tuple[float, ...]:
        if not args:
            raise ValueError("At least one value must be provided")

        return tuple(
            v + dt * next_v if i < len(args) - 1 else v
            for i, (v, next_v) in enumerate(zip(args, args[1:] + (0,)))
        )


class Bird(Sprite):
    def __init__(self, pos: tuple[int, int], view_size: tuple[int, int], jump_speed: int = 12):
        image = pg.Surface((50, 50))
        image.fill(pg.Color("orange"))
        super().__init__(image, pos, view_size)
        self.speed_y = 0
        self.accel_y = -0.8
        self.jump_speed = jump_speed

    @override
    def update(self, dt: float) -> None:
        virtual_y, self.speed_y, _ = SimplePhysics.update(
            self.virtual_y, self.speed_y, self.accel_y
        )
        self.virtual_y = int(virtual_y)

    def jump(self) -> None:
        self.speed_y = self.jump_speed


class Pipe(Sprite):
    """Single pipe"""

    def __init__(
        self,
        gap_center_left: tuple[int, int],
        view_size: tuple[int, int],
        scroll_speed: int = -5,
        gap_size: int = 200,
        pipe_width: int = 50,
        upper: bool = False,
    ):
        image = pg.Surface((pipe_width, view_size[1]))
        image.fill(pg.Color("green"))
        anchorpoint_type = AnchorPoint.BOTTOM_LEFT if upper else AnchorPoint.TOP_LEFT
        anchorpoint_pos = (
            (gap_center_left[0], gap_center_left[1] + gap_size // 2)
            if upper
            else (gap_center_left[0], gap_center_left[1] - gap_size // 2)
        )
        super().__init__(
            image,
            anchorpoint_pos,
            view_size,
            anchor_point=anchorpoint_type,
            coord_system=CoordSystem.BOTTOM_LEFT,
        )

        self.scroll_speed = scroll_speed

    @override
    def update(self, dt: float) -> None:
        self.virtual_x += self.scroll_speed

    def off_screen(self) -> bool:
        return self.virtual_x < -unwrap(self.rect).width


class PipePair(Sprite):
    def __init__(
        self,
        gap_center_left: tuple[int, int],
        view_size: tuple[int, int],
        scroll_speed: int = -5,
        gap_size: int = 200,
        pipe_width: int = 50,
    ):
        super().__init__(None, gap_center_left, view_size)
        self.upper = Pipe(
            gap_center_left, view_size, scroll_speed, gap_size, pipe_width, upper=True
        )
        self.lower = Pipe(
            gap_center_left, view_size, scroll_speed, gap_size, pipe_width, upper=False
        )
        self.add_child(self.upper)
        self.add_child(self.lower)

    @override
    def update(self, dt: float) -> None:
        super().update(dt)

    def off_screen(self) -> bool:
        return self.upper.off_screen()


class Score(Sprite):
    def __init__(self, pos: tuple[int, int], view_size: tuple[int, int]):
        self.value = 0
        self.font = pg.font.Font(None, 36)
        image = self.font.render(f"Score: {self.value}", True, pg.Color("black"))
        super().__init__(image, pos, view_size, anchor_point=AnchorPoint.TOP_LEFT, layer=1)

    def increment(self) -> None:
        self.value += 1
        self.image = self.font.render(f"Score: {self.value}", True, pg.Color("black"))

    def reset(self) -> None:
        self.value = 0


class FlappyBirdModel(GameModel):
    def __init__(self, size: tuple[int, int]):
        super().__init__(size)
        self.bird = Bird((100, size[1] // 2), size)
        self.pipes = Group()
        self.pipes.add(PipePair((size[0], size[1] // 2), size))
        self.sprites.add(self.bird, *self.pipes)
        self.score = Score((20, self.height - 10), view_size=size)
        self.sprites.add(self.bird, *self.pipes, self.score)
        self.can_pass = True

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.bird.jump()

    def check_bird_off_screen(self) -> None:
        if self.bird.virtual_y < 0 or self.bird.virtual_y > self.height:
            self.state = GameState.GAME_OVER

    def check_pipe_off_screen(self) -> None:
        for pair in self.pipes:
            if pair.off_screen():
                self.pipes.remove(pair)
                self.spawn_pipe_pair()
                self.can_pass = True

    def check_pass(self) -> None:
        for pair in self.pipes:
            if self.can_pass and pair.upper.virtual_x < self.bird.virtual_x:
                self.score.increment()
                self.can_pass = False

    def spawn_pipe_pair(self) -> None:
        gap_center_left = (self.width, randint(100, self.height - 100))
        self.pipes.add(PipePair(gap_center_left, self.size))
        self.sprites.add(*self.pipes)

    def check_collision(self) -> None:
        for pair in self.pipes:
            if pair.upper.rect.colliderect(self.bird.rect) or pair.lower.rect.colliderect(
                self.bird.rect
            ):
                self.state = GameState.GAME_OVER

    def update(self, dt: float) -> None:
        super().update(dt)
        self.check_collision()
        self.check_bird_off_screen()
        self.check_pipe_off_screen()
        self.check_pass()


class FlappyBirdPresenter(GamePresenter):
    def update(self) -> None:
        super().update()
        if self.model.state == GameState.GAME_OVER:
            self.running = False


if __name__ == "__main__":
    screen = pg.display.set_mode((600, 600))
    view = GameView(screen)
    model = FlappyBirdModel(view.size_subject.value)
    view.size_subject.attach(model.on_resize)
    presenter = FlappyBirdPresenter(view, model, screen, pg.time.Clock(), 60)
    presenter.run()
