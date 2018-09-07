from contextlib import suppress
import os

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup

# NOTE: helpers also loads a kv file for widgets used.
from ..helpers import LoadableWidget, Synchronisable, copyfile


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/teams.kv")


class TeamManager(LoadableWidget, Synchronisable, BoxLayout):
    @classmethod
    def from_factory(cls, teams=[], **kwargs):
        self = super().from_factory(**kwargs)

        for team in teams:
            self.addteam(**team)

        return self

    def addteam(self, **data):
        # Instantiate from args - widget inherits LoadableWidget self-adding.
        # The team name change will fire callback_teamset (plus it will fire on
        # the TextInput instantiation anyway, due to the Kivy bug #3588).
        # Since we ignore empty team names anyway, we do not rely on the bug.
        TeamWidget.from_factory(**data, parent=self.teamset, manager=self)

    def callback_teamset(self):
        # Teamset has changed, either deletion, addition, or (later) reorder.
        # This is just self.manager.livemanager but we need the Synchronisable
        # pattern since it won't be instantiated until after this object (the
        # factory method indirectly calls this).
        for listener in self.listeners:
            listener.callback_teamset()

    def __export__(self):
        return {
            'teams': [i.__export__() for i in reversed(self.teamset.children)],
        }


class TeamWidget(LoadableWidget, Synchronisable, BoxLayout):
    @classmethod
    def from_factory(cls, name="", logo="", teamcolor="#ffffff", sr="",
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
        self.manager.callback_teamset()

    def callback_event(self, event):
        if event == "name":
            # Necessary to update teamselect lists.
            self.manager.callback_teamset()

        for listener in self.listeners:
            listener.callback_event(event)

    def draw_name(self, target):
        with open(target, 'w') as f:
            f.write(self.name.text)

    def draw_logo(self, target):
        # Will copy missing.png as necessary.
        copyfile(self.logo.text, target)

    def draw_color(self, target):
        # We don't care if the colour is invalid, not our problem.
        with open(target, 'w') as f:
            f.write("<!DOCTYPE html>"
                    "<html>"
                    "<head>"
                    "    <meta http-equiv=\"refresh\" content=\"1\">"
                    "    <title>Solid Colour</title>"
                    "</head>"
                    "<body style=\"width:100%; height:100%; "
                    "background-color:{};\">"
                    "</body>"
                    "</html>".format(self.teamcolor.text))

    def draw_sr(self, target):
        sr = self.sr.text
        if not sr:
            sr = 0
            for child in self.rosterview.playerset.children:
                # Any invalid values are assumed to be 0 (empty also errors).
                with suppress(ValueError):
                    sr += int(child.sr.text)
            # Integer average; max(1, len) prevents zero division.
            sr //= max(1, len(self.rosterview.playerset.children))
        with open(target, 'w') as f:
            f.write(str(sr))  # Gotta write a string.

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
