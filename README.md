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

The *Live Data File* contains the information about the currently playing map.
It will be identical to the file for the relevant map.

| Parameter | Filename | Live Data File |
| --------- | -------- | -------------- |
| Game Mode/Map Pool Image | `map#pool.png` | `livepool.png` |
| Game Mode/Map Pool Name | `map#pool.txt` | `livepool.txt` |
| Map Image | `map#.png` | `livemap.png` |
| Map Name  | `map#.txt` | `livemap.txt` |
| Team Score (For Map) | `map#score#.txt` | `livescore#.png` |
| Map Result | `map#result.txt` | `liveresult.png` |

Additionally, `livetotal#.txt` is provided for each team, and stores the number
of won maps.

#### Interface & Behaviour

-   The "Map Style" selector determines which kind of map images are output.

-   A map cannot be both current and final at the same time - enabling one will
cause the other to become disabled.

-   Setting any map's final state, adding a map, or deleting a map will cause
the first non-final map to be set as the current map. It is possible to have no
current map (you can disable the current switch on the current map).

-   If a map is not current, the map image will be desaturated (monochrome).
This is currently only possible for the "Strips" style.

-   If the source image cannot be found, the file will be removed from the
output folder, except for the map image, which will be set to an image icon to
indicate a missing source.

-   Similarly, if there is no currently playing map, all live data files will
be removed (with the exception of `livetotal#.txt`).

---
