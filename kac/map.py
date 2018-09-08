
import math
import pygame
from pygame import Rect

import kac.colors as colors
from kac.brush import Brush
from kac.gui import Widget
from kac.tile import TileType, Fertility


class KacMap(object):
    KeyCellSaveData = "Cell+CellSaveData"
    KeyWorldSaveData = "World+WorldSaveData"
    KeyTownName = "TownNameUI+TownNameSaveData"
    KeyBuildings = "Building+BuildingSaveData"

    def __init__(self, map_objects, data_file) -> None:
        self._map_objects = map_objects
        self._data_file = data_file
        self._tiles = map_objects[KacMap.KeyCellSaveData].class_base.instances
        self._width = self._map_objects[KacMap.KeyWorldSaveData]["gridWidth"].value
        self._height = self._map_objects[KacMap.KeyWorldSaveData]["gridHeight"].value
        self._name = self._map_objects[KacMap.KeyTownName]["townName"].value
        self._object_data = None
        self._objects = [None] * len(self._tiles)

        if KacMap.KeyBuildings in self._map_objects:
            print("Buildings: ")
            self._object_data = self._map_objects[KacMap.KeyBuildings].classBase.instances
            for building in self._object_data:
                pos = building["globalPosition"]["x"][0], building["globalPosition"]["y"][0]
                idx = pos[0] + pos[1] * self._width
                self._objects[idx] = building["uniqueName"].value
                print("  ({}, {}) -> {}".format(pos[0], pos[1], self._objects[idx]))

    def tile_size(self, width: float) -> float:
        return width / self._width

    def turn_all_farms(self):
        for tile in self._tiles:
            tile["fertile"].update(self._data_file, 2)

    def clear(self):
        for tile in self._tiles:
            tile["fertile"].update(self._data_file, Fertility.Barren)
            tile["deepWater"].update(self._data_file, True)
            tile["saltWater"].update(self._data_file, False)
            tile["type"]["value__"].update(self._data_file, TileType.Water)

    @property
    def tiles(self) -> dict:
        return self._tiles

    @property
    def objects(self) -> dict:
        return self._map_objects

    @property
    def name(self) -> str:
        return self._name

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def file(self):
        return self._data_file


class MapWidget(Widget):
    def __init__(self, x: int, y: int, width: int, height: int, map_object: KacMap) -> None:
        Widget.__init__(self, x, y, width, height)
        self.map = map_object
        self.brush = Brush()
        self.grid = True
        self.grid_color = colors.Black
        self._map_area = self.rect

    def render(self, screen):
        if not self._dirty:
            return

        if self.grid:
            self._render_grid(screen)
        else:
            self._render_nogrid(screen)
        self._dirty = False

    def _render_nogrid(self, screen):
        self._map_area = self.rect
        tile_size = self.width / self.map.width
        for i in range(self.map.height):
            for j in range(self.map.width):
                tile = self.map.tiles[self.map.height * i + j]
                color = colors.get_tile_color(tile)
                upper_left = self.x + (self.map.width - j - 1) * tile_size, self.y + i * tile_size

                screen.fill(color, pygame.Rect(upper_left[0], upper_left[1], tile_size, tile_size))
                if tile["amount"].value > 0 and tile["type"]["value__"].value == 0:
                        tree_size = int(tile_size / 2.0)
                        tile_rect = Rect(upper_left[0] + tree_size, upper_left[1] + tree_size, tree_size, tree_size)
                        screen.fill(colors.Tree, tile_rect)

    def _render_grid(self, screen):
        map_width = self.map.width
        map_height = self.map.height
        grid_pixels = map_width + 1, map_height + 1
        tile_size = (
            int((self.width - grid_pixels[0]) / map_width),
            int((self.height - grid_pixels[1]) / map_height)
        )
        border_width = (
            (self.width - ((tile_size[0] * map_width) + map_width + 1)) / 2.0,
            (self.height - ((tile_size[1] * map_height) + map_height + 1)) / 2.0
        )

        # Draw our borders
        left = Rect(0, 0, int(math.floor(border_width[0])), self.height)
        right_width = int(math.ceil(border_width[0]))
        right = Rect(self.width - right_width, 0, right_width, self.height)
        top_width = right.left - left.right
        top = Rect(left.right, 0, top_width, int(math.floor(border_width[1])))
        bottom_height = int(math.ceil(border_width[1]))
        bottom = Rect(left.right, self.height - bottom_height, top_width, bottom_height)
        screen.fill(self.grid_color, left)
        screen.fill(self.grid_color, right)
        screen.fill(self.grid_color, top)
        screen.fill(self.grid_color, bottom)

        self._map_area = Rect(left.right, top.bottom, right.left, bottom.top)
        x, y = self._map_area.left, self._map_area.top

        for i in range(map_height):
            for j in range(map_width):
                tile = self.map.tiles[map_height * i + j]
                color = colors.get_tile_color(tile)
                # upper_left = x + (map_width - j - 1) * tile_size[0] + j, y + i * tile_size[1] + i
                upper_left = x + j * tile_size[0] + j, y + i * tile_size[1] + i

                screen.fill(color, Rect(upper_left[0], upper_left[1], tile_size[0], tile_size[1]))
                if tile["amount"].value > 0 and tile["type"]["value__"].value == 0:
                    tree_size = int(tile_size[0] / 2.0)
                    tile_rect = Rect(upper_left[0] + tree_size, upper_left[1] + tree_size, tree_size, tree_size)
                    screen.fill(colors.Tree, tile_rect)

    def click(self, x: int, y: int) -> None:
        inside_x = self._map_area.left <= x <= self._map_area.right
        inside_y = self._map_area.top <= y <= self._map_area.bottom
        if not (inside_x and inside_y):
            return

        x -= self._map_area.left
        y -= self._map_area.top

        tile_factor = self.map.width / self._map_area.width
        tile_x = int(math.ceil(x * tile_factor))
        tile_y = int(math.ceil(y * tile_factor))
        if 0 <= tile_x < self.map.width and 0 <= tile_y < self.map.height:
            self.brush.apply(self.map, tile_x, tile_y)
            self._dirty = True
