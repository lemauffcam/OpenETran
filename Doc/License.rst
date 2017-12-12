Copyright and License 
=====================

*Copyright (c) 1992, 1994, 1998, 2002, 2011, 2012,*

*Electric Power Research Institute, Inc.*

*All rights reserved.*

GNU General Public License
--------------------------

*OpenETran is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.*

*OpenETran is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.*

*You should have received a copy of the GNU General Public License along
with OpenETran. If not, see <http://www.gnu.org/licenses/>.*

Historical Background
---------------------

During the period from 1990 through 2002, EPRI funded the development of
a Lightning Protection Design Workstation (LPDW), which was used by many
utilities to assess the lightning performance of distribution lines.
Since about 2002, this program has not been available. EPRI decided to
release the simulation kernel of LPDW under the name OpenETran, with an
open-source license (GPL v3), so it may be incorporated into IEEE Flash
and other projects.

OpenETran can presently simulate multi-conductor power lines,
insulators, surge arresters, non-linear grounds, and lightning strokes.
It efficiently calculates energy and charge duty on surge arresters, and
iterates to find the critical lightning current causing flashover on one
or more phases. It is also suitable for use in substation insulation
coordination. Capacitor switching, TRV, and other applications may be
added.

EPRI originally had permission to use code from the Numerical Recipes
book in LPDW. These routines have been removed in favor of the GNU
Scientific Library (GSL), which also uses the GPL v3 license. As a
result, the OpenETran package can be freely used and modified, but not
commercialized.

Acknowledgements
----------------

This work has been funded by the Electric Power Research Institute (EPRI) and members of CEATI’s Grounding
and Lightning Interest Group (GLIG).


