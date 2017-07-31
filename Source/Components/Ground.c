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
#include <gsl/gsl_roots.h>

#include "../OETypes.h"
#include "../Parser.h"
#include "../ReadUtils.h"
#include "Meter.h"
#include "../WritePlotFile.h"
#include "Pole.h"
#include "Ground.h"

double rs_function (double rs, void *params)
{
	struct rs_params *p = (struct rs_params *) params;
	double ret;
	double rp = p->rp;
	int n = p->n;
	double r60 = p->r60;
	double a = rp / rs;
	double s = sqrt(1.0 + 4.0 * a);
	double pls = 1.0 + s;
	double mns = 1.0 - s;
	int i;
	double pls_n = 1.0;
	double mns_n = 1.0;
	for (i = 0; i < n; i++) {
		pls_n *= pls;
		mns_n *= mns;
	}
	pls_n *= pls_n; /* now pls^2n */
	mns_n *= mns_n;

	ret = 0.5 * rs * (pls_n * pls - mns_n * mns) / (pls_n - mns_n);

	return ret - r60;
}

double rdwight_cp (double len, double a, double h, double rho)
{
	double x = 0.5 * len;
	double s = 2.0 * h;
	double term1, term2, term3, term4;
	term1 = log (4.0 * x / a);
	term2 = log (4.0 * x / s);
	term3 = s / 2.0 / x;
	term4 = term3 * s / 8.0 / x;
	return (0.5 * rho / TWOPI / x) * (term1 + term2 + term3 + term4 - 2.0);
}

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
	
	/* Voltage at node 0 */
	Vt = gsl_vector_get (ptr->parent->voltage, ptr->from) - gsl_vector_get (ptr->parent->voltage, ptr->to);

	/* Total ground current */
	It = Vt * ptr->y + ptr->i;
	ptr->amps = It;
	Imag = fabs (It);

	/* Counterpoise model if there's a counterpoise at the base of each pole */
	if (ptr->counterpoise) {
		/* We start by solving for the voltages at each node */
		gsl_vector_set(ptr->current, 0, It);
		gsl_linalg_LU_solve(ptr->yTri, ptr->yPerm, ptr->current, ptr->voltage);

		/* We then update the currents and the Ybus matrix for the next time step */
		updateModel(ptr);

		/* Updated ground voltage */
		Vg = gsl_vector_get(ptr->voltage, 0);

		/* Current ground impulse resistance */
		if (Vg) {
			ptr->Yi = It / Vg;

			/* Bias current to add at node 0 so that Vg equals Vt */
			ptr->i_bias = (Vt - Vg) * ptr->Yi;

		} else {
			ptr->i_bias = 0;
		}
	
	} else {
		ptr->Ri = ptr->R60 / sqrt (1.0 + Imag / ptr->Ig); /* desired impulse resistance */
		Vg = It * ptr->Ri; /* ground voltage rise caused by Ri times It */
		/* inject this current into R60 to produce a back emf, so total ground voltage is Vg */
		ptr->i_bias = Vg * (1.0 / ptr->Ri - ptr->y60);
		printf("rod It, Ri, Vt, Vg, Ibias=%g %g %g %g %g\n", It, ptr->Ri, Vt, Vg, ptr->i_bias);
	}

	/* update past history of the built-in ground inductance */
	Vl = Vt - Vg;
	if (ptr->zl > 0.0) {
		ptr->h = It + Vl / ptr->zl;
	}

	ptr->i = ptr->h * ptr->yzl + ptr->i_bias * ptr->yr;
	printf("  check_ground Vl, h, i=%g %g %g\n", Vl, ptr->h, ptr->i);

	return;
} /* check_ground */

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
	double radius, lengthC, depth, perm; /* Counterpoise conductor parameters */
	int numberSegment;
	struct ground *ptr;
	int monitor;
	double *target;

	int counterpoise = 0;
	
	(void) next_double (&R60);
	if (!R60) oe_exit(ERR_R60_GROUND);

	if (R60 < 0.0) { /* input R60 < 0 means we want an ammeter */
		R60 *= -1.0;
		monitor = 1;
	} else {
		monitor = 0;
	}

	(void) next_double (&Rho);
	if (!Rho) oe_exit(ERR_RHO_GROUND);

	(void) next_double (&e0);
	(void) next_double (&L);
	(void) next_double (&length);

	/* The "next_double" function returns 1 if there's no data */
	if (!next_double(&radius)) {
		counterpoise = 1;

		if (next_double(&depth)) oe_exit(ERR_COUNTERPOISE);
		if (next_double(&lengthC)) oe_exit(ERR_COUNTERPOISE);
		if (next_int(&numberSegment)) oe_exit(ERR_COUNTERPOISE);
		if (next_double(&perm)) oe_exit(ERR_COUNTERPOISE);

		if (numberSegment < 1) oe_exit(ERR_NO_SEGMENT);
		if (radius <= 0) oe_exit(ERR_COUNT_RADIUS);
		if (depth <= 0) oe_exit(ERR_DEPTH);
	
	}

	L *= length;
	(void) read_pairs ();
	(void) read_poles ();
	(void) reset_assignments ();
	while (!next_assignment (&i, &j, &k)) {
		ptr = add_ground (i, j, k, R60, Rho, e0, L);

		if (counterpoise) {
			add_counterpoise(ptr, radius, lengthC, depth, numberSegment, Rho, perm, e0);
		}

		if (monitor) {
			target = &(ptr->amps);
			(void) add_ammeter (i, j, IPG_FLAG, target);
		}
	}
	return (0);
} /* read_ground */

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

		/* No counterpoise by default */
		ptr->counterpoise = 0;

		printf("AddGround y60,Ig,zl,y,yr,yzl=%g %g %g %g %g %g\n",
			   ptr->y60, ptr->Ig, ptr->zl, ptr->y, ptr->yr, ptr->yzl);

		return (ptr);
	} else {
		if (logfp) fprintf( logfp, "can't allocate new ground\n");
		oe_exit (ERR_MALLOC);
	}
	return (NULL);
} /* add_ground */

void add_counterpoise(struct ground *ptr, double a, double length, double h, int numSeg,
						double rho, double perm, double e0) {

	double li, Ri, Li, Ci, Gi, y, yfirst, ylast; /* Counterpoise parameters and branch admittance */
	int signum, i, j;
	/* root solver parameters */
	struct rs_params params;
	double r_lo, r_hi;
	double itertol = 1.0e-3;
	const gsl_root_fsolver_type *T;
	gsl_root_fsolver *s;
	gsl_function F;
	int status, iter=0, maxiter=100;
	
	ptr->numSeg = numSeg;
	ptr->counterpoise = 1;

	/* No counterpoise here */
	if (!numSeg) {
		return;
	}

	/* set up the GSL root finder */
	F.function = &rs_function;
	F.params = &params;
	T = gsl_root_fsolver_brent;
	s = gsl_root_fsolver_alloc (T);

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

	ptr->hist = gsl_vector_calloc(numSeg);

	/* Inductance of 1 segment of the counterpoise, constant in the current model */
	Li = U0 * li / (2 * M_PI) * (log(2 * li / a) - 1);

	ptr->Li = Li;

	/* Capacitance & conductance (time dependant, initial value set for ionization radius equals conductor radius) */
	Ci = shuntCapa(ptr, a) + shuntCapa(ptr, 2 * h - a);
	Gi = Ci / (perm * EPS0 * rho);

	for (i = 0; i < numSeg; i++) {
		gsl_vector_set(ptr->Ci, i, Ci);
		gsl_vector_set(ptr->Gi, i, Gi);
	}

	/* Resistance of 1 segment of the conductor, constant in the current model */
	/* - not using this from the paper; seems to be an error as the resistances are much too high 
	ri = rho / (2 * M_PI * li) * ((2 * h + a) / li + log((li + sqrt(li * li + a * a)) / a)
    	- sqrt(1 + pow(a / li, 2)) + log((li + sqrt(li * li + 4 * h * h)) / (2 * h)) - sqrt(1 + pow(2 * h / li, 2)));
    */
	r_lo = 1.0e-6;
	r_hi = 1.0e3;
	params.n = numSeg;
	params.rp = 1.0 / Gi;
	params.r60 = rdwight_cp (length, a, h, rho);
	gsl_root_fsolver_set (s, &F, r_lo, r_hi);
	do {
		++iter;
		status = gsl_root_fsolver_iterate (s);
		Ri = gsl_root_fsolver_root (s);
		r_lo = gsl_root_fsolver_x_lower (s);
		r_hi = gsl_root_fsolver_x_upper (s);
		status = gsl_root_test_interval (r_lo, r_hi, itertol, 0.0);
		if (status == GSL_SUCCESS) {
			ptr->ri = Ri;
		}
	} while (status == GSL_CONTINUE && iter < maxiter);

	printf("Cpoise: R60=%8.3f Li=%8.3g Ci=%8.3g Rp=%8.3f Ri=%8.3f\n", 
		   params.r60, Li, Ci, params.rp, Ri);

	/* Fill out Ybus matrix */
	for (i = 0; i < numSeg; i++) {
		for (j = 0; j < numSeg; j++) {
			if (i == j) {
				y = 2 / (Ri + 2 * Li / dT) + Gi + 2 * Ci / dT;
				printf("  setting y(%d,%d)=%g\n", i, j, y);
			} else if (abs(i - j) == 1) {
				y = -1 / (Ri + 2 * Li / dT);
				printf("  setting y(%d,%d)=%g\n", i, j, y);
			} else {
				y = 0;
			}

			gsl_matrix_set(ptr->Ybus, i, j, y);
		}
	}

	/* First segment's admittance */
	yfirst = 1 / (Ri + 2 * Li / dT);
	printf("  setting y(%d,%d)=%g\n", 0, 0, yfirst);
	gsl_matrix_set(ptr->Ybus, 0, 0, yfirst);

	/* Last segment's admittance */
	ylast = 1 / (Ri + 2 * Li / dT) + Gi + 2 * Ci / dT;
	printf("  setting y(%d,%d)=%g\n", numSeg-1, numSeg-1, ylast);
	gsl_matrix_set(ptr->Ybus, numSeg - 1, numSeg - 1, ylast);

	/* Admittance matrix triangularization */
	gsl_matrix_memcpy(ptr->yTri, ptr->Ybus);
	gsl_linalg_LU_decomp(ptr->yTri, ptr->yPerm, &signum);

	gsl_root_fsolver_free (s);

	printf("AddCP yfirst,ylast=%g %g\n", yfirst, ylast);

	return;
} /* add_counterpoise */

void updateModel(struct ground *ptr) {
	double ri = ptr->ri, Li = ptr->Li, li = ptr->li, perm = ptr->relPerm * EPS0;
	double Ci, Gi, i, dI, ai, y;
	int k, signum;

	/* There is no counterpoise here */
	if (!ptr->numSeg) {
		return;
	}

	/* We don't care about the current in the first segment since it's injected via the base of the tower */
	for (k = 1; k < ptr->numSeg - 1; k++) {
		Ci = gsl_vector_get(ptr->Ci, k);
		Gi = gsl_vector_get(ptr->Gi, k);

		i = -(gsl_vector_get(ptr->voltage, k) - gsl_vector_get(ptr->voltage, k - 1)) / (ri + 2 * Li / dT) +
			(2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k) +
			(gsl_vector_get(ptr->voltage, k) - gsl_vector_get(ptr->voltage, k + 1)) / (ri + 2 * Li / dT);

		/* History current */
		i -= gsl_vector_get(ptr->hist, k);

		gsl_vector_set(ptr->current, k, i);

		/* Update history current for next time step (will be changed again when Ci is updated) */
		i -= (2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k);

		/* Calculate new values of Ci & Gi using the leaked current */
		dI = (2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k);
		ai = ptr->radiusC + dI * ptr->rho / (2 * M_PI * ptr->e0 * li);
		/* ai = ptr->radiusC;  disabling */

		Ci = shuntCapa(ptr, ai) + shuntCapa(ptr, 2 * ptr->depthC - ai);
		Gi = Ci / (perm * ptr->rho);

		/* Update history current again with the new value of Ci (conservation of charge) */
		gsl_vector_set(ptr->hist, k, i + 2 * Ci * gsl_vector_get(ptr->voltage, k) / dT);

		/* New admittance value for the Ybus matrix */
		y = 2 / (ri + 2 * Li / dT) + Gi + 2 * Ci / dT;
		gsl_matrix_set(ptr->Ybus, k, k, y);

		gsl_vector_set(ptr->Ci, k, Ci);
		gsl_vector_set(ptr->Gi, k, Gi);
	}

	/* Last node */
	Ci = gsl_vector_get(ptr->Ci, k);
	Gi = gsl_vector_get(ptr->Gi, k);

	i = -(gsl_vector_get(ptr->voltage, k) - gsl_vector_get(ptr->voltage, k - 1)) / (ri + 2 * Li / dT) +
		(2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k);
	
	/* History current */
	i -= gsl_vector_get(ptr->hist, k);

	gsl_vector_set(ptr->current, k, i);

	/* Update history current for next time step (will be changed again when Ci is updated) */
	i -= (2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k);

	/* Calculate new values of Ci & Gi using the leaked current */
	dI = (2 * Ci / dT + Gi) * gsl_vector_get(ptr->voltage, k);
	ai = ptr->radiusC + dI * ptr->rho / (2 * M_PI * ptr->e0 * li);

	Ci = shuntCapa(ptr, ai) + shuntCapa(ptr, 2 * ptr->depthC - ai);
	Gi = Ci / (perm * ptr->rho);

//	printf("Cpoise update: i=%g dI=%g ai=%g Ci=%g Rp=%g\n", i, dI, ai, Ci, 1.0/Gi);

	/* Update history current again with the new value of Ci (conservation of charge) */
	gsl_vector_set(ptr->hist, k, i + 2 * Ci * gsl_vector_get(ptr->voltage, k) / dT);

	/* New admittance value for the Ybus matrix */
	y = 1 / (ri + 2 * Li / dT) + Gi + 2 * Ci / dT;
	gsl_matrix_set(ptr->Ybus, k, k, y);

	gsl_vector_set(ptr->Ci, k, Ci);
	gsl_vector_set(ptr->Gi, k, Gi);

	/* Triangularization of Ybus */
	gsl_matrix_memcpy(ptr->yTri, ptr->Ybus);
	gsl_linalg_LU_decomp(ptr->yTri, ptr->yPerm, &signum);

	return;
} /* updateModel */

/* Returns value of shunt capacitance in an infinite medium.
	- ai : soil ionization radius
*/
double shuntCapa(struct ground *ptr, double ai) {
	double perm = ptr->relPerm * EPS0; /* Soil permittivity */
	double li = ptr->li;

	if (ai < ptr->radiusC) {
		ai = ptr->radiusC;
	}

	double C = 2 * M_PI * perm  * li / ( ai / li + log( (li + sqrt(pow(li, 2) + pow(ai, 2))) / ai )
		- sqrt(1 + pow(ai / li, 2)) );

	return C;
}