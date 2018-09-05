import os

from kivy.graphics import Color
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from ..constants import IMAGEROOT, OUTPUTROOT
from ..helpers import LoadableWidget


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/live.kv")


class LiveManager(LoadableWidget, BoxLayout):
    @classmethod
    def from_factory(cls, title="", herostyle="Portrait", herofilter=True,
                     team1={}, team2={}, **kwargs):
        self = super().from_factory(**kwargs)

        self.title.text = title
        self.herostyle.text = herostyle
        self.herofilter.active = herofilter

        # Sets up self.teamlist and there's no LiveTeam objects to draw yet.
        self.callback_teamlist()

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

    def callback_teamlist(self, draw=True):
        # Disallow empty team names. If duplicate names, last takes priority.
        teamlist = {"": None}
        for team in reversed(self.manager.teammanager.teamset.children):
            name = team.name.text
            if name:
                teamlist[name] = team

        self.teamlist = teamlist
        for child in self.teamset.children:
            child.draw_teamselect()

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
    @classmethod
    def from_factory(cls, teamname="", title="Team", background=(0, 0, 0, 1),
                     **kwargs):
        self = super().from_factory(**kwargs)

        self.canvas.before.insert(0, Color(*background))
        self.title.text = title

        # Setup the current team (name/object), default to None if missing.
        self.team = self.manager.teamlist.get(teamname, None)
        self.draw_teamselect()  # Draw now that we have set self.team.

        for i in range(6):
            pass  # TODO Add the LivePlayer widgets.

        return self

    @property
    def index1(self):
        # 1-indexed position of this widget in its parent.
        return len(self.parent.children) - self.parent.children.index(self)

    def callback_teamselect(self, value):
        # This shouldn't KeyError, we have limited teamselect values.
        team = self.manager.teamlist[value]
        if team != self.team:
            # Don't redraw unless necessary (could be just name change).
            self.draw_players()
            self.team = team

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

    def draw_players(self):
        # We could delete and regenerate the hero selectors, this means there
        # would not be "inert" selectors for players that don't exist.
        pass

    def __export__(self):
        return {
            'teamname': self.teamselect.text,
        }


class LivePlayer(BoxLayout):
    @property
    def manager(self):
        return self.parent.root

    @property
    def index1(self):
        # 1-indexed position of this widget in its parent.
        return len(self.parent.children) - self.parent.children.index(self)

    def callback_hero(self, hero):
        self.teamplayer.hero = hero
        self.draw_hero()

    def draw_hero(self):
        target = "{}/team{}hero{}".format(OUTPUTROOT,
                                          self.manager.index1, self.index1)
        # infile = "{}/heroes/{}/{}".format(IMAGEROOT, herostyle, )

    def draw_user(self):
        pass

    def draw_role(self):
        pass

    def draw(self):
        self.draw_user()
        self.draw_role()
        self.draw_hero()
