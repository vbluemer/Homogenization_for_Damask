# Users guide
In this document, explanation is given for the use of this code. The general section includes the grid and material properties that need to be supplied. In the other sections, the simulation types are elaborated.
## General
The `problem_definition.py` defines all the settings that can be changed. Some settings are or can be used for all the simulation types. These will be considered the general settings, these include the sections `general`, `yielding_condition` and `solver`.

Most of the settings defined in the `problem_definition.py` will be checked for validity and for missing values. If any errors are found in the `problem_definition.py`, this will be returned to the user.

Files can be specified relative to the problem_definition.yaml or with the full path (starting with `/`).


