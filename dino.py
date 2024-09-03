from typing import override

import pygame as pg

from mvpygame.mvp.m import GameModel, GameState
from mvpygame.mvp.p import GamePresenter
from mvpygame.mvp.v import GameView
from mvpygame.sprite import AnchorPoint, Sprite
from mvpygame.subject import MutableSubject
from mvpygame.utils import unwrap

pg.init()
pg.font.init()
pg.display.set_caption("Dino Game")


def between[T: int | float](value: T, min_value: T, max_value: T) -> T:
    return min(max(value, min_value), max_value)


class Physics:
    @staticmethod
    def update(*args: float, dt: float = 1) -> tuple[float, ...]:
        if not args:
            raise ValueError("At least one value must be provided")

        return tuple(
            v + dt * next_v if i < len(args) - 1 else v
            for i, (v, next_v) in enumerate(zip(args, args[1:] + (0,)))
        )


class Dino(Sprite):
    def __init__(
        self,
        pos: tuple[int, int],
        view_size: tuple[int, int],
        ground_level: int = 0,
        jump_speed: int = 20,
        jump_buffer_tolerance_height: int = 180,
        accel_y: int = -1,
        max_speed_y: int = 20,
    ):
        image = pg.Surface((50, 50))
        image.fill(pg.Color("red"))
        super().__init__(image, pos, view_size)
        self.ground_level = ground_level
        self.speed_y = 0
        self.jump_speed = jump_speed
        self.accel_y = accel_y
        self.max_speed_y = max_speed_y
        self.jump_buffer = False
        self.jump_buffer_tolerance_height = jump_buffer_tolerance_height

    def can_buffer_jump(self) -> bool:
        return (
            self.virtual_y - self.ground_level <= self.jump_buffer_tolerance_height
            and self.speed_y < 0
        )

    def on_ground(self) -> bool:
        return self.virtual_y == self.ground_level

    def _jump(self) -> None:
        self.speed_y += self.jump_speed
        self.jump_buffer = False

    def jump(self) -> None:
        if self.on_ground():
            self._jump()
        elif self.can_buffer_jump():
            print("Can't jump yet, buffering jump")
            self.jump_buffer = True

    def update(self, dt: float) -> None:
        if self.jump_buffer and self.on_ground():
            print("Jumping from buffer")
            self._jump()

        virtual_y, self.speed_y, _ = Physics.update(self.virtual_y, self.speed_y, self.accel_y)
        self.virtual_y = int(virtual_y)
        self.virtual_y = between(self.virtual_y, self.ground_level, self.view_height)
        self.speed_y = between(self.speed_y, -self.max_speed_y, self.max_speed_y)
        if self.on_ground():
            self.speed_y = 0
        print(self.virtual_y, self.speed_y)


class Obstacle(Sprite):
    def __init__(
        self,
        pos: tuple[int, int],
        view_size: tuple[int, int],
        scroll_speed: int = 5,
    ):
        image = pg.Surface((20, 60))
        image.fill(pg.Color("black"))
        super().__init__(image, pos, view_size)
        self.scroll_speed = scroll_speed

    def on_speed_change(self, speed: int) -> None:
        self.scroll_speed = speed

    def update(self, dt: float) -> None:
        self.virtual_x -= self.scroll_speed

    def off_screen(self) -> bool:
        return self.x + unwrap(self.rect).width < 0


class Score(Sprite):
    def __init__(self, pos: tuple[int, int], view_size: tuple[int, int]):
        self.value = 0
        self.font = pg.font.Font(None, 36)
        image = self.font.render(f"Score: {self.value}", True, pg.Color("black"))
        super().__init__(image, pos, view_size, anchor_point=AnchorPoint.TOP_LEFT)

    def increment(self) -> None:
        self.value += 1
        self.image = self.font.render(f"Score: {self.value}", True, pg.Color("black"))

    def reset(self) -> None:
        self.value = 0


class DinoModel(GameModel):
    def __init__(self, size: tuple[int, int]):
        super().__init__(size)
        self.scroll_speed_subject = MutableSubject[int](5)
        self.score = Score((20, self.height - 10), view_size=size)
        self.can_pass = True
        self.dino = Dino((70, 0), ground_level=0, jump_speed=17, view_size=size)
        self.obstacle = Obstacle(
            (self.width, 0), view_size=size, scroll_speed=self.scroll_speed_subject.value
        )
        self.scroll_speed_subject.attach(self.obstacle.on_speed_change)
        self.sprites.add(self.dino, self.obstacle, self.score)

    def check_collision(self) -> None:
        if unwrap(self.dino.rect).colliderect(unwrap(self.obstacle.rect)):
            self.state = GameState.GAME_OVER

    def check_obstacle_off_screen(self) -> None:
        if self.obstacle.off_screen():
            self.obstacle.virtual_x = self.width
            self.can_pass = True

    def check_pass(self) -> None:
        if self.can_pass and self.dino.virtual_x > self.obstacle.virtual_x:
            self.score.increment()
            self.can_pass = False

    def update_scroll_speed(self) -> None:
        new_speed = min(5 + self.score.value // 5, 15)
        self.scroll_speed_subject.value = new_speed

    @override
    def update(self, dt: float) -> None:
        super().update(dt)
        self.check_pass()
        self.check_obstacle_off_screen()
        self.check_collision()
        self.update_scroll_speed()

    @override
    def handle_event(self, event: pg.event.Event) -> None:
        super().handle_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.dino.jump()


class DinoPresenter(GamePresenter):
    @override
    def update(self) -> None:
        super().update()
        if self.model.state == GameState.GAME_OVER:
            self.running = False
            print("Game Over")


if __name__ == "__main__":
    view = GameView(pg.display.set_mode((800, 600)))
    model = DinoModel((800, 600))
    view.size_subject.attach(model.on_resize)
    presenter = DinoPresenter(view, model, pg.display.get_surface(), pg.time.Clock(), 60)
    presenter.run()
