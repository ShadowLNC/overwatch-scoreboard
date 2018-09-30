from contextlib import suppress
import os
import re

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout

from ..constants import MAPS, IMAGEROOT, OUTPUTROOT
# NOTE: helpers also loads a kv file for widgets used.
from ..helpers import LoadableWidget, filename_fmt, text_fmt, copyfile
from .teams import TeamWidget


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/maps.kv")


# 888b     d888  .d8888b.  8888888b.
# 8888b   d8888 d88P  Y88b 888   Y88b
# 88888b.d88888 888    888 888    888
# 888Y88888P888 888        888   d88P
# 888 Y888P 888 888  88888 8888888P"
# 888  Y8P  888 888    888 888 T88b
# 888   "   888 Y88b  d88P 888  T88b
# 888       888  "Y8888P88 888   T88b

class MapManager(LoadableWidget, BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = None

    @classmethod
    def from_factory(cls, attackers="", mapstyle="Strips",
                     mapset=[], current=None, **kwargs):
        self = super().from_factory(**kwargs)

        self.attackers.text = attackers
        self.mapstyle.text = mapstyle
        for child in mapset:
            self.addmap(**child)

        # children is a stack, so current=0 is actually the last item.
        # The export function sets this accordingly.
        # Set the current map last to override autocurrentmap() calls.
        if current is not None:
            current = self.mapset.children[current]
        self.setcurrentmap(current)

        self.manager.livemanager.sync(self)  # Listen for teams/swap events.
        self.draw()
        return self

    @property
    def style(self):
        return self.mapstyle.text

    def addmap(self, **data):
        # Instantiate from args - widget inherits LoadableWidget self-adding.
        MapWidget.from_factory(**data, parent=self.mapset, manager=self)
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

    def swapteams(self):
        for child in self.mapset.children:
            child.swapteams()  # Swap map scores.

        # Swap the attackers value. Use existing if lookup fails (no change).
        # This also applies if there's no currently attacking team (no switch).
        swap = {"Team 1": "Team 2", "Team 2": "Team 1"}
        with suppress(KeyError):
            # EAFP means .get() is NOT preferred here.
            self.attackers.text = swap[self.attackers.text]

    def callback_event(self, event):
        if event == "swap":
            self.swapteams()
        elif event == "teamchange":
            # Indirectly calls draw_result().
            for child in self.mapset.children:
                child.draw_result()

    def callback_mapstyle(self):
        for child in self.mapset.children:
            child.draw_map()
        # draw_livemap is called from child.draw_map() unless current is None.
        if self.current is None:
            self.draw_livemap()

    def draw_livepool(self):
        prefix = "{}/livemappool.".format(OUTPUTROOT)
        targets = ["png", "txt"]  # Suffixes.
        if self.current is not None:
            self.current.draw_pool(prefix, *targets)
        else:
            for i in targets:
                with suppress(FileNotFoundError):
                    os.remove(prefix + i)

    def draw_livemap(self):
        prefix = "{}/livemap.".format(OUTPUTROOT)
        targets = ["png", "txt"]  # Suffixes.
        if self.current is not None:
            self.current.draw_map(prefix, *targets)
        else:
            for i in targets:
                with suppress(FileNotFoundError):
                    os.remove(prefix + i)

    def draw_livescore(self, team=None):
        if team is None:
            for team in (1, 2):
                self.draw_livescore(team)  # Draw for all teams.

        # Formatted target becomes a format string accepting team only.
        target = "{}/livemapscore{{team}}.txt".format(OUTPUTROOT)
        if self.current is not None:
            self.current.draw_score(team=team, target=target)
        else:
            with suppress(FileNotFoundError):
                os.remove(target.format(team=team))

    def draw_result(self):
        prefix = "{}/match".format(OUTPUTROOT)

        teams = [0] * 3  # Each index represents that team (0 is draws)
        for child in self.mapset.children:
            teams[child.winner] += 1
        for team, wins in enumerate(teams):
            if not team:
                continue  # Skip team "0" (draws).
            target = "totalscore{}.txt".format(team)
            with open(prefix + target, 'w') as f:
                f.write(text_fmt(wins))

        # Get the team with the maximum score, then use that to draw winner.
        team = None  # Winning team.
        teams = teams[1:]  # Remove draws.
        best = max(teams)
        if teams.count(best) == 1:
            # Only attempt to determine winner if there is a clear winner.
            best = teams.index(best) + 1  # 1-indexed.
            with suppress(IndexError):
                # IndexError suppressed in case LiveTeam widget is missing.
                # Children are in reverse order hence negative index.
                team = self.manager.livemanager.teamset.children[-best].team

        prefix += "winner"
        logo = prefix + "logo.png"
        color = prefix + "color.html"
        text = prefix + "name.txt"
        if team is not None:
            team.draw_logo(logo)
            team.draw_color(color)
            team.draw_name(text)
        else:
            # Either no winner, or the winning team is not set in Live tab.
            # Skip second item as HTML cannot be removed.
            for i in [logo, text]:
                with suppress(FileNotFoundError):
                    os.remove(i)
            # Placeholder HTML to retain refresh rate.
            TeamWidget.make_color(color)

    def draw_positions(self):
        for team in (1, 2):
            target = "{}/liveposition{}.png".format(OUTPUTROOT, team)

            # We are allowing positions to be set even if no current map.
            if self.attackers.text:
                if self.attackers.text == "Team " + str(team):
                    pos = "attack"
                else:
                    pos = "defense"

                pos = filename_fmt(pos)
                infile = "{}/game/positions/{}.png".format(IMAGEROOT, pos)
                copyfile(infile, target)
            else:
                with suppress(FileNotFoundError):
                    os.remove(target)  # Should we copy "none" in instead?

    def draw_live(self):
        self.draw_livepool()
        self.draw_livemap()
        self.draw_livescore()  # team=None causes all to redraw.
        self.draw_result()
        self.draw_positions()

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

class MapWidget(LoadableWidget, BoxLayout):
    @classmethod
    def from_factory(cls, pool="", map="", score1="0", score2="0", final=False,
                     **kwargs):

        self = super().from_factory(**kwargs)
        # Cached switch states. If the callback fires and it's a mismatch,
        # then do callback stuff, otherwise suppress.
        self.cache_current = False
        self.cache_final = final

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
        return self

    @property
    def iscurrent(self):
        # Use switch value not cache, otherwise this is outdated for callbacks.
        return self.current.active

    @iscurrent.setter
    def iscurrent(self, val):
        self.cache_current = val
        self.current.active = val  # Only fires callback if changing.

    @property
    def isfinal(self):
        # Use switch value not cache, otherwise this is outdated for callbacks.
        return self.final.active

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

    # The following are all event-driven methods. Draw methods always output
    # output; callback functions may call draw methods, but do not directly
    # output. Both callback and draw functions may have KVlang triggers.

    def swapteams(self):
        # This will fire any callbacks as necessary (unless drawn, since no
        # change in values, but no redraw necessary in that instance).
        # `a, b = b, a` swaps values.
        self.score1.text, self.score2.text = self.score2.text, self.score1.text

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

    def draw_pool(self, prefix=None, image=None, text=None):
        if prefix is None:
            # Set prefix and overwrite image/text fragments.
            prefix = "{}/map{}pool.".format(OUTPUTROOT, self.index1)
            image = "png"
            text = "txt"

            if self.iscurrent:
                # This is a standard call and we should call the live updater.
                self.manager.draw_livepool()

        if image is not None:
            pool = filename_fmt(self.pool.text)
            infile = "{}/game/modes/{}.png".format(IMAGEROOT, pool)
            copyfile(infile, prefix + image)

        if text is not None:
            with open(prefix + text, 'w') as f:
                f.write(text_fmt(self.pool.text))

    def draw_map(self, prefix=None, image=None, text=None):
        if prefix is None:
            # Set prefix and overwrite image/text fragments.
            prefix = "{}/map{}.".format(OUTPUTROOT, self.index1)
            image = "png"
            text = "txt"

            if self.iscurrent:
                # This is a standard call and we should call the live updater.
                self.manager.draw_livemap()

        if image is not None:
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
            copyfile(infile, prefix + image, delete_if_missing=False)

        if text is not None:
            with open(prefix + text, 'w') as f:
                f.write(text_fmt(self.map.text))

    def draw_score(self, team=None, target=None):
        if team is None:
            for team in (1, 2):
                self.draw_score(team)  # Draw for all teams.

        if target is None:
            # Formatted target becomes a format string accepting team only.
            target = "{}/map{}score{{team}}.txt".format(OUTPUTROOT,
                                                        self.index1)

            if self.iscurrent:
                # Current map and standard redraw? Call the live updater too.
                self.manager.draw_livescore(team)

        # Team is 1 or 2, depending on which score value was changed.
        target = target.format(team=team)
        with open(target, 'w') as f:
            text = getattr(self, "score{}".format(team))  # Input field.
            f.write(text_fmt(text.text))

        if self.isfinal:
            self.draw_result()

    def draw_result(self, prefix=None, logo=None, color=None, text=None):
        if prefix is None:
            prefix = "{}/map{}winner".format(OUTPUTROOT, self.index1)
            logo = "logo.png"
            color = "color.html"
            text = "name.txt"

            # Changing result changes totals... a bit inefficient to place it
            # here (ends up being called multiple times), but it does need to
            # be called (at least once) when a map's result changes.
            self.manager.draw_result()

        # Fetch the winning team, if one exists from livemanager.
        team = None
        if self.isfinal:
            with suppress(IndexError):
                # teamset.children is reversed, and self.winner is 1-indexed.
                # IndexError suppressed in case LiveTeam widget is missing.
                live = self.manager.manager.livemanager
                team = live.teamset.children[-self.winner].team

        if logo is not None:
            if team is not None:
                team.draw_logo(prefix + logo)
            else:
                with suppress(FileNotFoundError):
                    os.remove(prefix + logo)

        if color is not None:
            if team is not None:
                team.draw_color(prefix + color)
            else:
                # Placeholder HTML to retain refresh rate.
                TeamWidget.make_color(prefix + color)

        if text is not None:
            with open(prefix + text, 'w') as f:
                # The file is now truncated, if not final, write nothing.
                if self.isfinal:
                    data = ""
                    if team is not None:
                        data = team.name.text
                    elif self.winner != 0:
                        # We have a winner but no team.
                        data = "Team {}".format(self.winner)
                    else:
                        data = "Draw"

                    if data:
                        f.write(text_fmt(data))

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
