/*
 * sql.h
 *
 *  Created on: 30 Oct 2014
 *      Author: oxis
 */

#ifndef SQL_H_
#define SQL_H_

using namespace std;

class Connector {
	MYSQL *connect; // Create a pointer to the MySQL instance
	struct CREDS {
		std::string host;
		std::string usr;
		std::string pwd;
		std::string base;
	} creds;
public:
	int connectDB();
	int disconnectDB();
	int getAllTasks();
	int markTaskAsRunning(std::string ligandId, std::string receptorId);
	int resetAllTaskRunningIds();
	int read_sql_config();
	//~Connector() {delete connect;};
};

struct jobstruct {
	const char* idreceptor;
	const char* namereceptor;
	const char* pdbreceptor;
	const char* confname;
	const char* pdbconf;
	const char* idligand;
	const char* nameligand;
	const char* pdbligand;
	const char* experiment;
};

#endif /* SQL_H_ */
