#!/usr/bin/python3
import argparse, time, sys
import pygame
from extractor import parse_save_file, write_save_file
from shutil import copyfile

from kac.map import KacMap

selectedCellType = None
TYPE_WATER_DEEP = 1
TYPE_WATER_FRESH = 2
TYPE_WATER_SALT = 3
TYPE_FARM_BARREN = 4
TYPE_FARM_FERTILE = 5
TYPE_FARM_FERTILE_PLUS = 6
TYPE_RES_ROCK = 7
TYPE_RES_STONE = 8
TYPE_RES_IRON = 9
TYPE_TREE_NOTREE = 10
TYPE_TREE_TREE = 11


def process_mouse_event(event, screen, map_object: KacMap):
    global selectedCellType
    if event[0] > 640:

        pos = event[0] - 640
        pos /= 66
        pos = int(pos)

        if event[1] >= 60 and event[1] <= 126:
            if pos == 0:
                selectedCellType = TYPE_WATER_SALT
            elif pos == 1:
                selectedCellType = TYPE_WATER_FRESH
            else:
                selectedCellType = TYPE_WATER_DEEP

        elif event[1] >= 172 and event[1] <= 238:
            if pos == 0:
                selectedCellType = TYPE_FARM_BARREN
            elif pos == 1:
                selectedCellType = TYPE_FARM_FERTILE
            elif pos == 2:
                selectedCellType = TYPE_FARM_FERTILE_PLUS
        elif event[1] >= 278 and event[1] <= 344:
            if pos == 0:
                selectedCellType = TYPE_RES_ROCK
            elif pos == 1:
                selectedCellType = TYPE_RES_STONE
            elif pos == 2:
                selectedCellType = TYPE_RES_IRON
        elif event[1] >= 384 and event[1] <= 450:
            if pos == 0:
                selectedCellType = TYPE_TREE_TREE
            elif pos == 1:
                selectedCellType = TYPE_TREE_NOTREE

    else:
        tile_factor = map_object.width / 640.0
        tile_x = map_object.width - int(event[0] * tile_factor) - 1
        tile_y = int(event[1] * tile_factor)
        selectedTile = map_object.tiles[tile_y * map_object.width + tile_x]
        if selectedCellType == TYPE_WATER_DEEP:
            selectedTile["type"]["value__"].update(map_object.file, 3)
            selectedTile["deepWater"].update(map_object.file, True)
        elif selectedCellType == TYPE_WATER_FRESH:
            selectedTile["type"]["value__"].update(map_object.file, 3)
            selectedTile["deepWater"].update(map_object.file, False)
            selectedTile["saltWater"].update(map_object.file, False)
        elif selectedCellType == TYPE_WATER_SALT:
            selectedTile["type"]["value__"].update(map_object.file, 3)
            selectedTile["deepWater"].update(map_object.file, False)
            selectedTile["saltWater"].update(map_object.file, True)
        elif selectedCellType == TYPE_FARM_BARREN:
            selectedTile["type"]["value__"].update(map_object.file, 0)
            selectedTile["fertile"].update(map_object.file, 0)
        elif selectedCellType == TYPE_FARM_FERTILE:
            selectedTile["type"]["value__"].update(map_object.file, 0)
            selectedTile["fertile"].update(map_object.file, 1)
        elif selectedCellType == TYPE_FARM_FERTILE_PLUS:
            selectedTile["type"]["value__"].update(map_object.file, 0)
            selectedTile["fertile"].update(map_object.file, 2)
        elif selectedCellType == TYPE_RES_ROCK:
            selectedTile["type"]["value__"].update(map_object.file, 4)
        elif selectedCellType == TYPE_RES_STONE:
            selectedTile["type"]["value__"].update(map_object.file, 2)
        elif selectedCellType == TYPE_RES_IRON:
            selectedTile["type"]["value__"].update(map_object.file, 5)
        elif selectedCellType == TYPE_TREE_TREE:
            selectedTile["amount"].update(map_object.file, 3)
        elif selectedCellType == TYPE_TREE_NOTREE:
            selectedTile["amount"].update(map_object.file, 0)

        map_object.draw(screen, 640)


def main():
    parser = argparse.ArgumentParser(description="Kingdoms and Castles save editor.")
    parser.add_argument("--input", "-i", help="the path to your save file")
    parser.add_argument("--gui", "-g", help="launches the GUI", action="store_true")
    args = parser.parse_args()

    savefile = args.input if args.input is not None else "./test/world"
    savefile_backup = savefile + "-" + time.strftime("%Y%m%d%H%M%S")
    print("Making a backup copy of", savefile, "to", savefile_backup)
    try:
        copyfile(savefile, savefile_backup)
    except FileNotFoundError:
        print("The savefile does not exists !")
        sys.exit(1)

    main_objects, data_file = parse_save_file(savefile_backup)
    kac_map = KacMap(main_objects, data_file)
    print("Loaded save for town {}".format(kac_map.name))
    print("The map is {} by {}".format(kac_map.width, kac_map.height))

    if args.gui != None:
        print("Loading GUI...")
        screen = pygame.display.set_mode((840, 640))
        pygame.font.init()
        mainfont = pygame.font.SysFont("Arial", 20)
        smallfont = pygame.font.SysFont("Arial", 14)

        pygame.draw.line(screen, (255, 255, 255), (640, 0), (640, 640))
        screen.blit(mainfont.render('Water', False, (255, 255, 255)), (700, 30))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(641, 60, 66, 66), 1)
        screen.blit(mainfont.render('Salt', False, (255, 255, 255)), (660, 66))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(707, 60, 66, 66), 1)
        screen.blit(mainfont.render('Fresh', False, (255, 255, 255)), (716, 66))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(773, 60, 66, 66), 1)
        screen.blit(mainfont.render('Deep', False, (255, 255, 255)), (783, 66))

        screen.blit(mainfont.render('Farm', False, (255, 255, 255)), (700, 136))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(641, 166, 66, 66), 1)
        screen.blit(mainfont.render('Barren', False, (255, 255, 255)), (645, 172))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(707, 166, 66, 66), 1)
        screen.blit(mainfont.render('Fertile', False, (255, 255, 255)), (716, 172))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(773, 166, 66, 66), 1)
        screen.blit(mainfont.render('Fertile+', False, (255, 255, 255)), (773, 172))

        screen.blit(mainfont.render('Ressources', False, (255, 255, 255)), (700, 242))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(641, 272, 66, 66), 1)
        screen.blit(mainfont.render('Rock', False, (255, 255, 255)), (645, 278))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(707, 272, 66, 66), 1)
        screen.blit(mainfont.render('Stone', False, (255, 255, 255)), (716, 278))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(773, 272, 66, 66), 1)
        screen.blit(mainfont.render('Iron', False, (255, 255, 255)), (773, 278))

        screen.blit(mainfont.render('Trees', False, (255, 255, 255)), (700, 348))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(641, 378, 66, 66), 1)
        screen.blit(mainfont.render('Trees', False, (255, 255, 255)), (645, 384))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(707, 378, 66, 66), 1)
        screen.blit(mainfont.render('Notree', False, (255, 255, 255)), (716, 384))

        screen.blit(smallfont.render('Press F to turn all farms fertile+', False, (255, 255, 255)), (640, 490))
        screen.blit(smallfont.render('Press C to clear the map', False, (255, 255, 255)), (640, 510))

        kac_map.draw(screen, 640)
        pygame.display.flip()

        running = True
        isMouseDown = False
        while running:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                running = False
                write_save_file(savefile, kac_map.file)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                process_mouse_event(event.pos, screen, kac_map)
                isMouseDown = True
                pygame.display.flip()
            elif event.type == pygame.MOUSEBUTTONUP:
                isMouseDown = False
            elif event.type == pygame.MOUSEMOTION:
                if isMouseDown:
                    process_mouse_event(event.pos, screen, kac_map)
                    pygame.display.flip()
            elif event.type == pygame.KEYDOWN:
                if event.unicode == "f" or event.unicode == "F":
                    kac_map.turn_all_farms()
                    kac_map.draw(screen, 640)
                    pygame.display.flip()
                elif event.unicode == "c" or event.unicode == "C":
                    kac_map.clear()
                    kac_map.draw(screen, 640)
                    pygame.display.flip()


if __name__ == "__main__":
    main()
