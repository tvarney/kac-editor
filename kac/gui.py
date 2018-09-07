
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


class Widget(object):
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._dirty = True
        self._parent = None
        self._active = False

    @property
    def parent(self) -> 'Widget':
        return self._parent

    @parent.setter
    def parent(self, parent: 'Widget') -> None:
        self._dirty = True
        self._parent = parent
        self._parent.dirty = True

    @property
    def dirty(self) -> bool:
        return self._dirty

    @dirty.setter
    def dirty(self, on: bool) -> None:
        if on and not self._dirty and self._parent is not None:
            self._dirty = on
            self.parent.dirty = True
        else:
            self._dirty = on

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

    def contains(self, pos: 'Tuple[int, int]') -> bool:
        x, y = self.origin
        width, height = self.dimensions
        return x <= pos[0] <= (x + width) and y <= pos[1] <= (y + height)

    def render(self, screen: 'pygame.Surface') -> None:
        self._dirty = False

    def set_active(self, on: bool=True) -> None:
        self._active = on

    def is_active(self) -> bool:
        return self._active

    def click(self, x, y) -> None:
        pass


class Container(Widget):
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        Widget.__init__(self, x, y, width, height)
        self._children = list()  # type: List[Widget]

    def render(self, screen: 'pygame.Surface') -> None:
        for child in self._children:
            if child.dirty:
                child.render(screen)
        self._dirty = False

    def add(self, child: 'Widget') -> None:
        self._children.append(child)
        child.parent = self

    def clear(self) -> None:
        self._children.clear()

    def click(self, x: int, y: int) -> None:
        for child in self._children:
            if child.contains((x, y)):
                child.click(x, y)


class Label(Widget):
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
        Widget.__init__(self, x, y, width, height)

    def render(self, screen: 'pygame.Surface') -> None:
        screen.blit(self._text_surface, self._text_origin, None, 1)
        self._dirty = False


class PushButton(Widget):
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
        self.action = kwargs.pop("action", None)
        width = max(self._text_size[0] + self._padding * 2, kwargs.pop("width", 0))
        height = max(self._text_size[1] + self._padding * 2, kwargs.pop("height", 0))
        Widget.__init__(self, x, y, width, height)
        self._inner_area = Rect(x + 1, y + 1, self.width - 2, self.height - 2)
        self._text_area = center_rect(self._inner_area, self._text_size)
        self._active = False

    def set_active(self, on: bool=True) -> None:
        if self._active != on:
            self.dirty = True
        self._active = on

    def render(self, screen: 'pygame.Surface'):
        pygame.draw.rect(screen, self._border_color, self.rect, 1)
        back_color = self._back_color_active if self.is_active() else self._back_color_inactive
        pygame.draw.rect(screen, back_color, self._inner_area, 0)
        screen.blit(self._text_surface, self._text_area.topleft, None, 1)
        self._dirty = False

    def click(self, x: int, y: int) -> None:
        if self.action is not None:
            self.action(self)
