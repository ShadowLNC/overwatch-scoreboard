from contextlib import suppress
import itertools
import os

from kivy.graphics import Color
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from ..constants import OUTPUTROOT, HEROES
from ..helpers import LoadableWidget, Synchronisable
from .teams import TeamWidget


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/live.kv")


class LiveManager(LoadableWidget, Synchronisable, BoxLayout):
    # We use Synchronisable so MapManager can listen for teamselect changes.

    @classmethod
    def from_factory(cls, title="", herostyle="Portraits", herofilter=True,
                     team1={}, team2={}, **kwargs):
        self = super().from_factory(**kwargs)

        self.title.text = title
        self.herostyle.text = herostyle
        self.herofilter.active = herofilter

        # Sets up self.teamlist and there's no LiveTeam objects to draw yet.
        self.manager.teammanager.sync(self)  # Sync for future changes.
        self.callback_teamset()

        # Auto added.
        LiveTeam.from_factory(
            title="Team 1 (Blue)",
            background=(0x15/255, 0x84/255, 0xb4/255, 1), **team1,
            parent=self.teamset, manager=self)
        LiveTeam.from_factory(
            title="Team 2 (Red)",
            background=(0xac/255, 0x10/255, 0x20/255, 1), **team2,
            parent=self.teamset, manager=self)

        return self

    def callback_title(self, value):
        # on_text fired on init is not a problem here (brief flicker).
        with open(OUTPUTROOT + "/livetitle.txt", 'w') as f:
            f.write(value)

    def callback_herostyle(self):
        for child in self.teamset.children:
            child.callback_herostyle()

    def callback_herofilter(self):
        for child in self.teamset.children:
            child.callback_herofilter()

    def callback_event(self, event):
        if event == "teamset":
            self.callback_teamset()  # We should recalc self.teamlist.
        else:
            super().callback_event(event)  # Else propagate up.

    # Called by TeamManager after we sync to it.
    def callback_teamset(self):
        # Disallow empty team names. If duplicate names, last takes priority.
        teamlist = {"": None}
        for team in reversed(self.manager.teammanager.teamset.children):
            name = team.name.text
            if name:
                teamlist[name] = team

        self.teamlist = teamlist
        for child in self.teamset.children:
            child.draw_teamselect()

    def callback_swap(self):
        # We swap the text values, triggering the callback (if changing).
        # The callback causes a redraw of the team.
        a = self.teamset.children[0].teamselect
        b = self.teamset.children[1].teamselect
        # `a, b = b, a` swaps values
        a.text, b.text = b.text, a.text
        self.callback_event("swap")  # Swap scores.

    def __export__(self):
        return {
            'title': self.title.text,
            'herofilter': self.herofilter.active,
            'herostyle': self.herostyle.text,
            # Not iterating as we know only 2 teams (setting colour manually).
            'team1': self.teamset.children[1].__export__(),
            'team2': self.teamset.children[0].__export__(),
        }


class LiveTeam(LoadableWidget, BoxLayout):
    # Drawable properties for an associated TeamWidget.
    # Class member as opposed to instance memeber since it's constant.
    PROPERTIES = ("name", "logo", "color", "sr")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.team = None

    @classmethod
    def from_factory(cls, teamname="", title="Team", background=(0, 0, 0, 1),
                     **kwargs):
        self = super().from_factory(**kwargs)

        self.canvas.before.insert(0, Color(*background))
        self.title.text = title

        # Setup the current team (name). This fires callback_teamselect.
        self.teamselect.text = teamname
        self.draw_teamselect()  # Draw now that we have set self.team.
        if self.team is None:
            self.draw()  # It won't draw otherwise (teamselect no change).

        # Add the LivePlayer widgets after we've drawn, prevent double redraw.
        players = self.teamroster
        for i in range(6):
            LivePlayer.from_factory(player=next(players),
                                    parent=self.players, manager=self)

        return self

    @property
    def index1(self):
        # 1-indexed position of this widget in its parent.
        return len(self.parent.children) - self.parent.children.index(self)

    @property
    def teamroster(self):
        # An iterator of self.team's PlayerWidgets, followed by repeating None.
        players = itertools.repeat(None)
        if self.team is not None:
            players = itertools.chain(
                reversed(self.team.rosterview.playerset.children), players)

        return players

    def callback_teamselect(self, value):
        # This shouldn't KeyError, we have limited teamselect values.
        try:
            team = self.manager.teamlist[value]
        except KeyError:
            # Fallback to None. The callback will fire again when changing.
            self.teamselect.text = ""
            return

        # If the team has changed, update sync and redraw.
        if team != self.team:
            if self.team is not None:
                self.team.desync(self)
            if team is not None:
                team.sync(self)
            self.team = team
            self.manager.callback_event("teamchange")
            self.draw()

        # Name has changed; we got a callback. However, callback_event() will
        # also be fired, so an extra self.draw_property("name") is unnecessary.

    def callback_herostyle(self):
        for player in self.players.children:
            player.draw_property("hero")

    def callback_herofilter(self):
        for player in self.players.children:
            player.draw_heroselect()

    def callback_event(self, event):
        if event in self.PROPERTIES:
            # Simulate a teamchange to cause redraw of map/match results.
            self.manager.callback_event("teamchange")
            self.draw_property(event)
        elif event == "roster":
            self.draw_roster()

    def draw_teamselect(self):
        # Sync the team selector against the team list.
        teamlist = self.manager.teamlist
        self.teamselect.values = teamlist.keys()

        # Try to maintain self.team sync (change self.teamlist.text)
        # if failure, set blank (don't guess from text value).
        # Both of these, if changing the text value, will trigger a redraw.
        if self.team is not None and self.team in teamlist.values():
            self.teamselect.text = self.team.name.text
        else:
            # Team no longer exists (or hidden by same name), set empty/None.
            self.teamselect.text = ""

    def draw_property(self, property):
        # name, logo, color, sr
        if property not in self.PROPERTIES:
            # If not str then this is gonna throw a TypeError trying to add.
            raise ValueError("Unknown property: " + property)

        filename = property
        if filename == "name":
            filename = ""  # "name" is not used in the target filename.

        # The extension is txt by default but we need to specify when it's not.
        extensions = {"logo": "png", "color": "html"}
        target = "{}/team{}{}.{}".format(OUTPUTROOT, self.index1, filename,
                                         extensions.get(property, "txt"))
        if self.team is not None:
            call = getattr(self.team, "draw_" + property)
            call(target)
        elif property == "color":
            # Maintain the refresh rate by putting an html file with no body.
            TeamWidget.make_color(target)
        else:
            with suppress(FileNotFoundError):
                os.remove(target)

    def draw_roster(self):
        # We could delete and regenerate the hero selectors, this means there
        # would not be "inert" selectors for players that don't exist.
        players = self.teamroster
        for child in reversed(self.players.children):
            child.player = next(players)

    def draw(self):
        # We don't call draw_teamselect here, it actually calls us.
        for property in self.PROPERTIES:
            self.draw_property(property)
        self.draw_roster()

    def __export__(self):
        return {
            'teamname': self.teamselect.text,
        }


class LivePlayer(LoadableWidget, BoxLayout):
    PROPERTIES = ("user", "role", "sr", "hero")

    @classmethod
    def from_factory(cls, player=None, **kwargs):
        self = super().from_factory(**kwargs)
        if player is not None:
            self.player = player
        else:
            self.draw()  # Fired by setting player, but only if changing.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._player = None

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        if player != self._player:

            if self._player is not None:
                self._player.desync(self)
            if player is not None:
                player.sync(self)

            self._player = player
            self.draw()

    @property
    def index1(self):
        # 1-indexed position of this widget in its parent.
        return len(self.parent.children) - self.parent.children.index(self)

    def callback_event(self, event):
        if event == "battletag":
            event = "user"

        if event in self.PROPERTIES:
            self.draw_property(event)

    def callback_hero(self, hero):
        # We do not need to sync if we just got a new self.player and set hero
        # text equal to the new player's hero (or if self.player is None).
        if self.player is not None and hero != self.player.hero:
            self.player.hero = hero
            self.draw_property("hero")

    def draw_heroselect(self):
        values = tuple()
        if self.player is not None:
            filter = None
            if self.manager.manager.herofilter.active:
                filter = self.player.role.text

            # Flex isn't a defined role and gets all the heroes (no filter).
            # If the filter switch is off, we also get all heroes.
            try:
                values = HEROES[filter]
            except KeyError:
                values = sum(HEROES.values(), [])  # Add the lists together.
        if values:
            # Only add blank option if we have selectable options.
            values = [""] + sorted(values)  # Should sort in case all heroes.
        self.hero.values = values

    def draw_property(self, property):
        if property not in self.PROPERTIES:
            # If not str then this is gonna throw a TypeError trying to add.
            raise ValueError("Unknown property: " + property)

        # Extra steps for certain properties.
        if property == "user":
            if self.player is not None:
                self.user.text = self.player.user
            else:
                self.user.text = "No Player"

        elif property == "role":
            if self.player is not None:
                self.role.text = self.player.role.text
            else:
                self.role.text = "No Role"

            self.draw_heroselect()

        elif property == "hero":
            # Won't trigger callback_hero() if no player/not actually changing.
            if self.player is not None:
                self.hero.text = self.player.hero
            else:
                self.hero.text = "No Hero"  # "role" removes selection values.

        # The extension is txt by default but we need to specify when it's not.
        extensions = {"role": "png", "hero": "png"}
        target = "{}/team{}{}{}.{}".format(
            # E.g. team1user1.txt (team number, property, player number).
            OUTPUTROOT, self.manager.index1, property, self.index1,
            extensions.get(property, "txt"))

        if self.player is not None:
            call = getattr(self.player, "draw_" + property)

            # Pass additional arguments as necessary.
            kwargs = {}
            if property == "hero":
                kwargs["style"] = self.manager.manager.herostyle.text
            call(target, **kwargs)

        else:
            with suppress(FileNotFoundError):
                os.remove(target)

    def draw(self):
        for property in self.PROPERTIES:
            # property = "role" calls draw_heroselect().
            self.draw_property(property)
