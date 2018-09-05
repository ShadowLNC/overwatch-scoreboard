import os
import re

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from ..constants import OUTPUTROOT
# NOTE: helpers also loads a kv file for widgets used.
from ..helpers import LoadableWidget, filename_fmt, text_fmt


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/custom.kv")


class CustomDataManager(LoadableWidget, BoxLayout):
    @classmethod
    def from_factory(cls, entries=None, **kwargs):
        self = super().from_factory(**kwargs)

        if entries is None:
            # This means this is first-run and has not been used before.
            # Can't use blank list as that can be in saved state.
            entries = ["caster1.txt", "caster2.txt",
                       "analyst1.txt", "analyst2.txt", ]
            # Create "instances" (kwargs for constructor) for each file.
            # Leave the data undefined; it defaults anyway.
            entries = [{'file': i} for i in entries]

        for child in entries:
            self.add_entry(**child)
        self.clean()  # No point drawing here as child.draw() bypasses.

        return self

    @property
    def files(self):
        # Return list as we use "if a in files".
        return [child.file.text for child in self.entries.children]

    def add_entry(self, **data):
        # Instantiate from args - widget inherits LoadableWidget self-adding.
        CustomTextWidget.from_factory(**data,
                                      parent=self.entries, manager=self)

    def add_new(self):
        FilenameDialog(self).open()  # Popup asking for filename.

    def clean(self):
        files = self.files

        for f in os.listdir(OUTPUTROOT + "/custom"):
            if f not in files:
                os.remove(OUTPUTROOT + "/custom/" + f)

    def __export__(self):
        return {
            'entries': [i.__export__() for i in
                        reversed(self.entries.children)],
        }


class CustomTextWidget(LoadableWidget, BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Workaround for Kivy #3588 TextInput on_text fired on init.
        self.instantiation_complete = False

    @classmethod
    def from_factory(cls, file="", data="", **kwargs):
        self = super().from_factory(**kwargs)

        file = filename_fmt(file)
        if not file:
            # I know I'm bad at naming files, but really? No name at all?
            Logger.warning("Custom: Empty filename, defaulting.")
            file = "untitled.txt"  # Default

        # Workaround for Kivy #3588 TextInput on_text fired on init.
        self.instantiation_complete = True

        # Check for a duplicate filename and rename this one accordingly.
        # Basically Untitled.txt => Untitled_2.txt => Untitled_3.txt and so on.
        files = self.manager.files
        if file in files:
            # The filename is known, this is a problem.
            file = file.rsplit(".", 1)

            # Check if it has a number on the end or not, and prep new number.
            end = re.search(r"(?<=_)\d+$", file[0])
            if end:
                end = end.group()
                file[0] = file[0][:-len(end)]
                end = int(end)
            else:
                if not file[0].endswith("_"):
                    file[0] += "_"
                end = 1  # Increments to 2 immediately.

            while True:
                end += 1  # Increment the number until we get a free file.
                new = [file[0] + str(end)] + file[1:]
                new = ".".join(new)
                if new not in files:
                    break

            file = new

        self.file.text = file
        self.data.text = data  # Triggers draw by change (unless blank).
        self.draw()  # Force draw anyway, in case file out of sync.

        return self

    def callback_delete(self):
        manager = self.manager  # Retain reference.
        self.parent.remove_widget(self)
        manager.clean()  # Cleanup.

    def draw(self):
        if not self.instantiation_complete:
            # Workaround for Kivy #3588 TextInput on_text fired on init.
            return
        with open(OUTPUTROOT + "/custom/" + self.file.text, 'w') as f:
            f.write(text_fmt(self.data.text))

    def __export__(self):
        return {
            'file': self.file.text,
            'data': self.data.text,
        }


class FilenameDialog(Popup):
    def __init__(self, manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager

    def confirm(self):
        file = self.file.text  # Formatted as filename when added as widget.
        if file and "." not in file:
            file += ".txt"  # Extension, if filename defined.
        self.manager.add_entry(file=file)  # Filename will default if empty.
        self.dismiss()
