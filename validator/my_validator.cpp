#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <math.h>
#include <fstream>
#include <sstream>
#include <iostream>
#include "boinc/sched_util.h"
#include "boinc/sched_msgs.h"
#include "sched/validator.h"
#include "boinc/validate_util.h"
#include "sched/validate_util2.h"
//#include "boinc/backend_lib.h"
//#include "boinc/error_numbers.h"
//#include "boinc/boinc_db.h"

using namespace std;

struct DATA {
	char* receptor;
	char* ligand;
	double seed;
	float score;
};

int init_result(RESULT & result, void*& data) {
	FILE* f;
	std::string line;
	int retval, n;
	DATA* dp = new DATA;

	OUTPUT_FILE_INFO fi;

	log_messages.printf(MSG_DEBUG, "Start\n");

	retval = get_output_file_path(result, fi.path);
	if (retval) {
		log_messages.printf(MSG_DEBUG, "Unable to open file\n");
		return retval;
	}

	f = fopen(fi.path.c_str(), "r");

	if (f == NULL) {
		log_messages.printf(MSG_DEBUG, "Open error\n");
		return -1;
	}
	log_messages.printf(MSG_DEBUG, "Check result\n");

	char buff[256];
	n = fscanf(f, "%s", buff);
	char * pch;
	pch = strtok(buff, " ,");
	if (pch != NULL) {
		dp->receptor = pch;
	} else {
		return -1;
	}
	pch = strtok(NULL, ",");
	if (pch != NULL) {
		dp->ligand = pch;
	} else {
		return -1;
	}
	pch = strtok(NULL, ",");
	if (pch != NULL) {
		dp->seed = strtod(pch, NULL);
	} else {
		return -1;
	}
	pch = strtok(NULL, ",");
	if (pch != NULL) {
		dp->score = atof(pch);
	} else {
		return -1;
	}

	log_messages.printf(MSG_DEBUG, "%s %s %f %f\n", dp->receptor, dp->ligand,
			dp->seed, dp->score);
	if (strlen(dp->ligand) < 4 || strlen(dp->receptor) < 4) {
		log_messages.printf(MSG_DEBUG, "%s %s Name failed\n", dp->receptor, dp->ligand);
		return -1;
	}

	if (dp->score > 50 || dp->score < -50) {
		log_messages.printf(MSG_DEBUG, "%f %f Score failed\n", dp->seed, dp->score);
		return -1;
	}

	return 0;
}

int compare_results(RESULT& r1, void* _data1, RESULT const& r2, void* _data2,
		bool& match) {
	return 0;
}

int cleanup_result(RESULT const& r, void* data) {
	if (data)
		delete (DATA*) data;
	return 0;
}
