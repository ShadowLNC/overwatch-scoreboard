import re
import shutil
import unicodedata

import kivy
import kivy.app

# from kivy.uix.button import Label
# from kivy.lang import Builder  # By default for Scoreboard(kivy.app.App)
from kivy.uix.tabbedpanel import TabbedPanel
# from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
# from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.clock import Clock

# Builder.load_file("scoreboard.kv")

from constants import MAPS, IMAGEROOT, OUTPUTROOT


def filename_fmt(val):
    val = unicodedata.normalize('NFD', val)  # Normalise, then strip others.
    val = str(bytes(val, encoding='utf-8', errors='ignore'), encoding='ascii')
    val = val.lower()
    return re.sub(r"[^\w ]", "", val)


def text_fmt(val):
    return val.upper()


def copyfile(src, dest):
    # Prevent crashes by outputting a fallback if we can't get the file.
    try:
        shutil.copyfile(src, dest)
    except FileNotFoundError:
        shutil.copyfile(IMAGEROOT + "/fallback.png", dest)


# TODO some modal confirmation... or none at all?
# Window.bind(on_request_close=lambda *a, **kw: True)


class MapManager(BoxLayout):
    def __init__(self, *args, mapset=[], current=None, **kwargs):
        Logger.info("Mapwidget: " + str(args) + str(kwargs))
        super().__init__(*args, **kwargs)
        # IDs from kv-lang: mapset

        def finish(dt):
            # Fix: Wait for instantiation to finish before accessing ids.
            for i in mapset:
                self.addmap(i)
            # children is a stack, so current=0 is actually the last item.
            # The export function sets this accordingly.
            _current = current
            if _current is not None:
                _current = self.mapset.children[current]
            self.setcurrentmap(current)

        Clock.schedule_once(finish)  # https://stackoverflow.com/a/26918422/

    def addmap(self, instance=None):
        # Add a map, either by dict args or a MapWidget already instantiated.
        if instance is None:
            instance = MapWidget()
        elif isinstance(instance, dict):
            instance = MapWidget(**instance)  # Import values.
        self.mapset.add_widget(instance)
        self.autocurrentmap()

    def setcurrentmap(self, map):
        self.current = map
        for i in self.mapset.children:
            i.iscurrent = i is map

    def autocurrentmap(self):
        # The first non-final map will be the current one.
        for i in reversed(self.mapset.children):
            if not i.isfinal:
                self.setcurrentmap(i)
                return
        self.setcurrentmap(None)

    def __export__(self):
        # mapset.children is a stack, so we have to reverse for export.
        # This means current=0 is the last item, init accounts for this.
        current = self.current
        if current is not None:
            current = self.mapset.children.index(current)
        return {
            'current': current,
            'mapset': [m.__export__() for m in reversed(self.mapset.children)],
        }


class MapWidget(BoxLayout):
    def __init__(self, *args,
                 pool="", map="", score1="", score2="", final=False, **kwargs):
        # Logger.info("Mapwidget: " + str(args) + str(kwargs))
        super().__init__(*args, **kwargs)
        self.suppress_callback_current = False
        self.suppress_callback_final = True  # Suppress for init.

        def finish(dt):
            # Fix: Wait for instantiation to finish before accessing ids.
            self.iscurrent = False  # May be set by MapManager later.
            self.pool.text = pool  # Triggers map selector update.
            self.pool.values = MAPS.keys()
            self.map.text = map
            self.score1.value = score1
            self.score2.value = score2
            self.final.active = final  # Do we need callback protection here?

        Clock.schedule_once(finish)  # https://stackoverflow.com/a/26918422/

    @property
    def iscurrent(self):
        return self.current.active

    @property
    def isfinal(self):
        return self.final.active

    @property
    def mapstyle(self):
        return self.mapstyle.text

    @property
    def index1(self):
        # Return the 1-indexed position of this element in the parent.
        # Good for filenames, especially if being used by non-programmers.
        siblings = self.parent.children
        return len(siblings) - siblings.index(self)

    @iscurrent.setter
    def iscurrent(self, val):
        if self.current.active != val:
            # Ensure it needs changed, prevent unnecessary redraw.
            self.suppress_callback_current = True
            self.current.active = val

    def callback_current(self, on):
        if self.suppress_callback_current:
            # Updating the value also
            self.suppress_callback_current = False
            return

        self.parent.root.setcurrentmap(self if on else None)
        if on and self.final.active:
            self.final.active = False

    def callback_final(self, on):
        # This is only relevant if the final switch equals the current switch.
        # (They cannot be both on, and both off might set current on.)
        # NEW: If we turn it on then redraw too (in case no current map).

        fn = "{}/map{}result.txt".format(OUTPUTROOT, self.index1)
        with open(fn, 'w') as f:
            # The file is now blank regardless, so if not final, write nothing.
            if on:
                f.write("Winner")

        # No need to suppress this callback; it will only turn off final when
        # current is on, so the if condition is already False.
        if on or not self.current.active:
            self.parent.root.autocurrentmap()

    def callback_delete(self):
        # TODO Some modal here.
        parent = self.parent  # Keep reference after deletion.
        parent.remove_widget(self)
        parent.root.autocurrentmap()

    def callback_pool(self, pool):
        self.map.values = MAPS[pool]
        self.map.text = ""
        fn = "{}/game/modes/{}.png".format(IMAGEROOT, filename_fmt(pool))
        out = "{}/map{}pool.png".format(OUTPUTROOT, self.index1)
        copyfile(fn, out)  # Will replace.

    def callback_map(self, map):
        # Now set the map image to the correct image.
        style = filename_fmt(self.parent.root.mapstyle.text)
        if self.isfinal:
            style += " desat"
        # Generate map name, or use the map pool, underscores must be allowed.
        map = filename_fmt(map) or ("_pool " + filename_fmt(self.pool.text))
        fn = "{}/maps/{}/{}.png".format(IMAGEROOT, style, map)
        out = "{}/map{}.png".format(OUTPUTROOT, self.index1)
        copyfile(fn, out)  # Will replace.

    def callback_score1(self, value):
        fn = "{}/map{}score1.txt".format(OUTPUTROOT, self.index1)
        with open(fn, 'w') as f:
            f.write(value)

    def callback_score2(self, value):
        fn = "{}/map{}score2.txt".format(OUTPUTROOT, self.index1)
        with open(fn, 'w') as f:
            f.write(value)

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
