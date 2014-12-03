/*
 * work_generator.h
 *
 *  Created on: 30 Oct 2014
 *      Author: oxis
 */

#ifndef WORK_GENERATOR_H_
#define WORK_GENERATOR_H_

#include <unistd.h>
#include <cstdlib>
#include <sstream>
#include <string.h>
#include <cstring>
#include <iostream>
#include <fstream>
#include <sys/stat.h>

//#include "boinc/boinc_db.h"
#include "boinc/error_numbers.h"
#include "boinc/backend_lib.h"
//#include "boinc/parse.h"
#include "boinc/util.h"
#include "boinc/svn_version.h"

//#include "boinc/sched_config.h"
#include "boinc/sched_util.h"
//#include "boinc/sched_msgs.h"
//#include "boinc/str_util.h"

using namespace std;

class Connector {
	MYSQL *connect; // Create a pointer to the MySQL instance
public:
	int connectDB();
	int disconnectDB();
	int getAllTasks();
	int markTaskAsRunning(std::string ligandId, std::string receptorId);
	int resetAllTaskRunningIds();
	//~Connector() {delete connect;};
};


#endif /* WORK_GENERATOR_H_ */
