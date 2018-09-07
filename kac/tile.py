
from enum import IntEnum, unique


@unique
class TileType(IntEnum):
    Land = 0
    Unknown = 1
    Stone = 2
    Water = 3
    Rock = 4
    Iron = 5


class Fertility:
    Barren = 0
    Fertile = 1
    VeryFertile = 2
