from contextlib import suppress
import os
import re

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout

from ..constants import MAPS, IMAGEROOT, OUTPUTROOT
# NOTE: helpers also loads a kv file for widgets used.
from ..helpers import filename_fmt, text_fmt, copyfile


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/maps.kv")


# 888b     d888  .d8888b.  8888888b.
# 8888b   d8888 d88P  Y88b 888   Y88b
# 88888b.d88888 888    888 888    888
# 888Y88888P888 888        888   d88P
# 888 Y888P 888 888  88888 8888888P"
# 888  Y8P  888 888    888 888 T88b
# 888   "   888 Y88b  d88P 888  T88b
# 888       888  "Y8888P88 888   T88b

class MapManager(BoxLayout):
    def __init__(self, *args, attackers="None", mapstyle="Strips",
                 mapset=[], current=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = None

        def finish(dt):
            # Fix: Wait for instantiation to finish before accessing ids.
            self.attackers.text = attackers
            self.mapstyle.text = mapstyle
            for child in mapset:
                self.addmap(child)
            # children is a stack, so current=0 is actually the last item.
            # The export function sets this accordingly.
            nonlocal current
            if current is not None:
                current = self.mapset.children[current]
            # Set the current map last to override autocurrentmap() calls.
            self.setcurrentmap(current)
            self.draw()

        Clock.schedule_once(finish)  # https://stackoverflow.com/a/26918422/

    @property
    def style(self):
        return self.mapstyle.text

    def addmap(self, instance=None):
        # Add a map, either by dict args or a MapWidget already instantiated.
        if instance is None:
            instance = {}  # Allow NoneType to be instantiated below.
        if isinstance(instance, dict):
            instance = MapWidget(**instance)  # Create from args.
        self.mapset.add_widget(instance)

        # Not drawing map here - use final() sub-function after setting values.
        self.autocurrentmap()

    def setcurrentmap(self, map):
        Logger.debug("Maps: Setting map {} current (was {})".format(
            map.index1 if map is not None else "empty",
            self.current.index1 if self.current is not None else "empty"))

        if self.current is map:
            return  # Skip superfluous redraws.

        self.current = map
        for child in self.mapset.children:
            child.iscurrent = child is map
        self.draw_live()  # Must always be called; child won't trigger it.

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


# 888       888 8888888 8888888b.   .d8888b.  8888888888 88888888888
# 888   o   888   888   888  "Y88b d88P  Y88b 888            888
# 888  d8b  888   888   888    888 888    888 888            888
# 888 d888b 888   888   888    888 888        8888888        888
# 888d88888b888   888   888    888 888  88888 888            888
# 88888P Y88888   888   888    888 888    888 888            888
# 8888P   Y8888   888   888  .d88P Y88b  d88P 888            888
# 888P     Y888 8888888 8888888P"   "Y8888P88 8888888888     888

class MapWidget(BoxLayout):
    def __init__(self, *args, pool="", map="",
                 score1="0", score2="0", final=False, **kwargs):

        # WARNING
        # It is expected that a MapWidget will be immediately added to a
        # MapManager (before the caller returns). If this is not the case, then
        # the widget won't be rendered (when the Clock event fires), and this
        # code will throw a myriad of exceptions.

        super().__init__(*args, **kwargs)
        # Cached switch states. If the callback fires and it's a mismatch,
        # then do callback stuff, otherwise suppress.
        self.cache_current = False
        self.cache_final = final

        def finish(dt):
            # Fix: Wait for instantiation to finish before accessing ids.
            # Set switches to their cached values, only triggers callbacks if
            # actually changing, and doesn't override changes before this func.
            self.current.active = self.cache_current
            self.pool.text = pool  # Triggers map selector update.
            self.pool.values = MAPS.keys()
            self.map.text = map
            self.score1.text = score1
            self.score2.text = score2
            self.final.active = self.cache_final

            self.draw()  # Draw images once all settings are correct.
            # self.manager.autocurrentmap() can't be here, it would override
            # the final setcurrentmap() call in MapManager.__init__.

        Clock.schedule_once(finish)  # https://stackoverflow.com/a/26918422/

    @property
    def iscurrent(self):
        # Returning cached value ensures up-to-date even before final().
        return self.cache_current

    @iscurrent.setter
    def iscurrent(self, val):
        self.cache_current = val
        self.current.active = val  # Only fires callback if changing.

    @property
    def isfinal(self):
        # Returning cached value ensures up-to-date even before final().
        # e.g. autocurrentmap() could pull the False value and set current,
        # deactivating the final switch erroneously.
        # (Anecdotally, callbacks don't seem to fire until *after* final(), so
        # this may be a non-issue, but it doesn't hurt to safeguard.)
        return self.cache_final

    @isfinal.setter
    def isfinal(self, val):
        self.cache_final = val
        self.final.active = val  # Only fires callback if changing.

    @property
    def index1(self):
        # Return the 1-indexed position of this element in the parent.
        # Good for filenames, especially if being used by non-programmers.
        if self.parent is None:
            return None  # manager.current maintains reference and may access.
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
        self.draw_map()  # Desat mode for non-current maps.

        # current and final cannot both be enabled; if one is switched on, it
        # must disable the other. Setting the switch via code still triggers
        # callbacks (if changing), so the two switches would keep changing each
        # other recursively. By storing the cached value, we can ignore known
        # callbacks. Code above runs regardless, e.g. redraw should occur on
        # any change, no matter whether we manually set the value or not.
        if on == self.cache_current:
            return
        self.cache_current = on  # Update the cached value to match current.

        self.manager.setcurrentmap(self if on else None)
        if on and self.isfinal:
            self.isfinal = False

    def callback_final(self, on):
        self.draw_result()  # Needed to trigger updates for manager totals.

        # Same callback pattern as per callback_current.
        # Both final and current, when enabled, disable the other.
        if on == self.cache_final:
            return
        self.cache_final = on  # Update the cached value to match final.

        self.manager.autocurrentmap()  # Need to update current switch.

    def callback_delete(self):
        # TODO Some modal here.
        manager = self.manager  # Keep reference after deletion.
        self.parent.remove_widget(self)
        manager.autocurrentmap()
        manager.draw()  # Clean up.

    def callback_pool(self, pool):
        self.map.values = MAPS[pool]
        old = self.map.text
        self.map.text = ""
        self.draw_pool()
        if not old:
            self.draw_map()  # map.on_text won't fire (text didn't change).

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
        if not self.iscurrent and style == "strips":
            style += " desat"  # Only possible for "strips" at this time.

        # Generate map name, or use the map pool.
        map = filename_fmt(self.map.text)  # Map (image) name.
        if not map:
            # If no map, use the pool image instead.
            # No map and no pool? No image (copyfile places "missing.png").
            map = filename_fmt("_pool " + self.pool.text)

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