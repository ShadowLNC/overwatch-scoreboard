IMAGEROOT = "assets"
OUTPUTROOT = "output"
SAVEFILE = "save.json"

# For all heroes, use sorted(sum(HEROES.values(), [])).
HEROES = {
    'Damage': [
        'Ashe',
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

    'Tank': [
        'D.Va',
        'Orisa',
        'Reinhardt',
        'Roadhog',
        'Winston',
        'Wrecking Ball',
        'Zarya',
    ],

    'Support': [
        'Ana',
        'Brigitte',
        'Lúcio',
        'Mercy',
        'Moira',
        'Zenyatta',
    ],
}

MAPS = {

    'extendedcontrol': [
        'Busan Downtown',
        'Busan Sanctuary',
        'Busan MEKA Base',
        'Ilios Lighthouse',
        'Ilios Ruins',
        'Ilios Well',
        'Lijiang Control Center',
        'Lijiang Garden',
        'Lijiang Night Market',
        'Nepal Sanctum',
        'Nepal Shrine',
        'Nepal Village',
        'Oasis City Center',
        'Oasis Gardens',
        'Oasis University',
    ],

    'Assault': [
        'Hanamura',
        'Horizon Lunar Colony',
        'Paris',
        'Temple of Anubis',
        'Volskaya Industries',
    ],

    'Escort': [
        'Dorado',
        'Junkertown',
        'Rialto',
        'Route 66',
        'Watchpoint: Gibraltar',
    ],

    'Hybrid': [
        'Blizzard World',
        'Eichenwalde',
        'Hollywood',
        'King\'s Row',
        'Numbani',
    ],

    'Control': [
        'Busan',
        'Ilios',
        'Lijiang Tower',
        'Nepal',
        'Oasis',
    ],

    'Capture the Flag': [
        # PLUS extendedcontrol
        'Ayutthaya',
    ],

    'Elimination': [
        # PLUS Capture the Flag
        'Black Forest',
        'Castillo',
        'Ecopoint: Antarctica',
        'Necropolis',
    ],

    'Deathmatch': [
        # PLUS extendedcontrol, Assault, Elimination* (*no subset items)
        'Dorado',
        'Eichenwalde',
        'Hollywood',
        'King\'s Row',

        'Château Guillard',
        'Petra',
    ],

}

# Subsets/copies.
MAPS['Capture the Flag'] += MAPS['extendedcontrol']
MAPS['Deathmatch'] += (
    MAPS['extendedcontrol'] + MAPS['Assault'] + MAPS['Elimination'])
MAPS['Team Deathmatch'] = MAPS['Deathmatch']
MAPS['Elimination'] += MAPS['Capture the Flag']  # Update after Deathmatch.

del MAPS['extendedcontrol']  # Must not appear in the dropdown.
for k, v in MAPS.items():
    MAPS[k] = [""] + sorted(v)  # Sort the lists, add blank option.
