
import pygame
from pygame import Rect

import typing
if typing.TYPE_CHECKING:
    from typing import List, Tuple


def center_dim(outer: int, inner: int) -> int:
    return int((outer - inner) / 2)


def center_rect(outer: Rect, inner: 'Tuple[int, int]') -> Rect:
    x = int((outer.width - inner[0]) / 2)
    y = int((outer.height - inner[1]) / 2)
    return Rect(x + outer.x, y + outer.y, inner[0], inner[1])


class Renderable(object):
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self._x = x
        self._y = y
        self._width = width
        self._height = height

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def origin(self) -> 'Tuple[int, int]':
        return self._x, self._y

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def dimensions(self) -> 'Tuple[int, int]':
        return self._width, self._height

    @property
    def bounds(self) -> 'Tuple[int, int, int, int]':
        return self._x, self._y, self._width, self._height

    @property
    def rect(self) -> Rect:
        return Rect(self._x, self._y, self._width, self._height)

    def render(self, screen: 'pygame.Surface') -> None:
        pass


class Gui(Renderable):
    def __init__(self, x: int, y: int, width: int, height: int, **kwargs) -> None:
        Renderable.__init__(self, x, y, width, height)
        self._children = list()  # type: List[Renderable]
        self._font = kwargs.pop("font", None)
        if self._font is None:
            self._font = pygame.font.SysFont("Arial", 20)
        self.build()

    def render(self, screen) -> None:
        for child in self._children:
            child.render(screen)

    def build(self) -> None:
        self._children.clear()
        self._children.append(Label(self.x, 30, "Water", self._font, width=self.width, centered=True))
        self._children.append(PushButton(self.x + 2, self.y + 60, "Salt", self._font, width=66, height=66))
        self._children.append(PushButton(self.x + 70, self.y + 60, "Fresh", self._font, width=66, height=66))
        self._children.append(PushButton(self.x + 138, self.y + 60, "Deep", self._font, width=66, height=66))

        self._children.append(Label(self.x, 136, "Land", self._font, width=self.width, centered=True))
        self._children.append(PushButton(self.x + 2, self.y + 166, "Barren", self._font, width=66, height=66))
        self._children.append(PushButton(self.x + 70, self.y + 166, "Fertile", self._font, width=66, height=66))
        self._children.append(PushButton(self.x + 138, self.y + 166, "Fertile+", self._font, width=66, height=66))

        self._children.append(Label(self._x, 242, "Resources", self._font, width=self.width, centered=True))
        self._children.append(PushButton(self.x + 2, self.y + 272, "Rock", self._font, width=66, height=66))
        self._children.append(PushButton(self.x + 70, self.y + 272, "Stone", self._font, width=66, height=66))
        self._children.append(PushButton(self.x + 138, self.y + 272, "Iron", self._font, width=66, height=66))

        self._children.append(Label(self._x, 348, "Trees", self._font, width=self.width, centered=True))
        self._children.append(PushButton(self.x + 1, self.y + 378, "Trees", self._font, width=66, height=66))
        self._children.append(PushButton(self.x + 70, self.y + 378, "No Trees", self._font, width=66, height=66))


class Label(Renderable):
    def __init__(self, x: int, y: int, title: str, font: 'pygame.font.Font', **kwargs) -> None:
        self._text = title
        self._text_size = font.size(title)
        self._centered = kwargs.pop("centered", False)
        width = max(self._text_size[0], kwargs.pop("width", 0))
        height = max(self._text_size[1], kwargs.pop("height", 0))
        self._anti_alias = bool(kwargs.pop("anti_alias", False))
        self._color = kwargs.pop("color", (255, 255, 255))
        self._text_surface = font.render(self._text, self._anti_alias, self._color)
        self._text_origin = x, y
        if self._centered:
            self._text_origin = x + center_dim(width, self._text_size[0]), y + center_dim(height, self._text_size[1])
        Renderable.__init__(self, x, y, width, height)

    def render(self, screen: 'pygame.Surface') -> None:
        screen.blit(self._text_surface, self._text_origin, None, 1)


class PushButton(Renderable):
    def __init__(self, x: int, y: int, title: str, font: 'pygame.font.Font', **kwargs) -> None:
        self._title = title
        self._font = font
        self._anti_alias = bool(kwargs.pop("anti_alias", False))
        self._color = kwargs.pop("color", (255, 255, 255))
        self._border_color = kwargs.pop("border_color", (255, 255, 255))
        self._back_color_active = kwargs.pop("back_color_active", (64, 0, 0))
        self._back_color_inactive = kwargs.pop("back_color_inactive", (0, 0, 0))
        self._padding = max(kwargs.pop("padding", 2), 2)
        self._text_size = font.size(self._title)
        self._text_surface = font.render(self._title, self._anti_alias, self._color)
        width = max(self._text_size[0] + self._padding * 2, kwargs.pop("width", 0))
        height = max(self._text_size[1] + self._padding * 2, kwargs.pop("height", 0))
        Renderable.__init__(self, x, y, width, height)
        self._inner_area = Rect(x + 1, y + 1, self.width - 2, self.height - 2)
        self._text_area = center_rect(self._inner_area, self._text_size)

    def render(self, screen: 'pygame.Surface'):
        pygame.draw.rect(screen, self._border_color, self.rect, 1)
        pygame.draw.rect(screen, self._back_color_inactive, self._inner_area, 0)
        screen.blit(self._text_surface, self._text_area.topleft, None, 1)

    def contains(self, pos: 'Tuple[int, int]') -> bool:
        x, y = self.origin
        width, height = self.dimensions
        return x <= pos[0] <= (x + width) and y <= pos[1] <= (y + height)
