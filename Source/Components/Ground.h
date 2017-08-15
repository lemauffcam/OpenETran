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
#define Y_OPEN	1e-009 /* Open Circuit admittance */
#define Y_CLOSE 1e+009 /* Short circuit admittance */

struct ground {
	/* Attributes for all grounds, and ground rods */
	double R60; /* power frequency resistance */
	double y60; /* admittance for R60 */
	double Ri;  /* impulse ground resistance at present time step */
	double Ig;  /* soil ionization current */
	double y;   /* admittance for the pole y matrix */
	double h;   /* past history current for built-in inductance */
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

	/* Counterpoise attributes and variables follow */
	int counterpoise; /* 1 if there's a counterpoise, 0 otherwise */
	double depthC; /* Depth in m. of counterpoise conductor */
	double radiusC; /* Radius in m. of counterpoise conductor */
	double lengthC; /* Total length in m. of counterpoise conductor */
	double li; /* Length of 1 segment of counterpoise conductor */
	int numSeg; /* Number of segments (RLC & G cells) in the counterpoise conductor */
	double relPerm; /* Relative electrical permittivity of soil */
	double e0; /* Critical field gradient (electric field intensity on the boundary of the soil ionized zone) */
	double rho; /* Resistivity of soil */
	/* solve a symmetric tridiagonal system of order numSeg+1 */
	gsl_vector *yDiag;   /* Diagonal elements */
	gsl_vector *yOff;    /* Off-Diagonal elements (will be constant) */
	gsl_vector *voltage; /* Voltage at each node */
	gsl_vector *current; /* Current at each node */
	double ri; /* series elements do not depend on current */
	double Li;
	gsl_vector *Ci; /* shunt elements in each segment depend on current */
	gsl_vector *Gi;
	gsl_vector *hRL; /* History current in series ri, Li */
	gsl_vector *hC;  /* History current in shunt Ci */
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

struct rs_params {
	double r60;
	double rp;
	int n;
};
double rs_function (double rs, void *params);


#endif
