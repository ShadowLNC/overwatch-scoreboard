import os
import re

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from ..constants import OUTPUTROOT
from ..helpers import filename_fmt, text_fmt


Builder.load_file(os.path.dirname(os.path.abspath(__file__)) + "/custom.kv")


class CustomDataManager(BoxLayout):
    def __init__(self, *args, entries=None, **kwargs):
        super().__init__(*args, **kwargs)

        if entries is None:
            # This means this is first-run and has not been used before.
            # Can't use blank list as that can be in saved state.
            entries = ["caster1.txt", "caster2.txt",
                       "analyst1.txt", "analyst2.txt", ]
            # Create "instances" (kwargs for constructor) for each file.
            # Leave the data undefined; it defaults anyway.
            entries = [{'file': i} for i in entries]

        def finish(dt):
            for child in entries:
                self.add_entry(child)
            self.clean()  # No point drawing here as child.draw() bypasses.

        Clock.schedule_once(finish)

    @property
    def files(self):
        # Return list as we use "if a in files".
        return [child.file.text for child in self.entries.children]

    def add_entry(self, instance=None):
        if instance is None:
            instance = {}  # Allow blank instantiation. (Not possible here.)
        if isinstance(instance, dict):
            instance = CustomTextWidget(**instance)  # From args.
        self.entries.add_widget(instance)

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


class CustomTextWidget(BoxLayout):
    def __init__(self, *args, file, data="", **kwargs):
        super().__init__(*args, **kwargs)

        # Workaround for Kivy #3588 TextInput on_text fired on init.
        self.instantiation_complete = False

        file = filename_fmt(file)
        if not file:
            # I know I'm bad at naming files, but really? No name at all?
            raise ValueError("Invalid filename.")

        def finish(dt):
            # WARNING: It is expected that this widget will immediately be
            # added to a CustomDataManager after instantiation. This scheduled
            # function to complete instantiation relies on that assumption.
            nonlocal file

            # Workaround for Kivy #3588 TextInput on_text fired on init.
            self.instantiation_complete = True

            files = self.manager.files
            if file in files:
                # The filename is known, this is a problem.
                file = file.rsplit(".", 1)

                # Check if it has a number on the end or not, and prep it.
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

        Clock.schedule_once(finish)

    @property
    def manager(self):
        return self.parent.root

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
        file = filename_fmt(self.file.text) or "untitled"  # Fallback if empty.
        file += ".txt"  # Extension.
        self.manager.add_entry({'file': file})
        self.dismiss()
