import json
import os

import kivy
import kivy.app

from kivy.clock import Clock
from kivy.logger import Logger
# from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel

from constants import OUTPUTROOT, SAVEFILE
# Load kv and classes below.
import helpers
from maps import MapManager
from teams import TeamManager


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load saved state; defaults listed below as well.
        state = {}
        if os.path.isfile(SAVEFILE):
            Logger.info("Scoreboard: Loading saved state...")
            with open(SAVEFILE) as f:
                state = json.load(f)

        # Order is important because of dependencies.
        self.teammanager = TeamManager(**state.get('teammanager', {}))
        self.mapmanager = MapManager(**state.get('mapmanager', {}))

        def finish(dt):
            # Fix: Wait for KVlang load before accessing ids.
            self.tabmaps.add_widget(self.mapmanager)
            self.tabteams.add_widget(self.teammanager)

        Clock.schedule_once(finish)

    def save(self):
        with open(SAVEFILE, 'w') as f:
            json.dump(self.__export__(), f)

    def __export__(self):
        return {
            'mapmanager': self.mapmanager.__export__(),
            'teammanager': self.teammanager.__export__(),
        }


class Scoreboard(kivy.app.App):
    def build(self):
        return View()


if __name__ == '__main__':
    # Ensure we have the output folder, prevent crashes.
    if not os.path.isdir(OUTPUTROOT):
        Logger.info("Scoreboard: Creating output folder...")
        os.makedirs(OUTPUTROOT)  # Make all "prerequisite" directories too.

    s = Scoreboard()
    s.run()
    s.root.save()  # Until we have a save event bubble up.
