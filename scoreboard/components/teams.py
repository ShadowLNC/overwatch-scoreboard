import os

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup

# NOTE: helpers also loads a kv file for widgets used.
from .. import helpers


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/teams.kv")


class TeamManager(BoxLayout):
    def __init__(self, *args, teams=[], **kwargs):
        super().__init__(*args, **kwargs)

        def finish(dt):
            for team in teams:
                self.addteam(team)

        Clock.schedule_once(finish)

    def addteam(self, instance=None):
        # Add via dict args or precreated instance.
        if instance is None:
            instance = {}  # Allow NoneType to be instantiated below.
        if isinstance(instance, dict):
            instance = TeamWidget(**instance)  # Create from args.
        self.teamset.add_widget(instance)

    def __export__(self):
        return {
            'teams': [i.__export__() for i in reversed(self.teamset.children)],
        }


class TeamWidget(BoxLayout):
    def __init__(self, *args, name="", logo="", teamcolor="#000000", sr="",
                 roster=[], **kwargs):
        super().__init__(*args, **kwargs)

        def finish(dt):
            self.rosterview = RosterWidget(roster=roster)
            self.name.text = name
            self.logo.text = logo
            self.teamcolor.text = teamcolor
            self.sr.text = sr

        Clock.schedule_once(finish)

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


class RosterWidget(Popup):
    def __init__(self, *args, roster=[], **kwargs):
        super().__init__(*args, **kwargs)

        def finish(dt):
            for player in roster:
                self.addplayer(player)

        Clock.schedule_once(finish)

    def addplayer(self, instance=None):
        # Add via dict args or precreated instance.
        if instance is None:
            instance = {}  # Allow NoneType to be instantiated below.
        if isinstance(instance, dict):
            instance = PlayerWidget(**instance)  # Create from args.
        self.playerset.add_widget(instance)


class PlayerWidget(BoxLayout):
    def __init__(self, *args, username="", role="Flex", sr="", **kwargs):
        super().__init__(*args, **kwargs)

        def finish(dt):
            self.user.text = username
            self.role.text = role
            self.sr.text = sr

        Clock.schedule_once(finish)

    def callback_delete(self):
        self.parent.remove_widget(self)

    def __export__(self):
        return {
            'username': self.user.text,
            'role': self.role.text,
            'sr': self.sr.text,
        }
