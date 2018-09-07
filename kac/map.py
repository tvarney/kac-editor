
import pygame

import kac.colors as colors
from kac.tile import TileType, Fertility


class KacMap(object):
    KeyCellSaveData = "Cell+CellSaveData"
    KeyWorldSaveData = "World+WorldSaveData"
    KeyTownName = "TownNameUI+TownNameSaveData"
    KeyBuildings = "Building+BuildingSaveData"

    def __init__(self, map_objects, data_file) -> None:
        self._map_objects = map_objects
        self._data_file = data_file
        # self._tiles = map_objects["Cell+CellSaveData"].classBase.instances
        self._tiles = map_objects[KacMap.KeyCellSaveData].classBase.instances
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

    def draw(self, screen, width: int, x: int=0, y: int=0) -> None:
        tile_size = self.tile_size(width)
        for i in range(self._height):
            for j in range(self._width):
                tile = self._tiles[self._height * i + j]
                color = colors.get_tile_color(tile)
                upper_left = x + (self._width - j - 1) * tile_size, y + i * tile_size

                screen.fill(color, pygame.Rect(upper_left[0], upper_left[1], tile_size, tile_size))
                if tile["amount"].value > 0 and tile["type"]["value__"].value == 0:
                        tree_size = int(tile_size / 2.0)
                        screen.fill(colors.Tree, pygame.Rect(upper_left[0] + tree_size, upper_left[1] + tree_size, tree_size, tree_size))

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