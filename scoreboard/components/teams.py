import os

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup

# NOTE: helpers also loads a kv file for widgets used.
from ..helpers import LoadableWidget


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/teams.kv")


class TeamManager(LoadableWidget, BoxLayout):
    @classmethod
    def from_factory(cls, teams=[], **kwargs):
        self = super().from_factory(**kwargs)

        for team in teams:
            self.addteam(**team)

        return self

    def addteam(self, **data):
        # Instantiate from args - widget inherits LoadableWidget self-adding.
        TeamWidget.from_factory(**data, parent=self.teamset, manager=self)

    def __export__(self):
        return {
            'teams': [i.__export__() for i in reversed(self.teamset.children)],
        }


class TeamWidget(LoadableWidget, BoxLayout):
    @classmethod
    def from_factory(cls, name="", logo="", teamcolor="#000000", sr="",
                     roster=[], **kwargs):
        self = super().from_factory(**kwargs)

        self.rosterview = RosterWidget.from_factory(roster=roster,
                                                    parent=None, manager=self)
        self.name.text = name
        self.logo.text = logo
        self.teamcolor.text = teamcolor
        self.sr.text = sr

        return self

    def callback_delete(self):
        self.parent.remove_widget(self)

    def __export__(self):
        return {
            'name': self.name.text,
            'logo': self.logo.text,
            'teamcolor': self.teamcolor.text,
            'sr': self.sr.text,
            # The roster is passed in RosterWidget instantiation.
            'roster': [i.__export__() for i in
                       reversed(self.rosterview.playerset.children)],
        }


class RosterWidget(LoadableWidget, Popup):
    @classmethod
    def from_factory(cls, roster=[], **kwargs):
        self = super().from_factory(**kwargs)

        for player in roster:
            self.addplayer(**player)

        return self

    def addplayer(self, **data):
        # Instantiate from args - widget inherits LoadableWidget self-adding.
        PlayerWidget.from_factory(**data, parent=self.playerset, manager=self)


class PlayerWidget(LoadableWidget, BoxLayout):
    @classmethod
    def from_factory(cls, username="", role="Flex", sr="", hero="", **kwargs):
        self = super().from_factory(**kwargs)

        self.user.text = username
        self.role.text = role
        self.sr.text = sr
        # Hero is used for the live tab only, but is part of player data.
        self.hero = hero

        return self

    def callback_delete(self):
        self.parent.remove_widget(self)

    def __export__(self):
        return {
            'username': self.user.text,
            'role': self.role.text,
            'sr': self.sr.text,
            'hero': self.hero,
        }
