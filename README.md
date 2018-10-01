# OVERWATCH SCOREBOARD

A simple but powerful tool for stream overlays when casting Overwatch matches!

**WARNING:** This software is in alpha and is under heavy development. Things
may break or change at any time, and without warning.

Original version: <https://github.com/mpfleming36/OW_Scoreboard_Tool/>

---

# Installation

1.  Install [Python 3](https://python.org/downloads/) (3.6.6 and 3.7.0 tested)

    **NOTE:** Make sure to tick the "Add Python to PATH" checkbox!

2.  Unzip the package

    **NOTE:** As the program is still under development, the images package is
    missing. You will need an `assets` folder with an appropriate directory
    structure.

3.  Double click `Overwatch Scoreboard.pyw` to run!

    **NOTE:** The first run may take some time to initialise.
    You will see dependencies being downloaded.

---

# Licence

This software is licenced under the GNU General Public License, version 3.

The images package is released separately, and is subject to a separate licence
(or copyright restrictions in your jurisdiction).

---

# Usage

The program will generate files in the `output` folder. Files can be expected
to be always available, except as specified.

The `#` character in documentation filenames (below) is a placeholder and the
the program will replace it for an appropriate number. For example, `map#.png`
becomes `map1.png`, `map2.png`, and so on (for each map).


### Team Information

#### Output

Team data is managed in the *Teams* tab.
Teams 1 and 2 are selected from the *Live* tab, as are heroes.

| Parameter | Data File | Notes |
| --------- | --------- | ----- |
| Team Name | `team#name.txt` | A |
| Team Logo | `team#logo.png` | AB |
| Team Colour | `team#color.html` | |
| Team SR | `team#sr.txt` | A |
| Player Username | `team#player#user.txt` | C |
| Player Role Image | `team#player#role.png` | CD |
| Player SR | `team#player#sr.txt` | C |
| Player Hero Image | `team#player#hero.png` | CD |

Additional files are provided:

-   `livetitle.txt` holds the value of the title field in the *Live* tab.

Notes:

-   A) This file only exists if a team has been selected.
-   B) This file only exists if the source image also exists (no placeholder).
-   C) This file only exists if the player slot is filled (a team must be selected).
-   D) This file will be removed if the value is empty.

#### Interface and Behaviour

-   If a team's SR is blank ("auto"), it is calculated from the SR entries of
    players listed in the team roster (all of them, not just the playing 6).

-   The "Hero Style" selector determines which kind of hero images are output.

-   The "Filter by Role" switch, when enabled, limits hero selections to the
    player's selected role (if "Flex" or no role is selected, no filter is
    applied). Existing selections are not altered when this switch is toggled.

-   A team should only be selected in one position at a time. Selecting the
    same team multiple times may have unintended consequences (the behaviour is
    undefined).

### Map Information

#### Output

The *Live Map Data* file contains information about the currently playing map.
It will be identical to the file for the relevant map.

| Parameter | Data File | Live Map Data | Notes |
| --------- | --------- | ------------- | ----- |
| Game Mode / Map Pool Name | `map#pool.txt` | `livemappool.txt` | A |
| Game Mode / Map Pool Image | `map#pool.png` | `livemappool.png` | AB |
| Map Name  | `map#.txt` | `livemap.txt` | A |
| Map Image | `map#.png` | `livemap.png` | A |
| Team Score (For Map) | `map#score#.txt` | `livemapscore#.png` | |
| Map Winner Team Name | `map#winnername.txt` | Does Not Exist | |
| Map Winner Team Logo | `map#winnerlogo.png` | Does Not Exist | BC |
| Map Winner Team Colour | `map#winnercolor.html` | Does Not Exist | ||

Additional files are provided:

-   `matchtotalscore#.txt` holds the number of maps won for each team.
-   `matchwinnername.txt` holds the name of the match-winning team. (C)
-   `matchwinnerlogo.png` holds the logo of the match-winning team. (BC)
-   `matchwinnercolor.html` holds the colour of the match-winning team.
-   `liveposition#.png` holds the attack/defence position for each team. (BD)

Notes:
-   A) Live map data is removed if there is no current map.
-   B) This file only exists if the source image also exists (no placeholder).
-   C) This file only exists if a winner exists.
-   D) If no side is set to attack, this file will be removed.


#### Interface and Behaviour

-   The "Map Style" selector determines which kind of map images are output.

-   Only one map may be current ("live") at any time. It cannot be final
    (complete). Enabling a conflicting switch causes the first to become
    disabled.

-   Setting any map's *final* state, or adding/deleting a map, will cause the
    first non-final map to be set as current automatically. You can set which
    map is current manually, including having no current map.

-   If a map is not current, the map image will be desaturated (monochrome).
    This is currently only possible for the "Strips" style.

> NOTE: We did not add winner details for the live map, as the map is no
> longer live once it has been won.

---
