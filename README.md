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

The program will generate images and text files in the `output` folder.

The `#` character in documentation filenames (below) is a placeholder and the
the program will replace it for an appropriate number. For example, `map#.png`
becomes `map1.png`, `map2.png`, and so on (for each map).


### Map Information

#### Output

The *Live Map Data* file contains information about the currently playing map.
It will be identical to the file for the relevant map.

| Parameter | Data File | Live Map Data | Notes |
| --------- | --------- | ------------- | ------------ |
| Game Mode / Map Pool Name | `map#pool.txt` | `livemappool.txt` | AX |
| Game Mode / Map Pool Image | `map#pool.png` | `livemappool.png` | AXY |
| Map Name  | `map#.txt` | `livemap.txt` | AX |
| Map Image | `map#.png` | `livemap.png` | AX |
| Team Score (For Map) | `map#score#.txt` | `livemapscore#.png` | A |
| Map Winner Team Name | `map#winnername.txt` | Does Not Exist | A |
| Map Winner Team Logo | `map#winnerlogo.png` | Does Not Exist | BY |
| Map Winner Team Colour | `map#winnercolor.html` | Does Not Exist | A |

Additional files are provided:

-   `matchtotalscore#.txt` holds the number of maps won for each team. (A)
-   `matchwinnername.txt` holds the name of the match-winning team. (B)
-   `matchwinnerlogo.png` holds the logo of the match-winning team. (BY)
-   `matchwinnercolor.html` holds the colour of the match-winning team. (A)
-   `liveposition#.png` holds the attack/defence position for each team. (CY)

Notes:
-   A) This file is always present.
-   B) This file only exists if a winner exists.
-   C) If no side is set to attack, this file will be removed.
-   X) Live map data is removed if there is no current map.
-   Y) If the source image is missing, this file will be removed (instead of a
    placeholder supplied).


#### Interface & Behaviour

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
