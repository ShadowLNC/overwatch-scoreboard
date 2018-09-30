from contextlib import suppress
import os
import re
import shutil
import unicodedata

from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from .constants import IMAGEROOT


# Load common widgets, this might be better in a common.py later.
Builder.load_file(os.path.dirname(os.path.abspath(__file__)) +
                  "/components/common.kv")


class LoadableWidget:
    @classmethod
    def from_factory(cls, parent=None, manager=None, **kwargs):
        self = cls(**kwargs)  # Allow passthrough of kwargs.

        # Render widget too while we're at it.
        if parent is not None:
            parent.add_widget(self)  # Sets self.parent in the process.
            if manager is None:
                manager = parent.root  # Only if defined in KVlang.
        self.manager = manager  # Can be None, but not if parent is defined.

        return self


class Synchronisable:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listeners = []

    def sync(self, listener):
        self.listeners.append(listener)

    def desync(self, listener):
        # Get the right-index of the object in case added multiple times.
        # This allows sync/desync to act as a stack, and maintain call order.
        with suppress(ValueError):
            rindex = -1 - list(reversed(self.listeners)).index(listener)
            self.listeners.pop(rindex)

    def callback_event(self, event):
        for listener in self.listeners:
            listener.callback_event(event)


def filename_fmt(val):
    val = unicodedata.normalize('NFD', val)  # Normalise, then strip others.
    val = str(bytes(val, encoding='ascii', errors='ignore'), encoding='ascii')
    val = val.lower()
    # Allow letters (including underscores), spaces, dots and hyphens (dashes).
    return re.sub(r"[^\w .-]", "", val, flags=re.ASCII)


def text_fmt(val):
    return str(val).upper()


def copyfile(src, dest, delete_if_missing=True):
    # Prevent crashes by outputting a fallback if we can't get the file.
    try:
        shutil.copyfile(src, dest)
    except (FileNotFoundError, PermissionError) as e:
        # Either delete the image or default to a "missing" image.
        Logger.warning("Helpers: " + str(e))
        if delete_if_missing:
            try:
                os.remove(dest)
            except PermissionError:
                Logger.error("Helpers: Could not remove " + str(dest))
            except FileNotFoundError:
                pass  # Can't use suppress(), must log PermissionError.
        else:
            try:
                shutil.copyfile(IMAGEROOT + "/missing.png", dest)
            except (FileNotFoundError, PermissionError) as e:
                try:
                    Logger.warning("Helpers: " + str(e))
                    open(dest, 'wb').close()  # Touch target for empty file.
                except PermissionError:
                    Logger.error("Helpers: Could not write " + str(dest))


class DeleteWidget(Button):
    def callback_press(self):
        DeleteConfirmation(self.callback_target).open()


class DeleteConfirmation(Popup):
    def __init__(self, target_callback, **kwargs):
        super().__init__(**kwargs)
        self.target_callback = target_callback
        self.live = False

    def callback_open(self):
        self.live = True

    def callback_delete(self):
        if self.live:
            self.live = False  # Suppress multi-click/multi-call.
            self.target_callback()  # Propagate.
            self.dismiss()
