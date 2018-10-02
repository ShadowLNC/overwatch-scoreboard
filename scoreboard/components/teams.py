from contextlib import suppress
import os
import re

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup

from ..constants import IMAGEROOT
# NOTE: helpers also loads a kv file for widgets used.
from ..helpers import LoadableWidget, Synchronisable, \
                      copyfile, filename_fmt, text_fmt


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/teams.kv")


class TeamManager(LoadableWidget, Synchronisable, BoxLayout):
    # callback_event handles "teamset" - teamset has changed, either deletion,
    # addition, or (later) reorder. This is just self.manager.livemanager but
    # we need to use Synchronisable since livemanager won't be instantiated
    # until after this object (the factory method indirectly fires the event).

    @classmethod
    def from_factory(cls, teams=[], **kwargs):
        self = super().from_factory(**kwargs)

        for team in teams:
            self.addteam(**team)

        return self

    def addteam(self, **data):
        # Instantiate from args - widget inherits LoadableWidget self-adding.
        # The team name change will fire callback_event teamset (plus it will
        # fire on the TextInput instantiation anyway, due to Kivy bug #3588).
        # Since we ignore empty team names anyway, we do not rely on the bug.
        TeamWidget.from_factory(**data, parent=self.teamset, manager=self)
        # No need to self.save() here as Kivy #3588 fires the TextInput change.

    def save(self):
        self.manager.save()

    def __export__(self):
        return {
            'teams': [i.__export__() for i in reversed(self.teamset.children)],
        }


class TeamWidget(LoadableWidget, Synchronisable, BoxLayout):
    @classmethod
    def from_factory(cls, name="", logo="", teamcolor="#000000ff", sr="",
                     roster=[], **kwargs):
        self = super().from_factory(**kwargs)

        self.rosterview = RosterWidget.from_factory(roster=roster,
                                                    parent=None, manager=self)
        self.name.text = name
        self.logo.text = logo
        self.teamcolor.text = teamcolor
        self.sr.text = sr

        return self

    @staticmethod
    def make_color(target, color=None):
        # We don't care if the colour is invalid, not our problem.
        with open(target, 'w') as f:
            f.write("<!DOCTYPE html>"
                    "<html>"
                    "<head>"
                    "<meta http-equiv=\"refresh\" content=\"1\">"
                    "<title>Solid Colour</title>"
                    "</head>")
            if color is not None:
                f.write("<body style=\"width:100%; height:100%; "
                        "background-color:{};\">"
                        "</body>".format(color))
            f.write("</html>")

    def callback_delete(self):
        self.parent.remove_widget(self)
        self.manager.save()
        self.manager.callback_event("teamset")

    def callback_event(self, event):
        super().callback_event(event)
        self.manager.save()  # callback_events are for modified properties.

        if event == "name":
            # Necessary to update teamselect lists.
            self.manager.callback_event("teamset")

    def callback_picklogo(self, file=None):
        if file is None:
            FileDialog.from_factory(start=self.logo.text,
                                    manager=self, parent=None).open()
        else:
            with suppress(ValueError):
                # ValueError when paths on different drives (Windows).
                # Use a relative path if the target is a descendant.
                if os.path.commonpath([file, os.getcwd()]):
                    file = os.path.relpath(file)
            self.logo.text = file

    def callback_pickcolor(self, color=None):
        if color is None:
            # This is to display the dialog.
            ColorDialog.from_factory(start=self.teamcolor.text,
                                     parent=None, manager=self).open()
        else:
            # Dialog has closed.
            self.teamcolor.text = color

    def draw_name(self, target):
        with open(target, 'w') as f:
            f.write(text_fmt(self.name.text))

    def draw_logo(self, target):
        copyfile(self.logo.text, target)  # Target deleted if logo missing.

    def draw_color(self, target):
        self.__class__.make_color(target, self.teamcolor.text)

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
            # text_fmt will cast to string and transform case but user should
            # only enter numbers, so there should be no case to transform.
            f.write(text_fmt(sr))

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
        self.manager.callback_event("roster")
        # No need for save() here as Kivy #3588 fires TextInput change.


class PlayerWidget(LoadableWidget, Synchronisable, BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Must define this first as Kivy #3588 triggers save indirectly.
        # If the property doesn't exist, save cannot proceed.
        self.hero = ""

    @classmethod
    def from_factory(cls, battletag="", role="Flex", sr="", hero="", **kwargs):
        self = super().from_factory(**kwargs)

        self.battletag.text = battletag
        self.role.text = role
        self.sr.text = sr
        # Hero is used for the live tab only, but is part of player data.
        self.hero = hero

        return self

    @staticmethod
    def make_hero(target, hero, style="Portraits"):
        hero = filename_fmt(hero)
        if hero:
            style = filename_fmt(style)
            infile = "{}/heroes/{}/{}.png".format(IMAGEROOT, style, hero)
            copyfile(infile, target, delete_if_missing=False)
        else:
            with suppress(FileNotFoundError):
                os.remove(target)

    @property
    def user(self):
        # Cut off the numeric part of the battletag.
        return self.battletag.text.rsplit("#", 1)[0]

    def callback_delete(self):
        self.parent.remove_widget(self)
        self.save()
        self.manager.manager.callback_event("roster")

    def callback_event(self, event):
        super().callback_event(event)
        self.save()  # callback_events are data changes.

        if event == "sr" and not self.manager.manager.sr.text:
            self.manager.manager.callback_event("sr")  # Recalc auto team SR.

    def draw_user(self, target, full=False):
        data = self.battletag.text
        if not full:
            data = self.user  # Numeric part removed.

        with open(target, 'w') as f:
            f.write(text_fmt(data))

    def draw_role(self, target):
        role = filename_fmt(self.role.text)
        if role:
            infile = "{}/game/roles/{}.png".format(IMAGEROOT, role)
            copyfile(infile, target, delete_if_missing=False)
        else:
            with suppress(FileNotFoundError):
                os.remove(target)

    def draw_sr(self, target):
        with open(target, 'w') as f:
            f.write(text_fmt(self.sr.text))

    def draw_hero(self, target, style="Portraits"):
        self.__class__.make_hero(target, self.hero, style)

    def save(self):
        # self > RosterWidget > TeamWidget > TeamManager.
        self.manager.manager.manager.save()

    def __export__(self):
        return {
            'battletag': self.battletag.text,
            'role': self.role.text,
            'sr': self.sr.text,
            'hero': self.hero,
        }


class FileDialog(LoadableWidget, Popup):
    @classmethod
    def from_factory(cls, start="", **kwargs):
        self = super().from_factory(**kwargs)
        if os.path.exists(start):
            # This still allows drive selection by entering "D:" etc.
            # Apparently a relative path breaks the FileChooser.
            self.picker.path = os.path.abspath(os.path.dirname(start))
        else:
            # cwd will usually be repository folder.
            self.picker.path = os.getcwd()
        return self

    def submit(self):
        if self.picker.selection:
            self.manager.callback_picklogo(self.picker.selection[0])
        self.dismiss()


class ColorDialog(LoadableWidget, Popup):
    # Basic Popup to choose colour and return it to the manager afterwards.
    @classmethod
    def from_factory(cls, start="", **kwargs):
        self = super().from_factory(**kwargs)
        if not re.match("^#*[a-fA-F0-9]{5,}$", start):
            # ColorPicker crashes if < 5 hex chars, so ensure valid value.
            start = "#000000ff"
        self.picker.hex_color = start
        return self

    def on_dismiss(self):
        self.manager.callback_pickcolor(self.picker.hex_color)
