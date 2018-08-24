import os

import kivy
import kivy.app

from kivy.logger import Logger
# from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel

from constants import OUTPUTROOT
# Load kv and classes below.
import helpers
import maps


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
    pass


class Scoreboard(kivy.app.App):
    def build(self):
        return View()


if __name__ == '__main__':
    # Ensure we have the output folder, prevent crashes.
    if not os.path.isdir(OUTPUTROOT):
        Logger.info("Scoreboard: Creating output folder...")
        os.makedirs(OUTPUTROOT)  # Make all "prerequisite" directories too.

    Scoreboard().run()
