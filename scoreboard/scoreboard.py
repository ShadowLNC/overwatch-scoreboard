import json
import os

import kivy.app
from kivy.logger import Logger
# from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel

from .constants import OUTPUTROOT, SAVEFILE
# Load kv and classes below.
from .components.live import LiveManager
from .components.maps import MapManager
from .components.custom import CustomDataManager
from .components.teams import TeamManager


# TODO some modal confirmation... or none at all?
# Window.bind(on_request_close=lambda *a, **kw: True)


# Possible settings to add in future:
# Auto update current map on/off
# Details of current game
# Liveupdate vs button
# Livesave vs button
# Lowercase/uppercase/titlecase/null transform on text
# Load custom saves/set custom savefile


class View(TabbedPanel):
    @classmethod
    def from_save(cls):
        self = cls()

        # Load saved state; defaults listed below as well.
        state = {}
        if os.path.isfile(SAVEFILE):
            Logger.info("Scoreboard: Loading saved state...")
            with open(SAVEFILE) as f:
                try:
                    state = json.load(f)
                except json.decoder.JSONDecodeError:
                    Logger.error(
                        "Scoreboard: Failed to load JSON, defaulting...")

        # Order is important because of dependencies.
        self.customdatamanager = CustomDataManager.from_factory(
            **state.get('customdatamanager', {}),
            parent=self.tabcustom, manager=self)
        self.teammanager = TeamManager.from_factory(
            **state.get('teammanager', {}),
            parent=self.tabteams, manager=self)
        self.livemanager = LiveManager.from_factory(
            **state.get('livemanager', {}),
            parent=self.tablive, manager=self)
        self.mapmanager = MapManager.from_factory(
            **state.get('mapmanager', {}),
            parent=self.tabmaps, manager=self)

        return self

    def save(self):
        with open(SAVEFILE, 'w') as f:
            json.dump(self.__export__(), f)

    def __export__(self):
        return {
            'livemanager': self.livemanager.__export__(),
            'customdatamanager': self.customdatamanager.__export__(),
            'mapmanager': self.mapmanager.__export__(),
            'teammanager': self.teammanager.__export__(),
        }


class Scoreboard(kivy.app.App):
    def build(self):
        return View.from_save()


if __name__ == '__main__':
    # Ensure we have the output folders, prevent crashes.
    if not os.path.isdir(OUTPUTROOT + "/custom"):
        Logger.info("Scoreboard: Creating output folder...")
        os.makedirs(OUTPUTROOT + "/custom")  # Make all "prerequisites" too.

    s = Scoreboard()
    s.run()
    s.root.save()  # Until we have a save event bubble up.
