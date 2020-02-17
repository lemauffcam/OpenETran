/*
  Copyright (c) 1992, 1994, 1998, 2002, 2011, 2012, 
  Electric Power Research Institute, Inc.
  All rights reserved.
  
  This file is part of OpenETran.

  OpenETran is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  OpenETran is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with OpenETran.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "OETypes.h"

#ifdef linux
#define _strnicmp strncasecmp /* Fonction not defined in the standard library that needs a mapping on linux */
#endif

#ifdef __APPLE__
#define _strnicmp strncasecmp /* Fonction not defined in the standard library that needs a mapping on darwin */
#endif

#define STREAM_LEN 4096
#define INPUT_EXT  ".dat" /* Extension of the input file */
#define OUTPUT_EXT ".out" /* Extension of the output file */
#define MAXPATHLEN 1024 /* Max length of strings defined at compilation time */

FILE* logfp = NULL;  /* Pointer to log file */
long nr_iter = 0L;
int nr_max = 0;
FILE* op = NULL; /* Pointer to output file */
FILE* bp = NULL; /* Pointer to plot file */
int plot_type = PLT_NONE;

void usage()
{
	printf("usage (one-shot): openetran -plot [none|csv|tab|elt] filename.dat\n");
	printf("usage (iteration): openetran -icrit first_pole last_pole wire_flags ... filename.dat\n");
	exit(EXIT_FAILURE);
}

/* Reading command line arguments and calling the simulation transient module accordingly */
int main(int argc, char* argv[])
{
	LPLTINSTRUCT  lp_in; /* Pointer to a structure LTINSTRUCT containing the simulation options and pointers to the files */
	LPLTOUTSTRUCT lp_out; /* Pointer to a structure LTOUTSTRUCT containing the command line ouput values */
	FILE* fp; /* Pointer to input file */
	char basename[MAXPATHLEN]; /* Input file name without its extension */
	char inputname[MAXPATHLEN]; /* Input file name based on basename and the extension INPUT_EXT (".dat") */
	char outputname[MAXPATHLEN]; /* Output file name based on basename and the extension OUTPUT_EXT (".out") */
	char plotname[MAXPATHLEN]; /* Plot file name based on basename and the extension type given by the argument following "-plot"  [.csv|.tab|.elt] */
	char buf[MAXPATHLEN]; /* Buffer used to read the argument strings */
	char* pc; /* Pointer to the last character of last argument which value is '.' */
	int iteration_mode = ONE_SHOT; /* Simulation mode [ONE_SHOT|FIND_CRITICAL_CURRENT] */
	int stop_on_flashover = FALSE;
	int idx; /* Iterator used in "for" loops */

	logfp = fopen("openetran.log", "w");
	if (argc >= 4) { /* Extracting and analysing the command line arguments */
		strcpy(buf, argv[1]);
		if (_strnicmp(buf, "-p", 2) == 0) { /* single-shot run with plots */
			strcpy(buf, argv[2]);
			switch (tolower(buf[0])) {
			case 'c': plot_type = PLT_CSV; break;
			case 't': plot_type = PLT_TAB; break;
			case 'e': plot_type = PLT_ELT; break;
			default: plot_type = PLT_NONE; break;
			}
		}
		else if (_strnicmp(buf, "-i", 2) == 0) { /* critical current iterations */
			iteration_mode = FIND_CRITICAL_CURRENT;
			stop_on_flashover = TRUE;
		}
		else {
			usage();
		}
		(void)strcpy(buf, argv[argc - 1]); /* Last argument is the file name */
		pc = strrchr(buf, '.'); /* Pointer to the last character of string 'buf' which value is '.' */
		if (pc) {
			*pc = '\0'; /* Change this character by the string ending character '\0' */
		}
		strcpy(basename, buf);
	}
	else {
		usage();
	}

	/* Defining the name of the input file (this might only lead to problems because of implicit naming) */
	(void)strcpy(inputname, basename);
	(void)strcat(inputname, INPUT_EXT);

	/* Defining the name of the output file */
	(void)strcpy(outputname, basename);
	(void)strcat(outputname, OUTPUT_EXT);

	/* Defining the name of the file for plots */
	(void)strcpy(plotname, basename);
	switch (plot_type) {
	case PLT_CSV: (void)strcat(plotname, ".csv"); break;
	case PLT_TAB: (void)strcat(plotname, ".txt"); break;
	case PLT_ELT: (void)strcat(plotname, ".elt"); break;
	case PLT_MAT: plotname[0] = '\0'; break; /* Not implemented yet, hence empty string */
	case PLT_NONE: plotname[0] = '\0'; break;
	default: break;
	}

	/* Opening the input file if it exists */
	if (!(fp = fopen(inputname, "r"))) {
		printf("failed to open input file %s\n", inputname);
		exit(EXIT_FAILURE);
	}

	/* Opening the output file if it exists */
	if (!(op = fopen(outputname, "w"))) {
		printf("failed to open output file %s\n", outputname);
		exit(EXIT_FAILURE);
	}

	/* Opening the plot file if it's non empty and if it exists */
	if (plotname[0] != '\0') {
		if (!(bp = fopen(plotname, "wb"))) {
			printf("failed to open plot file %s\n", plotname);
			exit(EXIT_FAILURE);
		}
	}

	/* Allocating memory for the structure containing the simulation information */
	if ((lp_in = (LPLTINSTRUCT)malloc(sizeof * lp_in))) {
		lp_in->stop_on_flashover = stop_on_flashover;
		lp_in->iteration_mode = iteration_mode;
		lp_in->fp = fp;
		lp_in->bp = bp;
		lp_in->op = op;

		/* Initializing the extra data for the critical current simulation mode */
		if (iteration_mode == FIND_CRITICAL_CURRENT) {
			lp_in->first_pole_hit = atoi(argv[2]);
			lp_in->last_pole_hit = atoi(argv[3]);
			for (idx = 0; idx < MAX_WIRES_HIT; ++idx) {
				lp_in->wire_struck[idx] = 0;
			}
			for (idx = 4; idx < argc - 1; ++idx) {
				lp_in->wire_struck[idx - 4] = atoi(argv[idx]);
			}
		}
	}
	else {
		printf("failed to allocate input struct storage\n");
		exit(EXIT_FAILURE);
	}

	/* Allocating memory for the structure containing the command line output values */
	if (!(lp_out = (LPLTOUTSTRUCT)malloc(sizeof * lp_out))) {
		printf("failed to allocate output storage\n");
		exit(EXIT_FAILURE);
	}

	/* Launching the simulation */
	lt(lp_in, lp_out);

	/* Writing the output on the command line */
	if (iteration_mode == ONE_SHOT) {
		printf("\nOutput Values:\n");
		printf(" SI:      %4e\n", lp_out->SI);
		printf(" Energy:  %4e\n", lp_out->energy);
		printf(" current: %4e\n", lp_out->current);
		printf(" charge:  %4e\n", lp_out->charge);
		printf(" pipegap:  %4e\n", lp_out->predischarge);
	}
	else if (iteration_mode == FIND_CRITICAL_CURRENT) {
		printf("\nAverage Critical Currents, Poles %d to %d\n", lp_in->first_pole_hit, lp_in->last_pole_hit);
		for (idx = 0; idx < MAX_WIRES_HIT; ++idx) {
			if (lp_in->wire_struck[idx] > 0) {
				printf(" wire %2d: %4e\n", idx + 1, lp_out->icritical[idx]);
			}
		}
	}

	/* Closing the input file */
	if (fp) {
		fclose(fp);
	}

	/* Closing the plot file */
	if (bp) {
		fclose(bp);
	}

	/* Closing the output file */
	if (op && (op != stdout)) {
		fclose(op);
	}

	/* Closing the log file */
	if (logfp) {
		fclose(logfp);
	}

	/* Freing memory of the simulations pointers */
	free(lp_in);
	free(lp_out);

	/* Exiting without error */
	return 0;
}



static char *err_msg[] = {
	"No error",  // 0
	"Overlapping conductors", //	ERR_OVERLAP		1
	"Can't allocate memory", //	ERR_MALLOC 		2
	"No input available for lt simulation", //	ERR_BUFFER_MISSING      3
	"Initial DC voltage on inductor", //	ERR_LVDC		4
	"Can't read number of phases", //	ERR_PHASE_READ  	5
	"Bad number of phases", //	ERR_NPHASES		6
	"Bad number of poles", //	ERR_NPOLES 		7
	"Too many conductors", //	ERR_CABLE_PHASES	8
	"Bad conductor number", //	ERR_CONDUCTOR_N 	9
	"Missing a conductor", //	ERR_MISSING_CONDUCTOR   10
	"Bad conductor radius", //	ERR_RADIUS 		11
	"Bad conductor height", //	ERR_HEIGHT 		12
	"Unmatched pair input", //	ERR_UNMATCHED_PAIR      13
	"Bad pair number on component", //	ERR_BAD_PAIR    	14
	"Bad pole number on component", //	ERR_BAD_POLE    	15
	"Transient simulation stopped (convergence failure)", //	ERR_LT_STOPPED  	16
	"Arrester energy calculation stopped (convergence failure)", //	ERR_ARRTAU_STOPPED      17
	"Can't allocate memory in math library", //	ERR_MATH_ALLOC  	18
	"Calculation error in math library", //	ERR_MATH_CALC   	19
	"Subscript out of range", //	ERR_OUT_OF_RANGE   	20
	"No arrester discharge voltage defined", // ERR_BAD_ARR_VI      21
	"Mixed conductor and cable input for same span", // ERR_MIXED_LINES 22
	"Counterpoise radius must be strictly positive", // ERR_COUNT_RADIUS 23
	"Number of segments for the counterpoise must be >= 1", // ERR_NO_SEGMENT 24
	"Missing counterpoise parameter", // ERR_COUNTERPOISE 25
	"Counterpoise depth must be strictly positive", // ERR_DEPTH 26
	"Ground R60 resistance can't be 0", // ERR_R60_GROUND 27
	"Ground resistivity can't be 0" // ERR_RHO_GROUND 28
};

void oe_exit (int i)
{
	if (logfp) {
		fclose(logfp);
		logfp = NULL;
	}
	if (i) {
/*		MessageBox (NULL, err_msg[i], "OpenETran Error", MB_ICONEXCLAMATION); */
        fprintf (stderr, "OpenEtran Error: %s\n", err_msg[i]);
	}
	exit (i);
}
