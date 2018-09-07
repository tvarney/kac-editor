#!/usr/bin/python3

import argparse
import time
import pygame
import shutil

from kac import colors
from kac.brush import Brush, BrushTile
from kac.extractor import parse_save_file, write_save_file
from kac.map import KacMap, MapWidget
from kac.gui import Container, Label, PushButton

import typing
if typing.TYPE_CHECKING:
    from kac.gui import Widget


class Application(object):
    def __init__(self) -> None:
        self.map = None
        self.gui = None
        self.map_widget = None
        self.parser = argparse.ArgumentParser(description="Kingdoms and Castles map editor")
        self.parser.add_argument("--input", "-i", help="The path to a KaC save file")
        self.parser.add_argument("--gui", "-g", help="Launches the GUI", action="store_true")
        self._run_gui = True
        self.save_file = None
        self.objects = None
        self.data = None
        self.screen = None
        self.small_font = None
        self.font = None
        self._last_widget = None
        self._brush = Brush()

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
        self.gui = Container(640, 0, 204, 640)
        self.map_widget = MapWidget(0, 0, 640, 640, self.map)
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 14)
        self.build_gui()

    def build_gui(self) -> None:
        gui = self.gui
        x, y, width, height = gui.bounds
        gui.add(Label(x, 30, "Water", self.font, width=width, centered=True))
        gui.add(PushButton(x + 2, y + 60, "Salt", self.font, width=66, height=66, action=self.action_water_salt))
        gui.add(PushButton(x + 70, y + 60, "Fresh", self.font, width=66, height=66, action=self.action_water_fresh))
        gui.add(PushButton(x + 138, y + 60, "Deep", self.font, width=66, height=66, action=self.action_water_deep))

        gui.add(Label(x, 136, "Land", self.font, width=width, centered=True))
        gui.add(PushButton(x + 2, y + 166, "Barren", self.font, width=66, height=66, action=self.action_land_barren))
        gui.add(PushButton(x + 70, y + 166, "Fertile", self.font, width=66, height=66, action=self.action_land_fertile))
        gui.add(PushButton(x + 138, y + 166, "Fertile+", self.font, width=66, height=66,
                           action=self.action_land_very_fertile))

        gui.add(Label(x, 242, "Resources", self.font, width=width, centered=True))
        gui.add(PushButton(x + 2, y + 272, "Rock", self.font, width=66, height=66, action=self.action_res_rock))
        gui.add(PushButton(x + 70, y + 272, "Stone", self.font, width=66, height=66, action=self.action_res_stone))
        gui.add(PushButton(x + 138, y + 272, "Iron", self.font, width=66, height=66, action=self.action_res_iron))

        gui.add(Label(x, 348, "Trees", self.font, width=width, centered=True))
        gui.add(PushButton(x + 1, y + 378, "Trees", self.font, width=66, height=66, action=self.action_trees))
        gui.add(PushButton(x + 70, y + 378, "No Trees", self.font, width=66, height=66, action=self.action_no_trees))

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

        self.map_widget.render(self.screen)
        self.gui.render(self.screen)

        self.screen.blit(self.small_font.render('Press F to turn all farms fertile+', False, colors.White), (640, 490))
        self.screen.blit(self.small_font.render('Press C to clear the map', False, colors.White), (640, 510))
        # self.map.draw(self.screen, 640)
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
                    x, y = event.pos[0], event.pos[1]
                    gui = self.gui  # type: Container
                    if gui.contains((x, y)):
                        gui.click(x, y)
                        if gui.dirty:
                            gui.render(self.screen)
                    else:
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

    def _handle_click(self, widget: 'Widget', cell_type: int):
        if self._last_widget is widget:
            return

        if self._last_widget is not None:
            last = self._last_widget  # type: Widget
            last.set_active(False)

        self._brush.tile = cell_type
        self._last_widget = widget
        widget.set_active(True)

    def action_water_salt(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.WaterSalt)

    def action_water_fresh(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.WaterFresh)

    def action_water_deep(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.WaterDeep)

    def action_land_barren(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.LandBarren)

    def action_land_fertile(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.LandFertile)

    def action_land_very_fertile(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.LandVeryFertile)

    def action_res_rock(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.ResourceRock)

    def action_res_stone(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.ResourceStone)

    def action_res_iron(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.ResourceIron)

    def action_trees(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.ResourceTree)

    def action_no_trees(self, widget: 'Widget') -> None:
        self._handle_click(widget, BrushTile.ResourceNoTree)

    def process_mouse_event(self, event) -> None:
        if event[0] > 640:

            pos = event[0] - 640
            pos /= 66
            pos = int(pos)
        else:
            tile_factor = self.map.width / 640.0
            tile_x = self.map.width - int(event[0] * tile_factor) - 1
            tile_y = int(event[1] * tile_factor)
            self._brush.apply(self.map, tile_x, tile_y)
            self.map_widget.render(self.screen)


if __name__ == "__main__":
    app = Application()
    app.main_loop()
