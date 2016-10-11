/*
  Copyright (c) 1992, 1994, 1998, 2002, 2011, 2012,  
  Electric Power Research Institute, Inc.
  All rights reserved.
  
  This file is part of OpenETran.

  OpenETran is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, using only version 3 of the License.

  OpenETran is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with OpenETran.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef ground_included
#define ground_included

extern char ground_token[];

#define U0		1.256637061e-6 /* Free space magnetic permeability */
#define EPS0	8.8419412828e-12 /* Free space electric permittivity */
#define Y_OPEN  1.0e-9      /* admittance for an "open circuit" */

struct ground {
	double R60; /* power frequency resistance */
	double y60; /* admittance for R60 */
	double Ri;  /* impulse ground resistance at present time step */
	double Ig;  /* soil ionization current */
	double y;   /* admittance for the pole y matrix */
	double h;   /* past history current for built-in inductance */

	double depthC; /* Depth in m. of counterpoise conductor */
	double radiusC; /* Radius in m. of counterpoise conductor */
	double lengthC; /* Total length in m. of counterpoise conductor */
	double li; /* Length of 1 segment of counterpoise conductor */
	int numSeg; /* Number of segments (RLC & G cells) in the counterpoise conductor */
	double rho; /* Resistivity of soil */
	double relPerm; /* Relative electrical permittivity of soil */
	double e0; /* Critical field gradient (electric field intensity on the boundary of the soil ionized zone) */

	gsl_matrix *Ybus; /* Nodal admittance matrix */
	gsl_matrix *yTri; /* Triangularized Ybus */

	gsl_permutation *yPerm; /* Permutation matrix for LU decomposition */

	gsl_vector *voltage; /* Voltage at each node */
	gsl_vector *current; /* Current at each node */

	double ri;
	double Li;
	gsl_vector *Ci;
	gsl_vector *Gi;

	double i;   /* total ground injection current */
	double i_bias;  /* back-injection of current to simulate reduction from R60 to Ri */
	double amps; /* total current in the ground */
	double yr;  /* admittance adjustment factors for the series R60 + L */
	double zl;
	double yzl;
	int from;
	int to;
	struct pole *parent;
	struct ground *next;
};

extern struct ground *ground_head, *ground_ptr;

int init_ground_list (void);
void do_all_grounds (void (*verb) (struct ground *));
void check_ground (struct ground *ptr);
void inject_ground (struct ground *ptr);
void reset_ground (struct ground *ptr);
int read_ground (void);
struct ground *add_ground (int i, int j, int k, double R60, 
	double Rho, double e0, double L);

/* Adds counterpoise wire properties to the ground structure.
	Rho : soil resistivity
	Perm : soil relative permittivity
	e0 : Critical electrical gradient (at limit of ionized zone)
	numSeg : Number of segments in counterpoise conductor (see physical model)
*/
void add_counterpoise(struct ground *ptr, double radius, double length, double depth, int numSeg,
						double rho, double perm, double e0);

struct ground *find_ground (int at, int from, int to);

#endif
