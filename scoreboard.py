import kivy
import kivy.app

# from kivy.uix.button import Label
# from kivy.lang import Builder  # By default for Scoreboard(kivy.app.App)
# from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.window import Window

# view = Builder.load_file("main.kv")


# For all heroes, use sorted(sum(heroes.items())).
heroes = {
    'damage': [
        'Bastion',
        'Doomfist',
        'Genji',
        'Hanzo',
        'Junkrat',
        'McCree',
        'Mei',
        'Pharah',
        'Reaper',
        'Soldier: 76',
        'Sombra',
        'Symmetra',
        'Torbjörn',
        'Tracer',
        'Widowmaker',
    ],

    'tank': [
        'D.Va',
        'Orisa',
        'Reinhardt',
        'Roadhog',
        'Winston',
        'Wrecking Ball',
        'Zarya',
    ],

    'support': [
        'Ana',
        'Brigitte',
        'Lúcio',
        'Mercy',
        'Moira',
        'Zenyatta',
    ],
}


class Scoreboard(kivy.app.App):
    # def build(self):
    #     return Widget()  # Label(text="Hello, World!")

    pass


# TODO some modal confirmation... or none at all?
Window.bind(on_request_close=lambda *a, **kw: True)


# Possible settings to add in future:
# Auto update current map on/off
# Details of current game
# Liveupdate vs button
# Livesave vs button
# Lowercase/uppercase/titlecase/null transform on text
# Load custom saves/set custom savefile


if __name__ == '__main__':
    Scoreboard().run()
