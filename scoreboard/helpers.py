from contextlib import suppress
import os
import re
import shutil
import unicodedata

from kivy.lang import Builder

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
    except FileNotFoundError:
        # Either delete the image or default to a "missing" image.
        if delete_if_missing:
            with suppress(FileNotFoundError):
                os.remove(dest)
        else:
            shutil.copyfile(IMAGEROOT + "/missing.png", dest)
