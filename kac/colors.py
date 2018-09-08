
from kac.tile import TileType, Fertility

import typing
if typing.TYPE_CHECKING:
    from typing import Tuple


White = (255, 255, 255)
Black = (0, 0, 0)
Magenta = (255, 0, 255)
DarkRed = (64, 0, 0)

Unknown = Magenta

LandBarren = (193, 206, 100)
LandFertile = (146, 190, 69)
LandVeryFertile = (103, 154, 49)

WaterFresh = (124, 199, 230)
WaterSalt = (167, 239, 254)
WaterDeep = (56, 137, 192)

ResourceStone = (166, 166, 166)
ResourceIron = (153, 102, 0)
UnusableStone = (32, 32, 32)

Tree = (102, 51, 0)


def get_tile_color(tile: dict) -> 'Tuple[int, int, int]':
    tile_type = tile["type"]["value__"].value
    if tile_type == TileType.Land:
        fertility = tile["fertile"].value
        if fertility == Fertility.Barren:
            return LandBarren
        if fertility == Fertility.Fertile:
            return LandFertile
        if fertility == Fertility.VeryFertile:
            return LandVeryFertile
        return Unknown
    if tile_type == TileType.Stone:
        return ResourceStone
    if tile_type == TileType.Water:
        if tile["deepWater"].value:
            return WaterDeep
        if tile["saltWater"].value:
            return WaterSalt
        return WaterFresh
    if tile_type == TileType.Rock:
        return UnusableStone
    if tile_type == TileType.Iron:
        return ResourceIron

    print("Unknown tile type: {}".format(tile_type))
    return 255, 0, 255
