import os
import re
import shutil
import unicodedata

from contextlib import suppress

import kivy
import kivy.app

# from kivy.uix.button import Label
# from kivy.lang import Builder  # By default for Scoreboard(kivy.app.App)
from kivy.uix.tabbedpanel import TabbedPanel
# from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
# from kivy.properties import ObjectProperty
# from kivy.logger import Logger
from kivy.clock import Clock

# Builder.load_file("scoreboard.kv")

from constants import MAPS, IMAGEROOT, OUTPUTROOT


def filename_fmt(val):
    val = unicodedata.normalize('NFD', val)  # Normalise, then strip others.
    val = str(bytes(val, encoding='utf-8', errors='ignore'), encoding='ascii')
    val = val.lower()
    return re.sub(r"[^\w ]", "", val)


def text_fmt(val):
    return str(val).upper()


def copyfile(src, dest, delete_if_missing=True):
    # Prevent crashes by outputting a fallback if we can't get the file.
    try:
        shutil.copyfile(src, dest)
    except FileNotFoundError:
        # Either delete the image or default to a "missing" image.
        if delete_if_missing:
            with suppress(FileNotFoundError):
                os.remove(dest)
        else:
            shutil.copyfile(IMAGEROOT + "/missing.png", dest)


# TODO some modal confirmation... or none at all?
# Window.bind(on_request_close=lambda *a, **kw: True)


class MapManager(BoxLayout):
    def __init__(self, *args, attackers="", mapstyle="Strips",
                 mapset=[], current=None, **kwargs):
        # Logger.info("Mapwidget: " + str(args) + str(kwargs))
        super().__init__(*args, **kwargs)
        # IDs from kv-lang: mapset
        self.current = None

        def finish(dt):
            # Fix: Wait for instantiation to finish before accessing ids.
            self.attackers.text = attackers
            self.mapstyle.text = mapstyle
            for child in mapset:
                self.addmap(child)
            # children is a stack, so current=0 is actually the last item.
            # The export function sets this accordingly.
            _current = current
            if _current is not None:
                _current = self.mapset.children[current]
            self.setcurrentmap(current)
            self.draw()

        Clock.schedule_once(finish)  # https://stackoverflow.com/a/26918422/

    @property
    def style(self):
        return self.mapstyle.text

    def addmap(self, instance=None):
        # Add a map, either by dict args or a MapWidget already instantiated.
        if instance is None:
            instance = MapWidget()
        elif isinstance(instance, dict):
            instance = MapWidget(**instance)  # Import values.
        self.mapset.add_widget(instance)

        # Anything done here will be overridden by the final() sub-function in
        # the MapWidget constructor. Instead, place code in that sub-function.

    def setcurrentmap(self, map):
        self.current = map
        for child in self.mapset.children:
            child.iscurrent = child is map
        self.draw_live()

    def autocurrentmap(self):
        # The first non-final map will be the current one.
        for child in reversed(self.mapset.children):
            if not child.isfinal:
                self.setcurrentmap(child)
                return
        self.setcurrentmap(None)

    def callback_mapstyle(self):
        for child in self.mapset.children:
            child.draw_map()
        # draw_livemap is called from child.draw_map() unless current is None.
        if self.current is None:
            self.draw_livemap()

    def draw_livepool(self):
        target = "{}/livepool.png".format(OUTPUTROOT)
        if self.current is not None:
            self.current.draw_pool(target=target)
        else:
            with suppress(FileNotFoundError):
                os.remove(target)
            with suppress(FileNotFoundError):
                os.remove(target[:-3] + "txt")

    def draw_livemap(self):
        target = "{}/livemap.png".format(OUTPUTROOT)
        if self.current is not None:
            self.current.draw_map(target=target)
        else:
            with suppress(FileNotFoundError):
                os.remove(target)
            with suppress(FileNotFoundError):
                os.remove(target[:-3] + "txt")

    def draw_livescore(self, team=None):
        if team is None:
            for team in (1, 2):
                self.draw_livescore(team)  # Draw for all teams.

        # Formatted target becomes a format string accepting team only.
        target = "{}/livescore{{team}}.txt".format(OUTPUTROOT)
        if self.current is not None:
            self.current.draw_score(team=team, target=target)
        else:
            with suppress(FileNotFoundError):
                os.remove(target.format(team=team))

    def draw_liveresult(self):
        target = "{}/liveresult.txt".format(OUTPUTROOT)
        if self.current is not None:
            self.current.draw_result(target=target)
        else:
            with suppress(FileNotFoundError):
                os.remove(target)

    def draw_totalscore(self):
        teams = [0] * 3  # Each index represents that team (0 is draws)
        for child in self.mapset.children:
            teams[child.winner] += 1
        for team, wins in enumerate(teams):
            if not team:
                continue  # Skip team "0" (draws).
            target = "{}/livetotal{}.txt".format(OUTPUTROOT, team)
            with open(target, 'w') as f:
                f.write(text_fmt(wins))

    def draw_live(self):
        self.draw_livepool()
        self.draw_livemap()
        self.draw_livescore()  # team=None causes all to redraw.
        self.draw_liveresult()
        self.draw_totalscore()

    def draw(self):
        for child in self.mapset.children:
            child.draw()  # Full redraw of each child.
        self.draw_live()

        # I think we always want to do this if we're doing a full redraw.
        for file in os.listdir(OUTPUTROOT):
            # Grab the number of the map and compare to the max map number.
            check = re.match(r"^map(\d+)\D.*", file)
            if check and int(check[1]) > len(self.mapset.children):
                os.remove("{}/{}".format(OUTPUTROOT, file))

    def __export__(self):
        # mapset.children is a stack, so we have to reverse for export.
        # This means current=0 is the last item, init accounts for this.
        current = self.current
        if current is not None:
            current = self.mapset.children.index(current)
        return {
            'attackers': self.attackers.text,
            'mapstyle': self.style,
            'current': current,
            'mapset': [i.__export__() for i in reversed(self.mapset.children)],

        }


class MapWidget(BoxLayout):
    def __init__(self, *args, pool="", map="",
                 score1="0", score2="0", final=False, **kwargs):

        # WARNING
        # It is expected that a MapWidget will be immediately added to a
        # MapManager (before the caller returns). If this is not the case, then
        # the widget won't be rendered (when the Clock event fires), and this
        # code will throw a myriad of exceptions.

        # Logger.info("Mapwidget: " + str(args) + str(kwargs))
        super().__init__(*args, **kwargs)
        self.suppress_callback_current = False
        self.suppress_callback_final = True  # Suppress for init.

        def finish(dt):
            # Fix: Wait for instantiation to finish before accessing ids.
            self.iscurrent = False  # May be set later.
            self.pool.text = pool  # Triggers map selector update.
            self.pool.values = MAPS.keys()
            self.map.text = map
            self.score1.text = score1
            self.score2.text = score2
            self.final.active = final  # Do we need callback protection here?

            # The following code ought to be in the MapManager.addmap method,
            # but cannot be as this finish() sub-function overrides set values.
            self.draw()
            self.manager.autocurrentmap()

        Clock.schedule_once(finish)  # https://stackoverflow.com/a/26918422/

    @property
    def iscurrent(self):
        return self.current.active

    @iscurrent.setter
    def iscurrent(self, val):
        if self.current.active != val:
            # Ensure it needs changed, prevent unnecessary redraw.
            self.suppress_callback_current = True
            self.current.active = val

    @property
    def isfinal(self):
        return self.final.active

    @property
    def index1(self):
        # Return the 1-indexed position of this element in the parent.
        # Good for filenames, especially if being used by non-programmers.
        siblings = self.parent.children
        return len(siblings) - siblings.index(self)

    @property
    def winner(self):
        # Returns number of the winning team (1-indexed). 0 is draw/incomplete.
        if not self.isfinal:
            return 0
        team1 = 0  # Defaults.
        team2 = 0
        with suppress(ValueError):
            # In case the user enters non-int.
            team1 = int(self.score1.text)
            team2 = int(self.score2.text)

        if team1 > team2:
            return 1
        elif team2 > team1:
            return 2
        else:
            return 0

    @property
    def manager(self):
        return self.parent.root

    # The following are all event-driven methods. Draw methods always output
    # output; callback functions may call draw methods, but do not directly
    # output. Both callback and draw functions may have KVlang triggers.

    def callback_current(self, on):
        if self.suppress_callback_current:
            # Updating the value also
            self.suppress_callback_current = False
            return

        self.manager.setcurrentmap(self if on else None)
        if on and self.final.active:
            self.final.active = False

    def callback_final(self, on):
        # This is only relevant if the final switch equals the current switch.
        # (They cannot be both on, and both off might set current on.)
        # NEW: If we turn it on then redraw too (in case no current map).

        self.draw_result()

        # TODO callback suppression for the init.
        # No need to suppress this callback; it will only turn off final when
        # current is on, so the if condition is already False.
        if on or not self.current.active:
            self.manager.autocurrentmap()

    def callback_delete(self):
        # TODO Some modal here.
        manager = self.manager  # Keep reference after deletion.
        self.parent.remove_widget(self)
        manager.autocurrentmap()
        manager.draw()  # Clean up.

    def callback_pool(self, pool):
        self.map.values = MAPS[pool]
        self.map.text = ""
        self.draw_pool()

    def draw_pool(self, target=None):
        custom = target is not None
        if not custom:
            target = "{}/map{}pool.png".format(OUTPUTROOT, self.index1)

        pool = filename_fmt(self.pool.text)
        infile = "{}/game/modes/{}.png".format(IMAGEROOT, pool)
        copyfile(infile, target)

        # Replace png with txt and print out the name.
        with open(target[:-3] + "txt", 'w') as f:
            f.write(text_fmt(self.pool.text))

        if not custom and self.iscurrent:
            # This is a standard call and we should call the live updater.
            self.manager.draw_livepool()

    def draw_map(self, target=None):
        custom = target is not None
        if not custom:
            target = "{}/map{}.png".format(OUTPUTROOT, self.index1)

        # Set the map image to the correct image.
        style = filename_fmt(self.manager.style)
        if self.isfinal:
            style += " desat"

        # Generate map name, or use the map pool, underscores must be allowed.
        map = filename_fmt(self.map.text)  # Map (image) name.
        if not map:
            # If no map, use the pool image instead.
            # No map and no pool? No image (copyfile places "missing.png").
            map = "_pool " + filename_fmt(self.pool.text)

        infile = "{}/maps/{}/{}.png".format(IMAGEROOT, style, map)
        target = target.format(OUTPUTROOT, self.index1)
        copyfile(infile, target, delete_if_missing=False)

        with open(target[:-3] + "txt", 'w') as f:
            f.write(text_fmt(self.map.text))

        if not custom and self.iscurrent:
            # This is a standard call and we should call the live updater.
            self.manager.draw_livemap()

    def draw_score(self, team=None, target=None):
        if team is None:
            for team in (1, 2):
                self.draw_score(team)  # Draw for all teams.

        custom = target is not None
        if not custom:
            # Formatted target becomes a format string accepting team only.
            target = "{}/map{}score{{team}}.txt".format(OUTPUTROOT,
                                                        self.index1)

        # Team is 1 or 2, depending on which score value was changed.
        target = target.format(team=team)
        with open(target, 'w') as f:
            text = getattr(self, "score{}".format(team))  # Input field.
            f.write(text_fmt(text.text))

        # Standard call? Call the live updater.
        if not custom and self.iscurrent:
            self.manager.draw_livescore(team)
        if self.isfinal:
            self.draw_result()

    def draw_result(self, target=None):
        custom = target is not None
        if not custom:
            target = "{}/map{}result.txt".format(OUTPUTROOT, self.index1)

        with open(target, 'w') as f:
            # The file is now blank regardless, so if not final, write nothing.
            if self.isfinal:
                win = self.winner  # 0 draw (not incomplete), else team number.
                if win != 0:
                    f.write(text_fmt("Team {}".format(win)))
                else:
                    f.write(text_fmt("Draw!"))

        if not custom and self.iscurrent:
            # This is a standard call and we should call the live updater.
            self.manager.draw_liveresult()
        self.manager.draw_totalscore()  # Changing the result changes totals.

    def draw(self):
        # Redraws all.
        self.draw_pool()
        self.draw_map()
        self.draw_score()
        self.draw_result()

    def __export__(self):
        return {
            'pool': self.pool.text,
            'map': self.map.text,
            'score1': self.score1.text,
            'score2': self.score2.text,
            'final': self.isfinal,
        }


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

    pass


if __name__ == '__main__':
    Scoreboard().run()
