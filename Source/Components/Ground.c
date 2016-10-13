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

/* This module contains the time-step loop and supporting functions for
LPDW's transient simulation engine, based on H. W. Dommel's IEEE papers.
Called from the driver and xfmr modules. */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <gsl/gsl_vector.h>
#include <gsl/gsl_matrix.h>
#include <gsl/gsl_blas.h>
#include <gsl/gsl_linalg.h>

#include "../OETypes.h"
#include "../Parser.h"
#include "../ReadUtils.h"
#include "Meter.h"
#include "../WritePlotFile.h"
#include "Pole.h"
#include "Ground.h"

/* Returns the shunt capa value in infinite medium
	ai : soil ionized zone radius
*/
double shuntCapa(struct ground *ptr, double ai);

/*	Update currents at each node for the new time step using previously calculated voltages
	Update the Ybus matrix with the new values of Ci & Gi calculated with the leakage current
*/
void updateModel(struct ground *ptr);

char ground_token[] = "ground";
struct ground *ground_head, *ground_ptr;

/* see if the ground resistance is reduced by impulse current flow */
void check_ground (struct ground *ptr) {
	double It, Vg, Vl, Imag, Vt;
	
	/* Voltage at node 1 */
	Vt = gsl_vector_get (ptr->parent->voltage, ptr->from) - gsl_vector_get (ptr->parent->voltage, ptr->to);

	It = Vt * ptr->y + ptr->i;  /* total ground current */
	ptr->amps = It;
	Imag = fabs (It);

	/* We start by solving for the voltages at each node */
	gsl_vector_set(ptr->current, 0, It);
	gsl_linalg_LU_solve(ptr->yTri, ptr->yPerm, ptr->current, ptr->voltage);

	/* We then update the currents and the Ybus matrix for the next time step */
	updateModel(ptr);
	
	Vg = gsl_vector_get(ptr->voltage, 0); /* Updated ground voltage */

/* inject this current into R60 to produce a back emf, so total ground voltage is Vg */
	ptr->i_bias = Vg * (1.0 / ptr->Ri - ptr->y60);
/* update past history of the built-in ground inductance */
	Vl = Vt - Vg;
	if (ptr->zl > 0.0) {
		ptr->h = It + Vl / ptr->zl;
	}
	ptr->i = ptr->h * ptr->yzl + ptr->i_bias * ptr->yr;

}

/* add ground bias current plus inductive past history current at the pole */

void inject_ground (struct ground *ptr) {
	gsl_vector *c;
	double val;
	
	c = ptr->parent->injection;
	val = ptr->i;
	*gsl_vector_ptr (c, ptr->from) -= val;
	*gsl_vector_ptr (c, ptr->to) += val;
}

int init_ground_list (void)
{
	if (((ground_head = (struct ground *) malloc (sizeof *ground_head)) != NULL)) {
		ground_head->next = NULL;
		ground_ptr = ground_head;
		return (0);
	}
	if (logfp) fprintf( logfp, "can't initialize ground list\n");
	oe_exit (ERR_MALLOC);
	return (1);
}

void do_all_grounds (void (*verb) (struct ground *))
{
	ground_ptr = ground_head;
	while (((ground_ptr = ground_ptr->next) != NULL)) {
		verb (ground_ptr);
	}
}

struct ground *find_ground (int at, int from, int to)
{
	ground_ptr = ground_head;
	while (((ground_ptr = ground_ptr->next) != NULL)) {
		if ((ground_ptr->parent->location == at) &&
			(ground_ptr->from == from) &&(ground_ptr->to == to)) return ground_ptr;
	}
	return NULL;
}

/* read ground data from file or buffer, set up structs */

int read_ground (void)
{
	int i, j, k;
	double R60, Rho, e0, L, length;
	double radius = 1, lengthC = 1, depth = 1, perm = 1; /* Counterpoise conductor parameters */
	int numberSegment;
	struct ground *ptr;
	int monitor;
	double *target;
	
	(void) next_double (&R60);
	if (R60 < 0.0) { /* input R60 < 0 means we want an ammeter */
		R60 *= -1.0;
		monitor = 1;
	} else {
		monitor = 0;
	}
	(void) next_double (&Rho);
	(void) next_double (&e0);
	(void) next_double (&L);
	(void) next_double (&length);

	(void)next_double(&radius);

	/* If radius is 0, then there's no counterpoise conductor */
	if (radius > 0.0) {
		(void) next_double (&lengthC);
		(void) next_double (&depth);
		(void) next_int (&numberSegment);
		(void) next_double (&perm);

		/* Must be >= 1, if there's an err the ground is considered to have no counterpoise */
		if (numberSegment < 1) {
			fprintf(logfp, "Err, the number of segments in the counterpoise can't be less than 1\n");
			radius = 0;
		}

	} else {
		lengthC = 0;
		depth = 0;
		numberSegment = 0;
	}

	L *= length;
	(void) read_pairs ();
	(void) read_poles ();
	(void) reset_assignments ();
	while (!next_assignment (&i, &j, &k)) {
		ptr = add_ground (i, j, k, R60, Rho, e0, L);
		add_counterpoise(ptr, radius, lengthC, depth, numberSegment, Rho, perm, e0);

		if (monitor) {
			target = &(ptr->amps);
			(void) add_ammeter (i, j, IPG_FLAG, target);
		}
	}
	return (0);
}

/* reset the ground history parameters */

void reset_ground (struct ground *ptr)
{
	ptr->h = 0.0;
	ptr->i = 0.0;
	ptr->i_bias = 0.0;
	ptr->amps = 0.0;
	ptr->Ri = ptr->R60; 
}

/* add a new ground struct to the linked list, called either by read_ground
or by read_customer */
	
struct ground *add_ground (int i, int j, int k, 
double R60, double Rho, double e0, double L)
{
	struct ground *ptr;

	if (((ptr = (struct ground *) malloc (sizeof *ptr)) != NULL)) {
		ptr->R60 = R60;
		ptr->y60 = 1.0 / R60;
		ptr->Ig = e0 * Rho / R60 / R60 / 6.283185;
		ptr->parent = find_pole (i);
		if (!ptr->parent) oe_exit (ERR_BAD_POLE);
		ptr->parent->solve = TRUE;
		ptr->zl = 2.0 * L / dT;
		ptr->y = 1.0 / (R60 + ptr->zl);
		ptr->yr = ptr->y * R60;
		ptr->yzl = ptr->y * ptr->zl;
		add_y (ptr->parent, j, k, ptr->y);
		ptr->from = j;
		ptr->to = k;
		ptr->next = NULL;
		reset_ground (ptr);
		ground_ptr->next = ptr;
		ground_ptr = ptr;
		return (ptr);
	} else {
		if (logfp) fprintf( logfp, "can't allocate new ground\n");
		oe_exit (ERR_MALLOC);
	}
	return (NULL);
} /* add_ground */

void add_counterpoise(struct ground *ptr, double a, double length, double h, int numSeg,
						double rho, double perm, double e0) {

	double li; /* Length of 1 segment of the counterpoise wire */
	int signum;
	double ri, Li, Ci, Gi, y; /* Counterpoise parameters and branch admittance */

	
	ptr->numSeg = numSeg;
	if (numSeg == 0) return;

	li = length / ((double)numSeg);
	ptr->depthC = h;
	ptr->radiusC = a;
	ptr->lengthC = length;
	ptr->rho = rho;
	ptr->relPerm = perm;
	ptr->e0 = e0;
	ptr->li = li;

	/* Allocations */
	ptr->Ybus = gsl_matrix_alloc(numSeg, numSeg);
	ptr->yTri = gsl_matrix_alloc(numSeg, numSeg);
	ptr->yPerm = gsl_permutation_alloc(numSeg);
	
	ptr->voltage = gsl_vector_calloc(numSeg);
	ptr->current = gsl_vector_calloc(numSeg);

	ptr->Ci = gsl_vector_alloc(numSeg);
	ptr->Gi = gsl_vector_alloc(numSeg);

	/* Resistance of 1 segment of the conductor, constant in the current model */
	ri = rho / (2 * M_PI * li) * ((2 * h + a) / li + log((li + sqrt(li * li + a * a)) / a)
		- sqrt(1 + pow(a / li, 2)) + log((li + sqrt(li * li + 4 * h * h)) / (2 * h)) - sqrt(1 + pow(2 * h / li, 2)));

	ptr->ri = ri;

	/* Inductance of 1 segment of the counterpoise, constant in the current model */
	Li = U0 * li / (2 * M_PI) * (log(2 * li / a) - 1);

	ptr->Li = Li;

	/* Capacitance & conductance (time dependant, initial value set for ionization radius equals conductor radius) */
	Ci = shuntCapa(ptr, a) + shuntCapa(ptr, 2 * h - a);
	Gi = Ci / (perm * EPS0 * rho);

	for (int i = 0; i < numSeg; i++) {
		gsl_vector_set(ptr->Ci, i, Ci);
		gsl_vector_set(ptr->Gi, i, Gi);
	}

	/* Fill out Ybus matrix */
	for (int i = 0; i < numSeg; i++) {
		for (int j = 0; j < numSeg; j++) {
			if (i == j) {
				y = 2 / (ri + 2 * Li / dT) + Gi + 2 * Ci / dT;
			
			} else if (abs(i - j) == 1) {
				y = -1 / (ri + 2 * Li / dT);
			
			} else {
				y = 0;
			}

			gsl_matrix_set(ptr->Ybus, i, j, y);
		}
	}

	/* First segment's admittance */
	y = 1 / (ri + 2 * Li / dT);
	gsl_matrix_set(ptr->Ybus, 0, 0, y);

	/* Last segment's admittance */
	y = 1 / (ri + 2 * Li / dT) + Gi + 2 * Ci / dT;
	gsl_matrix_set(ptr->Ybus, numSeg - 1, numSeg - 1, y);

	/* Admittance matrix triangularization */
	gsl_matrix_memcpy(ptr->yTri, ptr->Ybus);
	gsl_linalg_LU_decomp(ptr->yTri, ptr->yPerm, &signum);

	return;
} /* add_counterpoise */

static FILE *fp = NULL;  /* assumes just one active counterpoise in the model */

void updateModel(struct ground *ptr) {
	double ri = ptr->ri, Li = ptr->Li, li = ptr->li, perm = ptr->relPerm * EPS0;
	double Ci, Gi, i, dI, ai, y;
	int k, signum;

	if (ptr->numSeg < 1) return; /* there is no counterpoise here */

	/* We don't care about the current in the first segment since it's injected via the base of the tower */
	for (k = 1; k < ptr->numSeg - 1; k++) {
		Ci = gsl_vector_get(ptr->Ci, k);
		Gi = gsl_vector_get(ptr->Gi, k);

		i = -(gsl_vector_get(ptr->voltage, k) - gsl_vector_get(ptr->voltage, k - 1)) / (ri + 2 * Li / dT) +
			(2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k) +
			(gsl_vector_get(ptr->voltage, k) - gsl_vector_get(ptr->voltage, k + 1)) / (ri + 2 * Li / dT);

		i -= gsl_vector_get(ptr->current, k) - Gi * gsl_vector_get(ptr->voltage, k); // History current

		gsl_vector_set(ptr->current, k, i);

		/* Update the Ybus matrix */
		dI = (2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k);
		ai = ptr->radiusC + dI * ptr->rho / (2 * M_PI * ptr->e0 * li);

		Ci = shuntCapa(ptr, ai) + shuntCapa(ptr, 2 * ptr->depthC - ai);

		Gi = Ci / (perm * ptr->rho);

		y = 2 / (ri + 2 * Li / dT) + Gi + 2 * Ci / dT; /* New admittance value */
		gsl_matrix_set(ptr->Ybus, k, k, y);

		gsl_vector_set(ptr->Ci, k, Ci);
		gsl_vector_set(ptr->Gi, k, Gi);
	}

	/* Last node */
	Ci = gsl_vector_get(ptr->Ci, k);
	Gi = gsl_vector_get(ptr->Gi, k);

	i = -(gsl_vector_get(ptr->voltage, k) - gsl_vector_get(ptr->voltage, k - 1)) / (ri + 2 * Li / dT) +
		(2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k);
	
	i -= gsl_vector_get(ptr->current, k) - Gi * gsl_vector_get(ptr->voltage, k); // History current
	
	gsl_vector_set(ptr->current, k, i);

	/* Update the Ybus matrix */
	dI = (2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k);
	ai = ptr->radiusC + dI * ptr->rho / (2 * M_PI * ptr->e0 * li);

	Ci = shuntCapa(ptr, ai) + shuntCapa(ptr, 2 * ptr->depthC - ai);
	Gi = Ci / (ptr->relPerm * EPS0 * ptr->rho);

	y = 1 / (ri + 2 * Li / dT) + Gi + 2 * Ci / dT; /* New admittance value */
	gsl_matrix_set(ptr->Ybus, k, k, y);

	gsl_vector_set(ptr->Ci, k, Ci);
	gsl_vector_set(ptr->Gi, k, Gi);

	/* Triangularization of Ybus */
	gsl_matrix_memcpy(ptr->yTri, ptr->Ybus);
	gsl_linalg_LU_decomp(ptr->yTri, ptr->yPerm, &signum);

	/* temporary output logging */
	if (NULL == fp)	{
		fp = fopen ("cpground.csv", "w"); /* let fp close when the program exits */
		fprintf(fp, "t,");
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "I%d,", k);
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "V%d,", k);
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "R%d,", k); /* don't these ever change? */
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "L%d,", k);
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "C%d,", k);
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "G%d,", k);
		fprintf(fp,"\n");
	}
	if (NULL != fp)	{
		fprintf(fp, "%G,", t);
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "%G,", gsl_vector_get (ptr->current, k));
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "%G,", gsl_vector_get (ptr->voltage, k));
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "%G,", ptr->ri);
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "%G,", ptr->Li);
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "%G,", gsl_vector_get (ptr->Ci, k));
		for (k = 0; k < ptr->numSeg; k++) fprintf (fp, "%G,", gsl_vector_get (ptr->Gi, k));
		fprintf(fp,"\n");
	}

	return;
}

/* Returns value of shunt capacitance in an infinite medium.
	- ai : soil ionization radius
*/
double shuntCapa(struct ground *ptr, double ai) {
	double perm = ptr->relPerm * EPS0; /* Soil permittivity */
	double li = ptr->li;

	if (ai < 0.) {
		ai *= -1.;
	}

	double C = 2 * M_PI * perm  * li / ( ai / li + log( (li + sqrt(pow(li, 2) + pow(ai, 2))) / ai )
		- sqrt(1 + pow(ai / li, 2)) );

	return C;
}