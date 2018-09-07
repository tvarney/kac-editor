
from enum import IntEnum, unique

import typing
if typing.TYPE_CHECKING:
    from kac.map import KacMap


@unique
class BrushTile(IntEnum):
    Nothing = 0,
    WaterDeep = 1
    WaterFresh = 2,
    WaterSalt = 3,
    LandBarren = 4,
    LandFertile = 5,
    LandVeryFertile = 6,
    ResourceRock = 7,
    ResourceStone = 8,
    ResourceIron = 9,
    ResourceTree = 10,
    ResourceNoTree = 11


class Brush(object):
    def __init__(self) -> None:
        self._tile = BrushTile.Nothing
        self._size = 1

    def apply_single(self, map_obj: 'KacMap', tile: 'dict'):
        if self._tile == BrushTile.Nothing:
            return

        # TODO: Make sure to remove trees if they exist and they shouldn't on the new tile
        if self._tile == BrushTile.WaterDeep:
            tile["type"]["value__"].update(map_obj.file, 3)
            tile["deepWater"].update(map_obj.file, True)
        elif self._tile == BrushTile.WaterFresh:
            tile["type"]["value__"].update(map_obj.file, 3)
            tile["deepWater"].update(map_obj.file, False)
            tile["saltWater"].update(map_obj.file, False)
        elif self._tile == BrushTile.WaterSalt:
            tile["type"]["value__"].update(map_obj.file, 3)
            tile["deepWater"].update(map_obj.file, False)
            tile["saltWater"].update(map_obj.file, True)
        elif self._tile == BrushTile.LandBarren:
            tile["type"]["value__"].update(map_obj.file, 0)
            tile["fertile"].update(map_obj.file, 0)
        elif self._tile == BrushTile.LandFertile:
            tile["type"]["value__"].update(map_obj.file, 0)
            tile["fertile"].update(map_obj.file, 1)
        elif self._tile == BrushTile.LandVeryFertile:
            tile["type"]["value__"].update(map_obj.file, 0)
            tile["fertile"].update(map_obj.file, 2)
        elif self._tile == BrushTile.ResourceRock:
            tile["type"]["value__"].update(map_obj.file, 4)
        elif self._tile == BrushTile.ResourceStone:
            tile["type"]["value__"].update(map_obj.file, 2)
        elif self._tile == BrushTile.ResourceIron:
            tile["type"]["value__"].update(map_obj.file, 5)
        elif self._tile == BrushTile.ResourceTree:
            tile["amount"].update(map_obj.file, 3)
        elif self._tile == BrushTile.ResourceNoTree:
            tile["amount"].update(map_obj.file, 0)
        else:
            RuntimeError("Invalid BrushTile value: {}".format(self._tile))

    def apply(self, map_obj: 'KacMap', x: int, y: int):
        tile = map_obj.tiles[y * map_obj.width + x]
        self.apply_single(map_obj, tile)

    @property
    def tile(self) -> BrushTile:
        return self._tile

    @tile.setter
    def tile(self, brush_tile: BrushTile) -> None:
        self._tile = brush_tile

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, new_size: int) -> None:
        self._size = max(1, int(new_size))

