#!/usr/bin/python3

import argparse
import time
import pygame
import shutil

from kac import colors
from kac.extractor import parse_save_file, write_save_file
from kac.map import KacMap
from kac.gui import Gui


class Application(object):
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

    def __init__(self) -> None:
        self.map = None
        self.gui = None
        self.parser = argparse.ArgumentParser(description="Kingdoms and Castles map editor")
        self.parser.add_argument("--input", "-i", help="The path to a KaC save file")
        self.parser.add_argument("--gui", "-g", help="Launches the GUI", action="store_true")
        self._run_gui = True
        self.save_file = None
        self.objects = None
        self.data = None
        self.screen = None
        self.small_font = None

    def parse_args(self) -> None:
        print("Application::parse_args()")
        args = self.parser.parse_args()
        self.save_file = args.input
        if args.gui is None:
            print("  Running without GUI")
            self._run_gui = False

    def start_pygame(self) -> None:
        print("Application::start_pygame()")
        self.screen = pygame.display.set_mode((844, 640))
        pygame.font.init()
        self.gui = Gui(640, 0, 204, 640)
        self.small_font = pygame.font.SysFont("Arial", 14)

    def parse_save(self) -> bool:
        print("Application::parse_save()")
        if self.save_file is None:
            print("No Save file chosen; using test data")
            self.save_file = "./test/world"

        backup_file = self.save_file + "-" + time.strftime("%Y%m%d%H%M%S")
        print("Making a backup copy of {} at {}".format(self.save_file, backup_file))
        shutil.copyfile(self.save_file, backup_file)
        self.objects, self.data = parse_save_file(backup_file)
        self.map = KacMap(self.objects, self.data)
        print("Loaded save for town {}".format(self.map.name))
        print("The map is {} by {}".format(self.map.width, self.map.height))
        return True

    def render(self) -> None:
        pygame.draw.line(self.screen, (255, 255, 255), (640, 0), (640, 640))

        self.gui.render(self.screen)

        self.screen.blit(self.small_font.render('Press F to turn all farms fertile+', False, colors.White), (640, 490))
        self.screen.blit(self.small_font.render('Press C to clear the map', False, colors.White), (640, 510))
        self.map.draw(self.screen, 640)
        pygame.display.flip()

    def main_loop(self):
        self.parse_args()
        if not self.parse_save():
            print("Failed to parse save file; quitting...")
            return

        if self._run_gui:
            print("Loading GUI...")
            self.start_pygame()
            self.render()

            running = True
            is_mouse_down = False
            while running:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    running = False
                    write_save_file(self.save_file, self.map.file)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.process_mouse_event(event.pos)
                    is_mouse_down = True
                    pygame.display.flip()
                elif event.type == pygame.MOUSEBUTTONUP:
                    is_mouse_down = False
                elif event.type == pygame.MOUSEMOTION:
                    if is_mouse_down:
                        self.process_mouse_event(event.pos)
                        pygame.display.flip()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode == "f" or event.unicode == "F":
                        self.map.turn_all_farms()
                        self.map.draw(self.screen, 640)
                        pygame.display.flip()
                    elif event.unicode == "c" or event.unicode == "C":
                        self.map.clear()
                        self.map.draw(self.screen, 640)
                        pygame.display.flip()

    def process_mouse_event(self, event) -> None:
        global selectedCellType
        if event[0] > 640:

            pos = event[0] - 640
            pos /= 66
            pos = int(pos)

            if 60 <= event[1] <= 126:
                if pos == 0:
                    self.selectedCellType = Application.TYPE_WATER_SALT
                elif pos == 1:
                    self.selectedCellType = Application.TYPE_WATER_FRESH
                else:
                    self.selectedCellType = Application.TYPE_WATER_DEEP
            elif 172 <= event[1] <= 238:
                if pos == 0:
                    self.selectedCellType = Application.TYPE_FARM_BARREN
                elif pos == 1:
                    self.selectedCellType = Application.TYPE_FARM_FERTILE
                elif pos == 2:
                    self.selectedCellType = Application.TYPE_FARM_FERTILE_PLUS
            elif 278 <= event[1] <= 344:
                if pos == 0:
                    self.selectedCellType = Application.TYPE_RES_ROCK
                elif pos == 1:
                    self.selectedCellType = Application.TYPE_RES_STONE
                elif pos == 2:
                    self.selectedCellType = Application.TYPE_RES_IRON
            elif 384 <= event[1] <= 450:
                if pos == 0:
                    self.selectedCellType = Application.TYPE_TREE_TREE
                elif pos == 1:
                    self.selectedCellType = Application.TYPE_TREE_NOTREE
        else:
            tile_factor = self.map.width / 640.0
            tile_x = self.map.width - int(event[0] * tile_factor) - 1
            tile_y = int(event[1] * tile_factor)
            selected_tile = self.map.tiles[tile_y * self.map.width + tile_x]
            if self.selectedCellType == Application.TYPE_WATER_DEEP:
                selected_tile["type"]["value__"].update(self.map.file, 3)
                selected_tile["deepWater"].update(self.map.file, True)
            elif self.selectedCellType == Application.TYPE_WATER_FRESH:
                selected_tile["type"]["value__"].update(self.map.file, 3)
                selected_tile["deepWater"].update(self.map.file, False)
                selected_tile["saltWater"].update(self.map.file, False)
            elif self.selectedCellType == Application.TYPE_WATER_SALT:
                selected_tile["type"]["value__"].update(self.map.file, 3)
                selected_tile["deepWater"].update(self.map.file, False)
                selected_tile["saltWater"].update(self.map.file, True)
            elif self.selectedCellType == Application.TYPE_FARM_BARREN:
                selected_tile["type"]["value__"].update(self.map.file, 0)
                selected_tile["fertile"].update(self.map.file, 0)
            elif self.selectedCellType == Application.TYPE_FARM_FERTILE:
                selected_tile["type"]["value__"].update(self.map.file, 0)
                selected_tile["fertile"].update(self.map.file, 1)
            elif self.selectedCellType == Application.TYPE_FARM_FERTILE_PLUS:
                selected_tile["type"]["value__"].update(self.map.file, 0)
                selected_tile["fertile"].update(self.map.file, 2)
            elif self.selectedCellType == Application.TYPE_RES_ROCK:
                selected_tile["type"]["value__"].update(self.map.file, 4)
            elif self.selectedCellType == Application.TYPE_RES_STONE:
                selected_tile["type"]["value__"].update(self.map.file, 2)
            elif self.selectedCellType == Application.TYPE_RES_IRON:
                selected_tile["type"]["value__"].update(self.map.file, 5)
            elif self.selectedCellType == Application.TYPE_TREE_TREE:
                selected_tile["amount"].update(self.map.file, 3)
            elif self.selectedCellType == Application.TYPE_TREE_NOTREE:
                selected_tile["amount"].update(self.map.file, 0)

            self.map.draw(self.screen, 640)


if __name__ == "__main__":
    app = Application()
    app.main_loop()
